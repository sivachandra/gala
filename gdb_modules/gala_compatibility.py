"""GALA compatibility classes.

These classes expose lldb functionality that doesn't have an exact equivalent in
the gdb API, in a way that's compatible with both debuggers.
"""
import gdb
import gdb.printing

IN_LLDB = hasattr(gdb, "__lldb_init_module")
IN_GDB = not IN_LLDB


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


def get_nested_type(containing_type, nested_type_name):
  """Finds a type nested in another type.

  Given a code like `struct A { struct B{}; };`, get_nested_type(reference_to_A,
  "B") returns a reference to the A::B class.

  Args:
    containing_type: gdb.Type referencing the containing type.
    nested_type_name: Name of the nested type.

  Returns:
    gdb.Type referring to the nested type, if it exists.
  """
  if IN_LLDB:
    # LLDB has a dedicated API for this functionality.
    nested_type = containing_type.sbtype().FindDirectNestedType(nested_type_name)
    if nested_type.IsValid():
      return gdb.Type(nested_type)
    raise gdb.error("There is no type named %s" % nested_type_name)
  else:
    # In GDB we have to look up the type by name.
    return gdb.lookup_type(containing_type.name + "::" + nested_type_name)


def get_static_constexpr_value_from_type(containing_type, value_name):
  """Finds a static member in a type.

  Given code like `struct A { static constexpr int b = 47; };`,
  get_static_constexpr_value_from_type(reference_to_A, "b") returns `gdb.Value(47)`.

  Args:
    containing_type: gdb.Type referencing the containing type.
    value_name: Name of the contained static member.

  Returns:
    gdb.Value referring to the static member, if it exists.
  """
  if IN_LLDB:
    # Use the dedicated LLDB API.
    field = containing_type.sbtype().GetStaticFieldWithName(value_name)
    if not field.IsValid():
      raise gdb.error("There is no static field named %s" % value_name)
    value = field.GetConstantValue(gdb.gala_get_current_target())
    if not value.IsValid():
      raise gdb.error("%s is not a constexpr field" % value_name)
    return gdb.Value(value)
  else:
    # GDB's Value API can obtain static members, but it requires an instance of
    # that class. Since we don't have one (it may not even exists), we create
    # a bogus value from a null pointer.
    return gdb.Value(0).cast(containing_type.pointer()).dereference()[value_name]
