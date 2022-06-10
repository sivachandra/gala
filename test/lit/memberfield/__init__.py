import gdb

def print_field(f):
  print("========")
  print("name: %s" % f.name)
  print("type: %s" % f.type)
  if hasattr(f, "bitpos"):
    print("bitpos: %d" % f.bitpos)
  else:
    print("No bitpos attribute.")
  print("bitsize: %d" % f.bitsize)
  print("parent_type: %s" % f.parent_type)
  print("is_base_class: %s" % f.is_base_class)
  print("artificial: %s" % f.artificial)
  if hasattr(f, "enumval"):
    print("enumval: %d" % f.enumval)
  else:
    print("No enumval attribute.")

derived = gdb.lookup_type("Derived")
for f in derived.fields():
  print_field(f)

enum = gdb.lookup_type("EnumType")
for f in enum.fields():
  print_field(f)

derived_alias = gdb.lookup_type("DerivedAlias")
print("DerivedAlias has %d fields." % len(derived_alias.fields()))
