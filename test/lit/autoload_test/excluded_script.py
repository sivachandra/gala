import sys

# gdb scripts are run like normal python scripts, so we need to check that
# the idiomatic `__name__ == '__main__'` comparison works as expected.
if __name__ == '__main__':
  print("Hi from excluded_script.py!", file=sys.stderr)
