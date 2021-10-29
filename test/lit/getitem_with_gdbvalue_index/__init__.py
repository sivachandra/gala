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

ptr_to_array = gdb.parse_and_eval("ptr_to_array")
print("ptr_to_array[int_index] -> %d" % ptr_to_array[int_index])

ptr_to_struct = gdb.parse_and_eval("ptr_to_struct")
print("ptr_to_struct[\"my_value\"] -> %d" % ptr_to_struct["my_value"])

