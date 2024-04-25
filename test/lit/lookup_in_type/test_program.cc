struct Foo {
  struct Bar {};
  static constexpr int bar = 47;
  static int mutable_bar;
};

Foo::Bar bar;
int Foo::mutable_bar = 42;

int main() {}
