
#include <list>

int
main ()
{
  std::list<int> l;
  for (int i = 0; i < 10; i++)
    l.push_back(i);
  return l.size();
}
