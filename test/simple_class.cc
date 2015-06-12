class A
{
public:
  int geta();
  int a;
  float b;
  double c;
};

int
A::geta()
{
  return a;
}

int
main ()
{
  A obj;
  obj.a = 12345;

  A a_array[5] = {
    {0, 0.0, 0.0}, {1, 1.1, 1.11},
    {2, 2.2, 2.22}, {3, 3.3, 3.33},
    {4, 4.4, 4.44}
  };

  return obj.geta();
}
