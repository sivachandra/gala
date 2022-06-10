struct Base1 {
  int b1;
};

struct Base2 {
  int b2;
};

struct Derived : public Base1, Base2 {
  int x;
  int y;
};

enum EnumType {
  VALUE0 = 0,
  VALUE1 = 1234,
  VALUE2 = 5678,
};

Derived obj;
EnumType e;

typedef Derived DerivedAlias;
DerivedAlias obj2;

int main() { return 0; }
