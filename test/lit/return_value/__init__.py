import gdb
import gdb.printing

class TestStructPrinter:
  def __init__(self, val):
    self.val = val

  def display_hint(self):
    return "map"

  def to_string(self):
    return "A pretty TestStruct"

  def children(self):
    yield "key[0]", "gdb_value"
    yield "val[0]", self.val["value"]
    yield "key[1]", "int_value"
    yield "val[1]", 1234
    yield "key[2]", "str_value"
    yield "val[2]", "some_string"

printer = gdb.printing.RegexpCollectionPrettyPrinter("test_regexp_printer")
printer.add_printer("TestStruct", "TestStruct", TestStructPrinter)

gdb.printing.register_pretty_printer(gdb.current_objfile(), printer)
