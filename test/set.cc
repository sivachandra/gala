
#include <set>

int
main ()
{
  std::set<int> s;
  for (int i = 0; i < 10; i++)
    s.insert(i);
  return s.size();
}
