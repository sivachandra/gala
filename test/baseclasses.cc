class Base
{
public:
  Base () { base_a = 1111; base_b = 11.11; }
  int base_a;
  double base_b;
};

class Virtual
{
public:
  Virtual () { virtual_a = 3333; virtual_b = 33.33; }
  int virtual_a;
  double virtual_b;
};

class Protected
{
public:
  Protected () { protected_a = 4444; protected_b = 44.44; }
  int protected_a;
  double protected_b;
};

class Derived : public Base, virtual public Virtual, protected Protected
{
public:
  Derived () : Base () { derived_a = 2222; derived_b = 22.22; }
  int derived_a;
  double derived_b;
};

int
main ()
{
  Derived obj;
  return obj.base_a - 1110;
}
