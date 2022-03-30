import gdb

t1 = gdb.lookup_type("MyClass")
print("t1.name = %s" % t1.name)

t2 = gdb.lookup_type("::MyClass")
print("t2.name = %s" % t2.name)

try:
  gdb.lookup_type("::NonExistingType")
except gdb.error as e:
  print("lookup of non-existing type -> gdb.error: %s" % e)
