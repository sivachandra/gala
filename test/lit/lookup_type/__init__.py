import gdb

def test(name):
  try:
    t = gdb.lookup_type(name)
    print("%s => %s" % (name, t.name))
  except gdb.error as e:
    print("%s => %s" % (name, e))

test("int")
test("MyClass")
test("::MyClass")
test("ns::ClassInNS")
test("::ns::ClassInNS")
test("ns::MyClass")
test("::NonExistingType")

test("Templated<int>::InTemplate")
test("Templated<ns::ClassInNS>::InTemplate")
test("Templated<ns::ClassInNS>::MoreTemplates<ns::ClassInNS>")
