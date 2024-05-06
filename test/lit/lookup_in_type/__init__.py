import gala_compatibility
import gdb


def test(name, f):
    try:
        print("%s: %s\n" % (name, f()))
    except gdb.error as e:
        print("%s: %s\n" % (name, e))


Foo = gdb.lookup_type("Foo")
test("Foo::Bar", lambda: gala_compatibility.get_nested_type(Foo, "Bar").name)
test("Foo::Baz", lambda: gala_compatibility.get_nested_type(Foo, "Baz").name)
test(
    "Foo::bar",
    lambda: gala_compatibility.get_static_constexpr_value_from_type(Foo, "bar"),
)
test(
    "Foo::baz",
    lambda: gala_compatibility.get_static_constexpr_value_from_type(Foo, "baz"),
)
test(
    "Foo::mutable_bar",
    lambda: gala_compatibility.get_static_constexpr_value_from_type(Foo, "mutable_bar"),
)
