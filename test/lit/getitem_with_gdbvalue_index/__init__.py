import gdb

# getitem on an array with different index types
array = gdb.parse_and_eval("array")
print("array[int] -> %d" % array[0])

int_index = gdb.parse_and_eval("int_index")
char_index = gdb.parse_and_eval("char_index")
float_index = gdb.parse_and_eval("float_index")
string_index = gdb.parse_and_eval("string_index")
enum_index = gdb.parse_and_eval("enum_index")
print("array[Value(int)] -> %d" % array[int_index])
print("array[Value(char)] -> %d" % array[char_index])
print("array[Value(float)] -> %d" % array[float_index])
try:
  print(array[string_index])
except gdb.error as e:
  print("array[Value(string)] -> gdb.error: %s" % e)

print("array[Value(enum)] -> %d" % array[enum_index])

# array as a struct member with struct hack. See cc file for details.
struct_with_array = gdb.parse_and_eval("ptr_to_struct_with_array").dereference()
elements = struct_with_array["elements"]
try:
  print("struct hack: elements[1] -> %d" % elements[1])
except:
  # doesn't work without a process
  pass

# getitem on a struct
my_struct = gdb.parse_and_eval("my_struct")
print("struct[str] -> %d" % my_struct["my_value"])

# getitem on a struct but passing a gdb.Field instead of a name
field = my_struct.type.fields()[0]
print("struct[gdb.Field] -> %d" % my_struct[field])

try:
  print(my_struct["xxxxxxx"])
except gdb.error as e:
  print("struct[str/invalid] -> gdb.error: %s" % e)

try:
  print(my_struct[0])
except gdb.error as e:
  print("struct[int] -> gdb.error: %s" % e)

# getitem on a typedef'd struct
typedefed_struct = gdb.parse_and_eval("typedefed_struct")
print("typedefed_struct[str] -> %d" % typedefed_struct["my_value"])

# getitem on struct with a base class and an anonymous union.
struct_with_anonymous_union = gdb.parse_and_eval("struct_with_anonymous_union")
print("struct[anonymous union member].base_member -> %d" %
      struct_with_anonymous_union["my_value"])
print("struct[anonymous union member].anon_member -> %d" %
      struct_with_anonymous_union["d"])

# getitem on pointer to array/struct
ptr_to_array = gdb.parse_and_eval("ptr_to_array")
try:
  print("ptr_to_array[Value(int)] -> %d" % ptr_to_array[int_index])
except:
  # doesn't work without a process
  pass

print("Checking if out of bounds access raises an exception:")
try:
  v = ptr_to_array[1000000000000]
  print("Value was created. Now trying to read it.")
  print("v = %s" % v)
  print("FAILED")
except gdb.error as e:
  print("ptr_to_array[out of bounds] -> gdb.error: %s" % e)

ptr_to_struct = gdb.parse_and_eval("ptr_to_struct")
try:
  print("ptr_to_struct[str] -> %d" % ptr_to_struct["my_value"])
except:
  # doesn't work without a process
  pass

typedefed_ptr_to_struct = gdb.parse_and_eval("typedefed_ptr_to_struct")
try:
  print("typedefed_ptr_to_struct[str] -> %d" % typedefed_ptr_to_struct["my_value"])
except:
  # doesn't work without a process
  pass

# value["member_name"] on array of structs
struct_array = gdb.parse_and_eval("struct_array")
print("struct_array[str] -> %d" % struct_array["my_value"])

typedefed_struct_array = gdb.parse_and_eval("typedefed_struct_array")
print("typedefed_struct_array[str] -> %d" % typedefed_struct_array["my_value"])

# getitem on incorrect types
one = gdb.parse_and_eval("1")
member = gdb.parse_and_eval('"member"')
try:
  print(one[0])
except gdb.error as e:
  print("value(int)[int] -> gdb.error: %s" % e)

try:
  print(one[one])
except gdb.error as e:
  print("value(int)[value(int)] -> gdb.error: %s" % e)


try:
  print(one["member"])
except gdb.error as e:
  print("value(int)[str] -> gdb.error: %s" % e)

try:
  print(one[member])
except gdb.error as e:
  print("value(int)[value(str)] -> gdb.error: %s" % e)
