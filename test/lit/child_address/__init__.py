import gdb
import gdb.printing

class MyChildSubprinter:
  """A subprinter for class MyChild."""

  # GALA's gdb.printing.register_pretty_printer relies on the subprinter "name"
  # attribute to create a regex that matches the type.
  name = "MyChild"
  def __init__(self, val):
    self.val = val

  def to_string(self):
    s = self.val["s"]
    return "MyChild node at address 0x%x: '%s'" % (self.val.address, s.string())

class MyChildPrinter:
  def __init__(self):
    self.name = "MyChildPrinter"
    self.enabled = True
    self.subprinters = [MyChildSubprinter]

  # GALA ignores this and applies regex matching on each subprinter's name, but
  # gdb calls this function to detect if this prettyprinter applies to `val`.
  def __call__(self, val):
    if val.type.name == "MyChild":
      return MyChildSubprinter(val)

    return None


class MyClassSubprinter:
  """A subprinter for class MyClass."""

  # GALA's gdb.printing.register_pretty_printer relies on the subprinter "name"
  # attribute to create a regex that matches the type.
  name = "MyClass"
  def __init__(self, val):
    self.val = val

  def to_string(self):
    return "MyClass object with children:"

  def children(self):
    yield "[0]", self.val["child"]

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



gdb.printing.register_pretty_printer(gdb.current_objfile(), MyClassPrinter())
gdb.printing.register_pretty_printer(gdb.current_objfile(), MyChildPrinter())
