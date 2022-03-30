import gdb

print("Values:")
print("non_nested = %s" % gdb.parse_and_eval("non_nested"))
print("non_nested_scoped = %s" % gdb.parse_and_eval("non_nested_scoped"))
print("nested = %s" % gdb.parse_and_eval("nested"))
print("nested_scoped = %s" % gdb.parse_and_eval("nested_scoped"))

enum = gdb.lookup_type("Enum")
scoped_enum = gdb.lookup_type("ScopedEnum")
nested_enum = gdb.lookup_type("Class::Enum")
nested_scoped_enum = gdb.lookup_type("Class::ScopedEnum")

print("\nFields:")
print("non_nested = %s" % enum.fields()[0].name)
print("non_nested_scoped = %s" % scoped_enum.fields()[0].name)
print("nested = %s" % nested_enum.fields()[0].name)
print("nested_scoped = %s" % nested_scoped_enum.fields()[0].name)

print("not_an_enumerator = %d" % gdb.parse_and_eval("not_an_enumerator"))

