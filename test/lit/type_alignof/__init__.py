import gdb

print('alignof("OverAligned") = %d' % gdb.lookup_type("OverAligned").alignof)
