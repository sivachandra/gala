import gdb
try:
  import lldb
  is_lldb = True
except:
  is_lldb = False

def get_global_ref(name):
  if is_lldb:
    # Reference-typed SBValues show up as arguments to prettyprinters when the
    # prettyprinter doesn't skip references.
    #
    # However, it's hard to convince our implementation of gdb.parse_and_eval to
    # return a reference value, because EvaluateExpression will return a
    # `MyStruct` value when evaluating "ref", instead of a `MyStruct &`.
    #
    # So we just construct one by hand when running under lldb. This is a hack
    # that would be unnecessary if we had a more accurate impl for parse_and_eval.
    ref = gdb.Value(gdb.gala_get_current_target().FindFirstGlobalVariable(name))
  else:
    ref = gdb.parse_and_eval(name)
  return ref

s = gdb.parse_and_eval("s")
ref = get_global_ref("ref")
print("s.address = %x" % s.address)
print("ref.type = %s" % ref.type)
print("ref.address = %x" % ref.address)

class MyStructPrinter:
  """Reads the size member and emits as many synthetic children.

  This gives us an easy way to test `set print elements`.
  """

  def __init__(self, val):
    self.val = val

  def to_string(self):
    return "pretty MyStruct"

printer = gdb.printing.RegexpCollectionPrettyPrinter("my_struct_printer")
printer.add_printer("my_struct_printer", "^MyStruct$", MyStructPrinter)
gdb.printing.register_pretty_printer(gdb.current_objfile(), printer)

# Make sure we can also take the address of a value that has an associated
# prettyprinter. This can fail if we get a synthetic value with no address.
s = gdb.parse_and_eval("s")
print("Pretty s = %s" % s)
print("s.address = %x" % s.address)

# Check that ref still works too.
ref = get_global_ref("ref")
print("Pretty ref = %s" % ref)
print("ref.address = %x" % ref.address)
