import gdb

t = gdb.parse_and_eval("t")
f = gdb.parse_and_eval("f")

if t:
  print("t is truthy")
else:
  print("t is falsey")

if f:
  print("f is truthy")
else:
  print("f is falsey")

