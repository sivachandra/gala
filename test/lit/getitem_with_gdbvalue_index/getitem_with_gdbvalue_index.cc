#include <string>
#include <vector>

int array[6] = {11, 22, 33, 44, 55, 66};

int int_index = 1;
char char_index = 2;
float float_index = 3.1f;
std::string string_index = "4";

enum MyEnum {
  ENUM_INDEX = 5,
};

MyEnum enum_index = MyEnum::ENUM_INDEX;

// This is a regression test for a case where GALA casting the array to its
// canonical type after stripping typedefs resulted in an SBValue that no longer
// had an address. Which in turn resulted in GALA not being able to index the
// array.
struct StructWithArray {
  int num_elements;
  // huge array to approximate the behavior of "flexible array members" in C,
  // without accessing memory past the end of the array.
  void* elements[268435454];
};

StructWithArray *ptr_to_struct_with_array = [](){
  void *ptr = malloc(sizeof(int) + 2*sizeof(void*));
  StructWithArray *s = reinterpret_cast<StructWithArray*>(ptr);
  s->num_elements = 2;
  s->elements[0] = nullptr;
  s->elements[1] = nullptr;
  return s;
}();

// A pointer to array, to check the pointer[integer_index] case.
int *ptr_to_array = array;

// A pointer to struct, to check the pointer["struct_member"] case.
struct MyStruct {
  int my_value;
};

MyStruct my_struct = {99};
MyStruct *ptr_to_struct = &my_struct;

// A struct with a base class and an anonymous union. lldb has known issues
// getting the right member with SBValue::GetChildMemberWithName() so we need to
// test the workaround here.
struct StructWithAnonymousUnion : public MyStruct {
  int a;
  int b;
  union {
    int c;
    int d;
  };
};

StructWithAnonymousUnion struct_with_anonymous_union = []() {
  StructWithAnonymousUnion result;
  result.my_value = 12;
  result.a = 34;
  result.b = 56;
  result.d = 78;
  return result;
}();

// Pointer to struct, but typedef'd.
std::vector<MyStruct> v = {{42}};
std::vector<MyStruct>::pointer typedefed_ptr_to_struct = &v[0];

// Array of structs, to check the array["struct_member"] case.
MyStruct struct_array[2]= {{1234}, {5678}};
// Same but typedefed.
typedef MyStruct StructArray[2];
StructArray typedefed_struct_array = {{1234}, {5678}};

int main() { return 0; }
