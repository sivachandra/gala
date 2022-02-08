import lldb
import os
import tempfile
from threading import Thread

# If true, log some info to stdout.
DEBUG_ENABLED = False

# Types of .debug_gdb_scripts entries.
SECTION_SCRIPT_ID_PYTHON_FILE = 1
SECTION_SCRIPT_ID_SCHEME_FILE = 3
SECTION_SCRIPT_ID_PYTHON_TEXT = 4
SECTION_SCRIPT_ID_SCHEME_TEXT = 6

# gdb uses the script name to avoid running the same script twice. This set
# allows us to do the same.
loaded_scripts = set()


def debug_print(*args, **kwargs):
  if DEBUG_ENABLED:
    print(*args, **kwargs)


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


class LLDBListenerThread(Thread):

  def __init__(self, debugger):
    Thread.__init__(self)
    # The object backing `lldb.debugger` is, at the time of this writing, placed
    # in the stack. If we share it directly with the thread we can run into a
    # race condition where the debugger in the stack is destroyed by the time
    # the thread runs. As a workaround, we save its ID and we later use
    # `SBDebugger.FindDebuggerWithID` to create a properly managed object.
    self.debugger_id = debugger.GetID()
    self.target = debugger.GetSelectedTarget()
    self.listener = lldb.SBListener(".debug_gdb_script autoloader")
    self.target.GetBroadcaster().AddListener(
        self.listener, lldb.SBTarget.eBroadcastBitModulesLoaded)

  def run_script_from_file(self, script_path):
    loaded_scripts.add(script_path)
    debugger = lldb.SBDebugger.FindDebuggerWithID(self.debugger_id)
    ci = debugger.GetCommandInterpreter()
    res = lldb.SBCommandReturnObject()
    # HACK: When gdb autoloads scripts, __name__ is equal to "__main__". We
    # want to replicate this behavior, but I've only been able to make
    # prettyprinter scripts work reliably by using `command script import` in
    # lldb (as opposed to, for example, `exec`ing them directly from here).
    # So we copy the script code to a temporary file for lldb to run, and
    # insert at the beginning a `__name__ = "__main__"` assignment.
    script_code = insert_module_name_hack(open(script_path, "r").read())
    # In some platforms tmp.name can't be used to open the temporary file
    # unless the NamedTemporaryFile object has been `close`d. So we pass
    # `delete=False`, close it, run it, and delete it manually.
    tmp = tempfile.NamedTemporaryFile(suffix=".py", delete=False)
    script_name = tmp.name
    tmp.write(script_code.encode("utf-8"))
    tmp.close()
    debug_print("script =", script_path, " tempfile =", script_name)
    ci.HandleCommand("command script import " + script_name, res)
    if not DEBUG_ENABLED:  # Keep the file around if debugging.
      os.remove(script_name)

  def process_scripts_section(self, section):
    size = section.GetFileByteSize()
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
      # TODO: Support other kinds of entries.

  def run(self):
    while True:
      event = lldb.SBEvent()
      if self.listener.WaitForEvent(1, event):
        num_modules = self.target.GetNumModulesFromEvent(event)
        for i in range(num_modules):
          module = self.target.GetModuleAtIndexFromEvent(i, event)
          section = module.FindSection(".debug_gdb_scripts")
          if section.IsValid():
            self.process_scripts_section(section)


def __lldb_init_module(debugger, internal_dict):
  thread = LLDBListenerThread(debugger)
  thread.start()
