// Two different unrelated structs so we can test if type-callback matching
// works. In this case we'll match any type with a member named "x".
struct S1 {
  int x;
};

struct S2 {
  int x;
};

// A negative example.
struct S3 {
  int y;
};

S1 s1 = {1234};
S2 s2 = {5678};
S3 s3 = {9999};

int main() { return 0; }
