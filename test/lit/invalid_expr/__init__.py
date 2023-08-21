import gdb

# Eval a non-existing name. Should raise an exception.
try:
  x = gdb.parse_and_eval("jdfaskhjs")
except gdb.error:
  print("gdb.error was raised.")


