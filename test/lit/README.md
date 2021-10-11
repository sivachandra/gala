# Lit tests for GALA

These tests assume you have access to some llvm tools (clang, lldb, FileCheck)
in your PATH. clang and lldb are usually installed if you build them, but in
order to have utils like FileCheck installed you have to make sure
`LLVM_INSTALL_UTILS` is true when you configure your build.

You also need lit in your path. A stand-alone version of lit is
available in PyPI, and can be installed by running `pip install lit`.

## Running the tests

Pass the path to the directory containing these tests to the lit tool. For
example, if you're in the root directory of the gala repo, run:
```
lit test/lit
```

## Adding new tests

The configuration for the test suite is in `lit.cfg.py`. It currently defines
`.test` as the only recognized extension for tests.

These tests usually have three parts:

- A source file that uses some language featue we want to test from the
  debugger.
- A python script that uses the gdb API to interact with the test program and
  prints some results.
- A `.test` file that contains some lit `RUN:` directives to build the test
  program and run the debugger, and some `CHECK:` directives to verify the
  output matches expectations.

Take a look at the existing tests for more details.

