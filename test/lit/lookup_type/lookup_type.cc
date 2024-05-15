class MyClass {};
MyClass x;

namespace ns {
class ClassInNS {};
ClassInNS class_in_ns;
}  // namespace ns

template <typename T>
struct Templated {
  struct InTemplate {};
  template <typename U>
  struct MoreTemplates {};
};

Templated<int>::InTemplate in_template;
Templated<ns::ClassInNS>::InTemplate in_complex_template;
Templated<ns::ClassInNS>::MoreTemplates<ns::ClassInNS> more_templates;

int main() { return 0; }
