import gdb

print(gdb.parse_and_eval("i"))
print(gdb.parse_and_eval("f"))
print(gdb.parse_and_eval("d"))
print(gdb.parse_and_eval("c"))
print(gdb.parse_and_eval("s").string())
