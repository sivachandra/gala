import gdb

i = gdb.Value(123)
print("int: %d" % i)
print("float: %.1f" % gdb.Value(567.8))
print("gdb.Value: %s" % gdb.Value(i))

int32_minus_one = b"\xff\xff\xff\xff"
print("int from raw data: %s" % gdb.Value(int32_minus_one, gdb.lookup_type('int')))
