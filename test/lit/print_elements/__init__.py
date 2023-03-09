from __future__ import print_function

import gdb
import gdb.printing
import sys


class TestStructPrinter:
  """Reads the size member and emits as many synthetic children.

  This gives us an easy way to test `set print elements`.
  """

  def __init__(self, val):
    self.val = val

  def display_hint(self):
    return "array"

  def to_string(self):
    return "A TestStruct of size %d" % self.val["size"]

  def children(self):
    size = int(self.val["size"])
    i = 0
    while i < size:
      print("yielding child %d" % i, file=sys.stderr)
      yield "[%d]"%i, i
      i += 1

def __lldb_init_module(debugger, internal_dict):
  printer = gdb.printing.RegexpCollectionPrettyPrinter("test_struct_printer")
  printer.add_printer("TestStruct", "TestStruct", TestStructPrinter)
  gdb.printing.register_pretty_printer(gdb.current_objfile(), printer)

  # lldb treats all negative values here as 'unlimited'.
  # gdb.parameter('print elements') returns None in this case.
  debugger.HandleCommand('settings set -- target.max-children-count -99')
  print("gdb.parameter('print elements'):", gdb.parameter('print elements'))

  # lldb treats 0 as 'skip all children'.
  # gdb.parameter('print elements') doesn't return 0 in this case, as gdb treats
  # it as unlimited and returns None.
  #
  # In this case we preserve the 0 to respect lldb semantics. We may revisit
  # this decision if we find any breaking example.
  debugger.HandleCommand('settings set target.max-children-count 0')
  print("gdb.parameter('print elements'):", gdb.parameter('print elements'))

  debugger.HandleCommand('settings set target.max-children-count 10')
  print("gdb.parameter('print elements'):", gdb.parameter('print elements'))

  print("s = %s" % gdb.parse_and_eval('s'))
