#include <bitset>

int
main ()
{
  std::bitset<10> bits;
  for (int i = 0; i < 10; i++)
    bits[i] = ((i % 3) == 0);
  return bits.size();
}
