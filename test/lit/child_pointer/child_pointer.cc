// This will be printed with a child "[0] = child_string".
struct MyClass {
  const char *child_string;
};

MyClass c = {"hello"};

// This will be printed as a map, with a child "[child_key] = child_value".
struct MyMap {
  const char *child_key;
  const char *child_value;
};

MyMap m = {"my_key", "my_value"};

int main() { return 0; }
