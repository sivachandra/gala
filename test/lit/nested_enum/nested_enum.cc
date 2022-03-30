enum Enum {
  VALUE,
};

enum class ScopedEnum {
  VALUE,
};

class Class {
 public:
  enum Enum {
    VALUE,
  };

  enum class ScopedEnum {
    VALUE,
  };
};

Enum non_nested = VALUE;
ScopedEnum non_nested_scoped = ScopedEnum::VALUE;
Class::Enum nested = Class::VALUE;
Class::ScopedEnum nested_scoped = Class::ScopedEnum::VALUE;

Enum not_an_enumerator = (Enum)1234;

int main() { return 0; }

