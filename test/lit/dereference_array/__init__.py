import gdb

array = gdb.parse_and_eval("array")
print(array.dereference())
print(array.dereference().type)
