#include <string>

int array[6] = {11, 22, 33, 44, 55, 66};

int int_index = 1;
char char_index = 2;
float float_index = 3.1f;
std::string string_index = "4";

enum MyEnum {
  ENUM_INDEX = 5,
};

MyEnum enum_index = MyEnum::ENUM_INDEX;

int main() { return 0; }
