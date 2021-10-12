import gdb

array = gdb.parse_and_eval("array")
print("literal_index -> %d" % array[0])

int_index = gdb.parse_and_eval("int_index")
char_index = gdb.parse_and_eval("char_index")
float_index = gdb.parse_and_eval("float_index")
string_index = gdb.parse_and_eval("string_index")
enum_index = gdb.parse_and_eval("enum_index")
print("int_index -> %d" % array[int_index])
print("char_index -> %d" % array[char_index])
print("float_index -> %d" % array[float_index])
try:
  print(array[string_index])
except gdb.error:
  print("string_index -> ERROR")

print("enum_index -> %d" % array[enum_index])
