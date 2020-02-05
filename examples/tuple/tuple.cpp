template <typename ...Types> class Tuple;

template <>
class Tuple<> {};

template <int Index, typename ...Types>
class TupleElement;

template <typename T, typename ...Types>
class Tuple<T, Types...> : public Tuple<Types...> {
public:
  T Value;
};

template <int Index, typename T, typename ...Types>
class TupleElement<Index, Tuple<T, Types...>> {
public:
  using Type = typename TupleElement<Index - 1, Tuple<Types...>>::Type;

  static Type &Get(Tuple<T, Types...> &TheTuple) {
    return TupleElement<Index - 1, Tuple<Types...>>::Get(TheTuple);
  }
};

template <typename T, typename ...Types>
class TupleElement<0, Tuple<T, Types...>> {
public:
  using Type = T;
  
  static Type &Get(Tuple<T, Types...> &TheTuple) {
    return TheTuple.Value;
  }
};

template <int Index, typename ...Types>
typename TupleElement<Index, Tuple<Types...>>::Type &Get(Tuple<Types...> &TheTuple) {
  return TupleElement<Index, Tuple<Types...>>::Get(TheTuple);
}

int main() {
  Tuple<int, Tuple<int, long long>> my_tuple;
  Get<0>(my_tuple) = 100;
  Get<0>(Get<1>(my_tuple)) = 23;
  Get<1>(Get<1>(my_tuple)) = 32;
  return Get<0>(my_tuple);
}
