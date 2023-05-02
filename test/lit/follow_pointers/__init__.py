import gdb
import gdb.printing
import lldb

class MyStructPrinter:
  def __init__(self, val):
    self.val = val
    self.typename = val.type.tag

  def display_hint(self):
    return "map"

  def to_string(self):
    return "A pretty MyStruct"

  def children(self):
    yield "key[0]", "pretty_value"
    yield "val[0]", self.val["value"]

printer = gdb.printing.RegexpCollectionPrettyPrinter("test_regexp_printer")
printer.add_printer("MyStruct", "^MyStruct$", MyStructPrinter)

gdb.printing.register_pretty_printer(gdb.current_objfile(), printer)

def __lldb_init_module(debugger, internal_dict):
  target = debugger.GetSelectedTarget()
  ps = target.EvaluateExpression("ps");
  child = ps.GetChildAtIndex(0);
  print("child.GetName() = %s" % child.GetName())
  print("child.GetValueAsSigned() = %d" % child.GetValueAsSigned())

