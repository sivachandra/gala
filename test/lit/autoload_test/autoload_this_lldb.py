import sys

# For lldb scripts, `command script import` should be used. This ensures that
# __lldb_init_module is called, and also that the module is accessible from
# the global namespace, so scripts can run something like
# ```
#   type summary add --python-function my_module.my_summary_function
# ```
# and lldb will find "my_module" correctly.
def __lldb_init_module(debugger, internal_dict):
  print("Hi from autoload_this_lldb.py! %s" % sys.modules["autoload_this_lldb"],
        file=sys.stderr)
