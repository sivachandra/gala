
#include <tuple>

int
main ()
{
  std::tuple<int, char, float, double> t(12345, 'z', 12.345, 123.45);
  return std::get<0>(t) - 12345;
}
