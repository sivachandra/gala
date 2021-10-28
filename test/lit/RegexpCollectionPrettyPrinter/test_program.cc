// All instantiations of this template will be matched with a regex like
// "TemplatedStruct<.*>".
template<typename T>
struct TemplatedStruct {
  T value;
};

struct PlainOldStruct {
  int plain_old_value;
};

PlainOldStruct p = {1111};
TemplatedStruct<int> ti = {1234};
TemplatedStruct<float> tf = {5678.9};
TemplatedStruct<PlainOldStruct> ts{{2222}};

int main() { return 0; }
