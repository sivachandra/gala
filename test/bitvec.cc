
#include <vector>

int
main ()
{
  std::vector<bool> v;
  for (int i = 0; i < 250; i++)
    v.push_back((i % 3) == 0);
  return v.size();
}