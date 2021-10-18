import gdb

myclass = gdb.lookup_type("MyClass");
int_bound = gdb.parse_and_eval("int_bound")
char_bound = gdb.parse_and_eval("char_bound")
size_t_bound = gdb.parse_and_eval("size_t_bound")
float_bound = gdb.parse_and_eval("float_bound")
print(myclass.array(int_bound))
print(myclass.array(char_bound))
print(myclass.array(size_t_bound))
print(myclass.array(float_bound))
