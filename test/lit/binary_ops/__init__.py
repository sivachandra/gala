from __future__ import division
from __future__ import print_function

import gdb

# INTEGER OPS
i1 = gdb.parse_and_eval("i1")
i2 = gdb.parse_and_eval("i2")

# Sum
# gdb.Value + gdb.Value
print("i1 + i2 =", str(i1 + i2))
# gdbValue + int, and vice versa
print("i1 + 1 =", str(i1 + 1))
print("1 + i2 =", str(1 + i2))

# Subtraction
# gdb.Value - gdb.Value
print("i1 - i2 =", str(i1 - i2))
# gdbValue - int, and vice versa
print("i1 - 1 =", str(i1 - 1))
print("1 - i2 =", str(1 - i2))

# Multiplication
# gdb.Value * gdb.Value
print("i1 * i2 =", str(i1 * i2))
# gdbValue * int, and vice versa
print("i1 * 1 =", str(i1 * 1))
print("1 * i2 =", str(1 * i2))

# Division (gdb doesn't support // with gdb.Values as of this writing).
# gdb.Value / gdb.Value
print("i1 / i2 =", str(i1 / i2))
# gdbValue / int, and vice versa
print("i1 / 1 =", str(i1 / 1))
print("1 / i2 =", str(1 / i2))

# FLOAT OPS
# gdb.Values can be created from both C++ float and double values. However,
# python only has one 'float' type and AFAICT we can only create lldb SBValues
# from double data (SBData.SetDataFromDoubleArray), so "float + float"
# operations will actually create a double result.
f1 = gdb.parse_and_eval("f1")
f2 = gdb.parse_and_eval("f2")
d1 = gdb.parse_and_eval("d1")
d2 = gdb.parse_and_eval("d2")

# Sum
# float gdb.Value + float gdb.Value
print("f1 + f2 =", str(f1 + f2))
# float gdb.Value + float, and vice versa
print("f1 + 1.0 =", str(f1 + 1.0))
print("1.0 + f2 =", str(1.0 + f2))
# double gdb.Value + double gdb.Value
print("d1 + d2 =", str(d1 + d2))
# double gdb.Value + float, and vice versa
print("d1 + 1.0 =", str(d1 + 1.0))
print("1.0 + d2 =", str(1.0 + d2))
# float gdb.Value + double gdb.Value, and vice versa
print("f1 + d2 =", str(f1 + d2))
print("d1 + f2 =", str(d1 + f2))

# Subtraction
# float gdb.Value - float gdb.Value
print("f1 - f2 =", str(f1 - f2))
# float gdb.Value - float, and vice versa
print("f1 - 1.0 =", str(f1 - 1.0))
print("1.0 - f2 =", str(1.0 - f2))
# double gdb.Value - double gdb.Value
print("d1 - d2 =", str(d1 - d2))
# double gdb.Value - float, and vice versa
print("d1 - 1.0 =", str(d1 - 1.0))
print("1.0 - d2 =", str(1.0 - d2))
# float gdb.Value - double gdb.Value, and vice versa
print("f1 - d2 =", str(f1 - d2))
print("d1 - f2 =", str(d1 - f2))

# Multiplication
# float gdb.Value * float gdb.Value
print("f1 * f2 =", str(f1 * f2))
# float gdb.Value * float, and vice versa
print("f1 * 1.0 =", str(f1 * 1.0))
print("1.0 * f2 =", str(1.0 * f2))
# double gdb.Value * double gdb.Value
print("d1 * d2 =", str(d1 * d2))
# double gdb.Value * float, and vice versa
print("d1 * 1.0 =", str(d1 * 1.0))
print("1.0 * d2 =", str(1.0 * d2))
# float gdb.Value * double gdb.Value, and vice versa
print("f1 * d2 =", str(f1 * d2))
print("d1 * f2 =", str(d1 * f2))

# Division

# We format everything here to 2 decimal digits, mostly to make sure we have the
# right output type (int vs float) while avoiding precision issues in FileCheck
# textual comparison.

# float gdb.Value / float gdb.Value
print("f1 / f2 =", "%.2f"%(f1 / f2))
# int gdb.Value / float gdb.Value, and vice versa
print("i1 / f1 =", "%.2f"%(i1 / f1))
print("f1 / i1 =", "%.2f"%(f1 / i1))
# float gdb.Value / float, and vice versa
print("f1 / 1.0 =", "%.2f"%(f1 / 1.0))
print("1.0 / f2 =", "%.2f"%(1.0 / f2))
# double gdb.Value / double gdb.Value
print("d1 / d2 =", "%.2f"%(d1 / d2))
# double gdb.Value / float, and vice versa
print("d1 / 1.0 =", "%.2f"%(d1 / 1.0))
print("1.0 / d2 =", "%.2f"%(1.0 / d2))
# float gdb.Value / double gdb.Value, and vice versa
print("f1 / d2 =", "%.2f"%(f1 / d2))
print("d1 / f2 =", "%.2f"%(d1 / f2))

