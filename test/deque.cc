
#include <deque>

int
main ()
{
  std::deque<int> q;
  for (int i = 0; i < 100; i++)
    q.push_back(i);
  return q.size();
}
