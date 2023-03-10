import gdb
import gdb.types

t = gdb.lookup_type("MyType")
print("get_basic_type(%s) = %s" % (t, gdb.types.get_basic_type(t)))

pt = gdb.lookup_type("MyTypePtr")
print("get_basic_type(%s) = %s" % (pt, gdb.types.get_basic_type(pt)))

ppt = gdb.lookup_type("MyTypePtrPtr")
print("get_basic_type(%s) = %s" % (ppt, gdb.types.get_basic_type(ppt)))

rt = gdb.lookup_type("MyTypeRef")
print("get_basic_type(%s) = %s" % (rt, gdb.types.get_basic_type(rt)))

pt2 = gdb.lookup_type("MyTypePtrTypedef")
print("get_basic_type(%s) = %s" % (pt2, gdb.types.get_basic_type(pt2)))
