import gdb
import gdb.printing

class TemplatedStructPrinter:
  def __init__(self, val):
    self.val = val

  def display_hint(self):
    return "map"

  def to_string(self):
    return "A pretty TemplatedStruct of %s"%self.val.type.template_argument(0).name

  def children(self):
    yield "key[0]", "pretty_value"
    yield "val[0]", self.val["value"]

class PlainOldStructPrinter:
  def __init__(self, val):
    self.val = val

  def display_hint(self):
    return "map"

  def to_string(self):
    return "A pretty PlainOldStruct"

  def children(self):
    yield "key[0]", "pretty_value"
    yield "val[0]", self.val["plain_old_value"]

printer = gdb.printing.RegexpCollectionPrettyPrinter("test_regexp_printer")
printer.add_printer("TemplatedStruct", "TemplatedStruct<.*>", TemplatedStructPrinter)
printer.add_printer("PlainOldStruct", "PlainOldStruct", PlainOldStructPrinter)

gdb.printing.register_pretty_printer(gdb.current_objfile(), printer)
