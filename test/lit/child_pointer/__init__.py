import gdb
import gdb.printing

class MyClassSubprinter:
  """A subprinter for class MyMap."""

  # GALA's gdb.printing.register_pretty_printer relies on the subprinter "name"
  # attribute to create a regex that matches the type.
  name = "MyClass"
  def __init__(self, val):
    self.val = val

  def to_string(self):
    return "MyClass object with children:"

  def children(self):
    child_string = self.val["child_string"]
    yield "[0]", child_string

class MyClassPrinter:
  def __init__(self):
    self.name = "MyClassPrinter"
    self.enabled = True
    self.subprinters = [MyClassSubprinter]

  # GALA ignores this and applies regex matching on each subprinter's name, but
  # gdb calls this function to detect if this prettyprinter applies to `val`.
  def __call__(self, val):
    if val.type.name == "MyClass":
      return MyClassSubprinter(val)

    return None

class MyMapSubprinter:
  """A subprinter for class MyMap."""

  # GALA's gdb.printing.register_pretty_printer relies on the subprinter "name"
  # attribute to create a regex that matches the type.
  name = "MyMap"
  def __init__(self, val):
    self.val = val

  def display_hint(self):
    return "map"

  def to_string(self):
    return "MyMap object with children:"

  def children(self):
    child_key = self.val["child_key"]
    child_value = self.val["child_value"]
    yield "key[0]", child_key
    yield "val[0]", child_value

class MyMapPrinter:
  def __init__(self):
    self.name = "MyMapPrinter"
    self.enabled = True
    self.subprinters = [MyMapSubprinter]

  # GALA ignores this and applies regex matching on each subprinter's name, but
  # gdb calls this function to detect if this prettyprinter applies to `val`.
  def __call__(self, val):
    if val.type.name == "MyMap":
      return MyMapSubprinter(val)

    return None


gdb.printing.register_pretty_printer(gdb.current_objfile(), MyClassPrinter())
gdb.printing.register_pretty_printer(gdb.current_objfile(), MyMapPrinter())
