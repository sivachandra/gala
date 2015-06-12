
enum EnumList
{
  Val1,
  Val2,
  Val3,
  Val4
};

typedef EnumList MyEnum;
typedef MyEnum MyOwnEnum;

int
main ()
{
  MyOwnEnum v = Val3;
  return v;
}
