import lldb
import os
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


# Inserts `__name__ = "__main__"` at the beginning of the file. However, if the
# script has any `from __future__ import X` lines, they MUST happen before any
# actual code, so we scan backwards and insert our hack right after the last
# such line.
def insert_module_name_hack(script_code):
  lines = script_code.splitlines()
  current_line = len(lines) - 1
  while current_line >= 0:
    if lines[current_line].lstrip().startswith("from __future__"):
      break
    current_line -= 1
  lines.insert(current_line + 1, '__name__ = "__main__"')
  return "\n".join(lines)


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

  def log_loaded_script(self, file_name, original_name):
    if DEBUG_ENABLED:
      self.total_scripts_run += 1
      if self.total_scripts_run % 1000 == 0:
        debug_print("loaded script = %s (%s), %d loaded so far" %
                    (file_name, original_name, self.total_scripts_run))

  def run_script_code(self, file_name, script_code):
    loaded_scripts.add(file_name)
    try:
      script_code = insert_module_name_hack(script_code)
      exec(script_code)
      self.log_loaded_script(file_name, "embedded")
    except Exception as e:
      # We don't want autoload to crash if an error happens. For example, some
      # scripts might be unavailable, but we still want to autoload scripts that
      # are actually there. So, in case of error, just log it and return.
      debug_print("Error trying to run embedded script '%s'" % file_name)
      debug_print(traceback.format_exc())

  def run_script_from_file(self, script_path):
    loaded_scripts.add(script_path)
    try:
      debugger = lldb.SBDebugger.FindDebuggerWithID(self.debugger_id)
      ci = debugger.GetCommandInterpreter()
      res = lldb.SBCommandReturnObject()
      # HACK: When gdb autoloads scripts, __name__ is equal to "__main__". We
      # want to replicate this behavior, but I've only been able to make
      # prettyprinter scripts work reliably by using `command script import` in
      # lldb (as opposed to, for example, `exec`ing them directly from here).
      # So we copy the script code to a temporary file for lldb to run, and
      # insert at the beginning a `__name__ = "__main__"` assignment.
      script_code = insert_module_name_hack(
          open(os.path.join(self.script_base_path, script_path), "r").read())
      # In some platforms tmp.name can't be used to open the temporary file
      # unless the NamedTemporaryFile object has been `close`d. So we pass
      # `delete=False`, close it, run it, and delete it manually.
      tmp = tempfile.NamedTemporaryFile(suffix=".py", delete=False)
      tmp_file_name = tmp.name
      tmp.write(script_code.encode("utf-8"))
      tmp.close()
      ci.HandleCommand("command script import " + tmp_file_name, res)
      self.log_loaded_script(tmp_file_name, script_path)
      if not KEEP_TEMP_FILES:
        os.remove(tmp_file_name)
    except Exception as e:
      # We don't want autoload to crash if an error happens. For example, some
      # scripts might be unavailable, but we still want to autoload scripts that
      # are actually there. So, in case of error, just log it and return.
      debug_print("Error trying to run script at '%s'" % script_path)
      debug_print(traceback.format_exc())

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
