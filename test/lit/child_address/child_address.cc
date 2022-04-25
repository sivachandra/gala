struct MyChild {
  const char *s;
};

struct MyClass {
  MyChild child;
};

MyClass obj = {MyChild{"hello"}};


int main() { return 0; }
