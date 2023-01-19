import lldb
import os
import runpy
import sys
import tempfile
import time
import traceback
from threading import Thread

# If true, log some info to stdout.
DEBUG_ENABLED = False
KEEP_TEMP_FILES = False

# Types of .debug_gdb_scripts entries.
SECTION_SCRIPT_ID_PYTHON_FILE = 1
SECTION_SCRIPT_ID_SCHEME_FILE = 3
SECTION_SCRIPT_ID_PYTHON_TEXT = 4
SECTION_SCRIPT_ID_SCHEME_TEXT = 6

# gdb uses the script name to avoid running the same script twice. This set
# allows us to do the same.
loaded_scripts = set()
# Sometimes lldb will give us the same module in multiple events. We use this
# set to deduplicate them.
modules_processed = set()
modules_loaded_callbacks = []

def debug_print(*args, **kwargs):
  if DEBUG_ENABLED:
    print("[%f]" % time.time(), *args, **kwargs)


def register_modules_loaded_callback(callback):
  """Registers a function to be called when lldb loads a new module.

  lldb currently doesn't allow multiple listeners for the same event. GALA's
  autoload script listens for the "modules loaded" event, so we provide a
  callback facility so that other scripts can also respond to module loads.

  Args:
    callback: a function that takes a lldb.SBEvent object.
  """
  modules_loaded_callbacks.append(callback)


class LLDBListenerThread(Thread):

  def __init__(self, debugger, script_base_dir):
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

    self.total_scripts_run = 0  # For debug logging.

  def log_loaded_script(self, path, resolved_path):
    # `path` is the path as found in `.debug_gdb_scripts`.
    # `resolved_path` is the final path the file was loaded from.
    if DEBUG_ENABLED:
      self.total_scripts_run += 1
      debug_print("loaded script = %s (%s), %d loaded so far" %
                  (path, resolved_path, self.total_scripts_run))

  def run_script_code(self, file_name, script_code):
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

  def run_script_from_file(self, script_path):
    loaded_scripts.add(script_path)
    try:
      # Make script_path absolute.
      full_path = os.path.join(self.script_base_dir, script_path)
      runpy.run_path(full_path, run_name="__main__")
      self.log_loaded_script(script_path, full_path)
    except Exception as e:
      # We don't want autoload to crash if an error happens. For example, some
      # scripts might be unavailable, but we still want to autoload scripts that
      # are actually there. So, in case of error, just log it and return.
      print("Error trying to run script at '%s'" % script_path, file=sys.stderr)
      print(traceback.format_exc(), file=sys.stderr)

  def process_scripts_section(self, section):
    size = section.GetFileByteSize()
    debug_print("reading .debug_gdb_scripts section with size %d" % size)
    data = section.GetSectionData(0, size)
    error = lldb.SBError()
    current_offset = 0
    while current_offset < size:
      entry_type = data.GetUnsignedInt8(error, current_offset)
      entry_string = data.GetString(error, current_offset + 1)
      # skip the whole entry: type (1 byte) + string + null terminator (1 byte).
      current_offset += len(entry_string) + 2
      if (entry_type == SECTION_SCRIPT_ID_PYTHON_FILE and
          entry_string not in loaded_scripts):
        self.run_script_from_file(entry_string)
      elif entry_type == SECTION_SCRIPT_ID_PYTHON_TEXT:
        newline_index = entry_string.find('\n')
        file_name = entry_string[:newline_index]
        if file_name not in loaded_scripts:
          script_code = entry_string[newline_index + 1:]
          self.run_script_code(file_name, script_code)
    debug_print("finished processing .debug_gdb_scripts_section")

  def run(self):
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
            self.process_scripts_section(section)
        for callback in modules_loaded_callbacks:
          callback(event)


def initialize(debugger, script_base_dir):
  """Initializes autoloading of .debug_gdb_scripts entries.

  Args:
    - debugger: The debugger object passed from __lldb_init_module.
    - script_base_dir: the base directory that will be used for relative paths
      in .debug_gdb_scripts entries.
  """
  thread = LLDBListenerThread(debugger, script_base_dir)
  thread.start()


def __lldb_init_module(debugger, internal_dict):
  initialize(debugger, os.getcwd())
