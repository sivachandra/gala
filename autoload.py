import lldb
import os
import re
import runpy
import sys
import tempfile
import time
import traceback
from threading import Thread
from typing import Callable, Dict, List, Optional

# If true, log some info to stdout.
DEBUG_ENABLED = False

# Types of .debug_gdb_scripts entries.
SECTION_SCRIPT_ID_PYTHON_FILE = 1
SECTION_SCRIPT_ID_SCHEME_FILE = 3
SECTION_SCRIPT_ID_PYTHON_TEXT = 4
SECTION_SCRIPT_ID_SCHEME_TEXT = 6

SCRIPT_TYPE_GDB = "gdb"
SCRIPT_TYPE_LLDB = "lldb"

# gdb uses the script name to avoid running the same script twice. This set
# allows us to do the same.
loaded_scripts = set()
# Sometimes lldb will give us the same module in multiple events. We use this
# set to deduplicate them.
modules_processed = set()
modules_loaded_callbacks = []

def debug_print(*args, **kwargs) -> None:
  if DEBUG_ENABLED:
    print("[%f]" % time.time(), *args, **kwargs)


def register_modules_loaded_callback(
    callback: Callable[[lldb.SBEvent], None]) -> None:
  """Registers a function to be called when lldb loads a new module.

  lldb currently doesn't allow multiple listeners for the same event. GALA's
  autoload script listens for the "modules loaded" event, so we provide a
  callback facility so that other scripts can also respond to module loads.

  Args:
    callback: a function that takes a lldb.SBEvent object.
  """
  modules_loaded_callbacks.append(callback)


