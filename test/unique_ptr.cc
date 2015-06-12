#include <memory>

class A
{
public:
  int a, b, c;
};

int
main ()
{
  std::unique_ptr<A> p(new A);

  p->a = 111;
  p->b = 222;
  p->c = 333;

  return p->a - 110;
}
