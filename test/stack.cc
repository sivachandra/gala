
#include <stack>

int
main ()
{
  std::stack<int> s;
  for (int i = 0; i < 100; i++)
    s.push(i);
  return s.size();
}