class LLDBListenerThread(Thread):

  def __init__(self, debugger: lldb.SBDebugger, script_base_dir: str,
               excluded_patterns: List[re.Pattern]):
    Thread.__init__(self)
    # The object backing `lldb.debugger` is, at the time of this writing, placed
    # in the stack. If we share it directly with the thread we can run into a
    # race condition where the debugger in the stack is destroyed by the time
    # the thread runs. As a workaround, we save its ID and we later use
    # `SBDebugger.FindDebuggerWithID` to create a properly managed object.
    self.debugger_id = debugger.GetID()
    self.listener = lldb.SBListener(".debug_gdb_script autoloader")
    self.listener.StartListeningForEventClass(
        debugger, lldb.SBTarget.GetBroadcasterClassName(),
        lldb.SBTarget.eBroadcastBitModulesLoaded)
    self.script_base_dir = script_base_dir
    self.excluded_patterns = excluded_patterns

    self.total_scripts_run = 0  # For debug logging.

  def matches_exclusion_list(self, script_path: str) -> bool:
    debug_print("checking '%s' against exclusion list" % script_path)
    for p in self.excluded_patterns:
      if p.match(script_path):
        debug_print(
            "'%s' was excluded by pattern '%s'" % (script_path, p.pattern))
        return True
    return False

  def log_loaded_script(self, path: str, resolved_path: str) -> None:
    # `path` is the path as found in `.debug_gdb_scripts`.
    # `resolved_path` is the final path the file was loaded from.
    if DEBUG_ENABLED:
      self.total_scripts_run += 1
      debug_print("loaded script = %s (%s), %d loaded so far" %
                  (path, resolved_path, self.total_scripts_run))

  def run_script_code(self, file_name: str, script_code: str) -> None:
    loaded_scripts.add(file_name)
    try:
      exec(script_code, {__name__: "__main__", __file__: file_name})
      self.log_loaded_script(file_name, "embedded")
    except Exception as e:
      # We don't want autoload to crash if an error happens. For example, some
      # scripts might be unavailable, but we still want to autoload scripts that
      # are actually there. So, in case of error, just log it and return.
      print("Error trying to run embedded script '%s'" % file_name,
            file=sys.stderr)
      print(traceback.format_exc(), file=sys.stderr)

  def run_script_from_file(self, script_path: str, script_type: str) -> None:
    loaded_scripts.add(script_path)
    try:
      # Make script_path absolute.
      full_path = os.path.join(self.script_base_dir, script_path)
      if script_type == SCRIPT_TYPE_GDB:
        runpy.run_path(full_path, run_name="__main__")
      elif script_type == SCRIPT_TYPE_LLDB:
        debugger = lldb.SBDebugger.FindDebuggerWithID(self.debugger_id)
        debugger.HandleCommand("command script import %s" % full_path)
      else:
        raise RuntimeError("Invalid script type '%s'" % script_type)
      self.log_loaded_script(script_path, full_path)
    except Exception as e:
      # We don't want autoload to crash if an error happens. For example, some
      # scripts might be unavailable, but we still want to autoload scripts that
      # are actually there. So, in case of error, just log it and return.
      print("Error trying to run script at '%s'" % script_path, file=sys.stderr)
      print(traceback.format_exc(), file=sys.stderr)

  def process_gdb_scripts_section(self, section: lldb.SBSection) -> None:
    data = section.GetSectionData()
    size = data.GetByteSize()
    debug_print("reading .debug_gdb_scripts section with size %d" % size)
    error = lldb.SBError()
    current_offset = 0
    while current_offset < size:
      entry_type = data.GetUnsignedInt8(error, current_offset)
      entry_string = data.GetString(error, current_offset + 1)
      # skip the whole entry: type (1 byte) + string + null terminator (1 byte).
      current_offset += len(entry_string) + 2
      if (entry_type == SECTION_SCRIPT_ID_PYTHON_FILE and
          entry_string not in loaded_scripts and
          not self.matches_exclusion_list(entry_string)):
        self.run_script_from_file(entry_string, SCRIPT_TYPE_GDB)
      elif entry_type == SECTION_SCRIPT_ID_PYTHON_TEXT:
        newline_index = entry_string.find('\n')
        file_name = entry_string[:newline_index]
        if (file_name not in loaded_scripts and
            not self.matches_exclusion_list(file_name)):
          script_code = entry_string[newline_index + 1:]
          self.run_script_code(file_name, script_code)
    debug_print("finished processing .debug_gdb_scripts_section")

  def process_gala_lldb_scripts_section(self, section: lldb.SBSection) -> None:
    data = section.GetSectionData()
    size = data.GetByteSize()
    debug_print("reading .debug_gala_scripts section with size %d" % size)
    error = lldb.SBError()
    current_offset = 0
    while current_offset < size:
      entry_type = data.GetUnsignedInt8(error, current_offset)
      entry_string = data.GetString(error, current_offset + 1)
      # skip the whole entry: type (1 byte) + string + null terminator (1 byte).
      current_offset += len(entry_string) + 2
      if (entry_type == SECTION_SCRIPT_ID_PYTHON_FILE and
          entry_string not in loaded_scripts and
          not self.matches_exclusion_list(entry_string)):
        self.run_script_from_file(entry_string, SCRIPT_TYPE_LLDB)
    debug_print("finished processing .debug_gala_lldb_scripts_section")

  def run(self) -> None:
    while True:
      event = lldb.SBEvent()
      if self.listener.WaitForEvent(1, event):
        num_modules = lldb.SBTarget.GetNumModulesFromEvent(event)
        debug_print("%d modules loaded" % num_modules)
        for i in range(num_modules):
          module = lldb.SBTarget.GetModuleAtIndexFromEvent(i, event)
          if str(module) in modules_processed:
            debug_print("duplicate module %s" % module)
            continue
          modules_processed.add(str(module))
          section = module.FindSection(".debug_gdb_scripts")
          if section.IsValid():
            self.process_gdb_scripts_section(section)
          # lldb doesn't have yet an equivalent to .debug_gdb_scripts on Linux.
          # As a temporary solution, we autoload .debug_gala_lldb_scripts as
          # well, so users migrating to lldb can start writing lldb scripts too
          # without losing the autoloading functionality.
          section = module.FindSection(".debug_gala_lldb_scripts")
          if section.IsValid():
            self.process_gala_lldb_scripts_section(section)
        for callback in modules_loaded_callbacks:
          callback(event)


def initialize(debugger: lldb.SBDebugger,
               script_base_dir: str,
               excluded_paths: Optional[List[str]] = None) -> None:
  """Initializes autoloading of .debug_gdb_scripts entries.

  Args:
    - debugger: The debugger object passed from __lldb_init_module.
    - script_base_dir: the base directory that will be used for relative paths
      in .debug_gdb_scripts entries.
    - excluded_paths: a list of path regular expression strings that should be
      ignored by autoload. If a .debug_gdb_scripts or .debug_lldb_scripts entry
      matches any of them, it won't be loaded.
  """
  excluded_paths = excluded_paths or []
  excluded_patterns = [re.compile(p) for p in excluded_paths]
  thread = LLDBListenerThread(debugger, script_base_dir, excluded_patterns)
  thread.start()


def __lldb_init_module(debugger: lldb.SBDebugger, internal_dict: Dict) -> None:
  initialize(debugger, os.getcwd())
