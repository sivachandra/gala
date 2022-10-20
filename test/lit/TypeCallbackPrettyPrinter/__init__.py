import gdb
import gdb.printing
import gdb.types
from gala_compatibility import TypeCallbackPrettyPrinter

class ClassWithMemberNamedXPrinter(gdb.printing.PrettyPrinter):
  def __init__(self, val):
    self.val = val

  def to_string(self):
    return "A class with an X member. X = %d" % self.val["x"]


def has_x(t):
  try:
    return gdb.types.has_field(t, "x")
  except:
    return False


printer = TypeCallbackPrettyPrinter(
    "class-with-member-named-x", has_x, ClassWithMemberNamedXPrinter)
gdb.printing.register_pretty_printer(gdb.current_objfile(), printer)
