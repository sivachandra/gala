# GALA gdb compatibility modules

This directory contains Python libraries that are intended to run under both gdb
and lldb-with-GALA. The goal is to encapsulate functionality that can't be
provided in a 100% gdb-compatible way. This way, a script can remain compatible
with both debuggers.
