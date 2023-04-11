struct StaticData {
  int x;
  int y;
};

struct MyStruct {
  static StaticData static_data;
  int value;
};

StaticData MyStruct::static_data = {11, 22};
MyStruct s = {9999};

int main() { return 0; }
