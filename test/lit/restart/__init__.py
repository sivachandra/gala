import gdb
import gdb.printing

_STATIC_DATA = {}

class MyStructPrinter:
  def __init__(self, val):
    self.val = val
    self.typename = val.type.tag
    if self.typename not in _STATIC_DATA:
      _STATIC_DATA[self.typename] = gdb.parse_and_eval(self.typename + "::static_data")

  def display_hint(self):
    return "map"

  def to_string(self):
    return "A pretty MyStruct"

  def children(self):
    yield "key[0]", "MyStruct::static_data.x"
    yield "val[0]", _STATIC_DATA[self.typename]["x"]
    yield "key[1]", "MyStruct::static_data.y"
    yield "val[1]", _STATIC_DATA[self.typename]["y"]
    yield "key[2]", "pretty_value"
    yield "val[2]", self.val["value"]

printer = gdb.printing.RegexpCollectionPrettyPrinter("test_regexp_printer")
printer.add_printer("MyStruct", "MyStruct", MyStructPrinter)

gdb.printing.register_pretty_printer(gdb.current_objfile(), printer)
