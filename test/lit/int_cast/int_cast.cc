#include <cstdint>

// We are only interested in one variable of each type. We declare the struct
// like this to avoid padding, so we can control what goes into the adjacent
// memory.
struct Numbers {
  uint8_t b1, b2, b3, b4;
  uint16_t s1, s2;
};

Numbers numbers = {1, 2, 3, 4, 5, 6};

int main() {
  return 0;
}
