import gdb

print("non_nested = %s" % gdb.parse_and_eval("non_nested"))
print("non_nested_scoped = %s" % gdb.parse_and_eval("non_nested_scoped"))
print("nested = %s" % gdb.parse_and_eval("nested"))
print("nested_scoped = %s" % gdb.parse_and_eval("nested_scoped"))

