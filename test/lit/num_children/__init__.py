import gdb
import gdb.printing

class MyStructPrinter:
  MAX_MAX_COUNT = 0

  def __init__(self, val):
    self._val = val

  def display_hint(self):
    return "map"

  def to_string(self):
    return "A pretty MyStruct"

  def num_children(self, max_count):
    MyStructPrinter.MAX_MAX_COUNT = max(MyStructPrinter.MAX_MAX_COUNT, max_count)
    return 4

  def children(self):
    yield "key[0]", "key0"
    yield "val[0]", "val0"
    yield "key[1]", "key1"
    yield "val[1]", "val1"

printer = gdb.printing.RegexpCollectionPrettyPrinter("test_regexp_printer")
printer.add_printer("MyStruct", "MyStruct", MyStructPrinter)

gdb.printing.register_pretty_printer(gdb.current_objfile(), printer)
