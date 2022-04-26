import gdb

print("b1: %d" % gdb.parse_and_eval("numbers.b1"))
print("(int)b1: %d" % gdb.parse_and_eval("numbers.b1").cast(gdb.lookup_type("int")))
print("s1: %d" % gdb.parse_and_eval("numbers.s1"))
print("(int)s1: %d" % gdb.parse_and_eval("numbers.s1").cast(gdb.lookup_type("int")))
