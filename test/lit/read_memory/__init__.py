import gdb

s = gdb.parse_and_eval("s")
hello = str(gdb.selected_inferior().read_memory(int(s), 5).tobytes())
print(hello)

# Check that Value.string() works correctly with NUL-terminated strings.
print(s.string())
print(repr(s.string()))

