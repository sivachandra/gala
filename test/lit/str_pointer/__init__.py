import gdb

print("int_pointer = %s" % str(gdb.parse_and_eval("int_pointer")))
print("char_pointer = %s" % str(gdb.parse_and_eval("char_pointer")))
print("string_pointer = %s" % str(gdb.parse_and_eval("string_pointer")))
