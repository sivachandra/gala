struct MyType {
  int x;
  MyType() {}
};

MyType x;
const MyType cx;
volatile MyType vx;
const volatile MyType cvx;

using MyTypePtr = MyType*;
MyTypePtr px = &x;

using MyTypePtrPtr = MyTypePtr*;
MyTypePtrPtr ppx = &px;

using MyTypeRef = MyType&;
MyTypeRef rx = x;

using MyTypePtrTypedef = MyTypePtr;
MyTypePtrTypedef px2 = &x;

int main() { return 0; }
