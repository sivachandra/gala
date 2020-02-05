import gdb
import gdb.printing

class TuplePrinter(object):
  name = "Tuple"
  def __init__(self, val):
    self.val = val

  def to_string(self):
    return "Instance of %s" % str(self.val.type)

  def children(self):
    child_list = self.get_children(self.val)
    child_list = enumerate(child_list)
    return iter([(str(pair[0]), pair[1]) for pair in child_list])

  def get_children(self, val):
    child_list = []
    for field in val.type.fields():
      if field.name == "Value":
        child_list.append(val[field.name])
    for field in val.type.fields():
      if field.is_base_class:
        child_list.extend(self.get_children(val.cast(field.type)))
    return child_list

class MyPrinter(object):
  def __init__(self, name):
    self.name = name
    self.subprinters = []

  def __call__(self, val):
    if str(val.type).startswith("Tuple<"):
      return TuplePrinter(val)

PP = MyPrinter("MyPrinters")
PP.subprinters.append(TuplePrinter)

gdb.printing.register_pretty_printer(None, PP)
