"""GALA compatibility classes.

These classes expose lldb functionality that doesn't have an exact equivalent in
the gdb API, in a way that's compatible with both debuggers.
"""
import gdb
import gdb.printing

class TypeCallbackPrettyPrinter(gdb.printing.PrettyPrinter):
  """A type-callback prettyprinter compatible with GDB and lldb-with-GALA."""

  # The Subprinter class doesn't have any logic. We need it here because GALA's
  # implementation of `gdb.register_pretty_printer()` uses the
  # `gala_matching_function` and `gala_make_printer_function` subprinter
  # attributes to drive callback-based formatter registration in LLDB.
  class Subprinter(gdb.printing.SubPrettyPrinter):

    def __init__(self, name, matching_function, make_printer_function):
      self.enabled = True
      self.name = name
      self.gala_matching_function = matching_function
      self.gala_make_printer_function = make_printer_function

  def __init__(self, name, matching_function, make_printer_function):
    """Builds a TypeCallbackPrettyPrinter.

    Args:
      - name: a string to identify the prettyprinter.
      - matching_function: a function that takes a gdb.Type and returns True iff
                           we should use this prettyprinter.
      - make_printer_function: a function that takes a gdb.Value and returns a
                               gdb prettyprinter object.
    """
    subprinter = self.Subprinter(name, matching_function, make_printer_function)
    super(TypeCallbackPrettyPrinter, self).__init__(name, [subprinter])

  def __call__(self, val):
    sp = self.subprinters[0]
    if sp.gala_matching_function(val.type):
      return sp.gala_make_printer_function(val)
    return None


