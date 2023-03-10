import gdb
try:
  import lldb
  is_lldb = True
except:
  is_lldb = False

s = gdb.parse_and_eval("s")
if is_lldb:
  # Reference-typed SBValues show up as arguments to prettyprinters when the
  # prettyprinter doesn't skip references.
  #
  # However, it's hard to convince get implementation of gdb.parse_and_eval to
  # return a reference value, because EvaluateExpression will return a
  # `MyStruct` value when evaluating "ref", instead of a `MyStruct &`.
  #
  # So we just construct one by hand when running under lldb. This is a hack
  # that would be unnecessary if we had a more accurate impl for parse_and_eval.
  ref = gdb.Value(gdb.gala_get_current_target().FindFirstGlobalVariable("ref"))
else:
  ref = gdb.parse_and_eval("ref")
print("s.address = %x" % s.address)
print("ref.type = %s" % ref.type)
print("ref.address = %x" % ref.address)
