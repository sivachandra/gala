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

// A pointer to array, to check the pointer[integer_index] case.
int *ptr_to_array = array;

// A pointer to struct, to check the pointer["struct_member"] case.
struct MyStruct {
  int my_value;
};

MyStruct my_struct = {99};
MyStruct *ptr_to_struct = &my_struct;
MyStruct struct_array[2]= {{1234}, {5678}};

int main() { return 0; }
