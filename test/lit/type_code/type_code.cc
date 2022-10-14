using int_ptr = int*;
using int_ref = int&;
using int_array = int[10];

struct MyStruct {
  int member;
  void Method() {}
};

using member_ptr = int MyStruct::*;
using method_ptr = void (MyStruct::*)();

union MyUnion {
  int i;
  float f;
};

enum MyEnum {
  ONE,
  TWO,
};

// Declare some variables so the types above will be present in debug info.
int i;
bool b;
char c;
wchar_t wc;
float f;
double d;
int_ptr ip;
int_ref ir = i;
int_array ia;
MyStruct ms;
member_ptr memberp;
method_ptr methodp;
MyUnion u;
MyEnum e;

int main() { return 0; }
