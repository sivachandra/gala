import gdb
import lldb

def get_basic_type(t):
  # This is not equivalent to what gdb does. For example, if you have:
  #
  # typedef int* pint;
  # typedef pint* ppint;
  #
  # and run `gdb.types.get_basic_type(gdb.lookup_type("ppint"))`, gdb won't give
  # you `int **`. It will stop stripping typedefs at `pint *`, which is
  # technically not a typedef, but a pointer.
  #
  # lldb, however, will give you `int **` even if you try to just strip
  # qualifiers with `SBType.GetUnqualifiedType`. So I'm not sure we can get the
  # exact behavior of "remove qualifiers and strip layers of typedefs only until
  # you find a pointer type".
  #
  # This will do the trick for basic cases like "get the underlying unqualified
  # type in order to match a RegexpCollectionPrettyPrinter".
  return gdb.Type(t.sbtype().GetUnqualifiedType().GetCanonicalType())

def _sbtype_has_field(sbtype, field_name):
  """Recursive helper to have has_field search up the inheritance hierarchy."""
  for f in sbtype.fields:
    if f.name == field_name:
      return True

  for b in sbtype.bases:
    if _sbtype_has_field(b.type, field_name):
      return True

  for b in sbtype.vbases:
    if _sbtype_has_field(b.type, field_name):
      return True

  return False


def has_field(t, field_name):
  return _sbtype_has_field(t.sbtype(), field_name)


def make_enum_dict(t):
  """Returns a dict {'enum_value_name': enum_value...}."""
  return {field.name: field.enumval for field in t.fields()}
