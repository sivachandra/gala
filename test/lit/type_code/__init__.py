import gdb

def check_type_code(type_name, expected, strip_typedefs=True):
  """Checks that the named type has a code equal to gdb.<attr_name>."""
  t = gdb.lookup_type(type_name)
  if strip_typedefs:
    t = t.strip_typedefs()
  print("[%s:%s] code = %d. expected = %d" %
        (type_name, "PASS" if t.code == expected else "FAIL", t.code, expected))

check_type_code("int", gdb.TYPE_CODE_INT)
# Interestingly, gdb does return TYPE_CODE_INT for chars and wchars too.
check_type_code("char", gdb.TYPE_CODE_INT)
check_type_code("wchar_t", gdb.TYPE_CODE_INT)
check_type_code("bool", gdb.TYPE_CODE_BOOL)
check_type_code("float", gdb.TYPE_CODE_FLT)
check_type_code("double", gdb.TYPE_CODE_FLT)
check_type_code("int_ptr", gdb.TYPE_CODE_TYPEDEF, strip_typedefs=False)
check_type_code("int_ptr", gdb.TYPE_CODE_PTR)
check_type_code("int_ref", gdb.TYPE_CODE_REF)
check_type_code("int_array", gdb.TYPE_CODE_ARRAY)
check_type_code("MyStruct", gdb.TYPE_CODE_STRUCT)
check_type_code("member_ptr", gdb.TYPE_CODE_MEMBERPTR)
check_type_code("method_ptr", gdb.TYPE_CODE_METHODPTR)
check_type_code("MyUnion", gdb.TYPE_CODE_UNION)
check_type_code("MyEnum", gdb.TYPE_CODE_ENUM)

