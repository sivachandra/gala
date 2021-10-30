############################################################################
## Copyright 2015 Siva Chandra
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##   http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
############################################################################

import lldb


class error(BaseException):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "gdb.error: %s"%msg


pretty_printers = []


VERSION="10.0"


TYPE_CODE_BITSTRING = -1
TYPE_CODE_UNDEF = 0
TYPE_CODE_PTR = 1
TYPE_CODE_ARRAY = 2
TYPE_CODE_STRUCT = 3
TYPE_CODE_UNION = 4
TYPE_CODE_ENUM = 5
TYPE_CODE_FLAGS = 6
TYPE_CODE_FUNC = 7
TYPE_CODE_INT = 8
TYPE_CODE_FLT = 9
TYPE_CODE_VOID = 10
TYPE_CODE_SET = 11
TYPE_CODE_RANGE = 12
TYPE_CODE_STRING = 13
TYPE_CODE_ERROR = 14
TYPE_CODE_METHOD = 15
TYPE_CODE_METHODPTR = 16
TYPE_CODE_MEMBERPTR = 17
TYPE_CODE_REF = 18
TYPE_CODE_CHAR = 19
TYPE_CODE_BOOL = 20
TYPE_CODE_COMPLEX = 21
TYPE_CODE_TYPEDEF = 22
TYPE_CODE_NAMESPACE = 23
TYPE_CODE_DECFLOAT = 24
TYPE_CODE_MODULE = 25
TYPE_CODE_INTERNAL_FUNCTION = 26
TYPE_CODE_XMETHOD = 27


OP_ADD = 0
OP_SUB = 1
OP_BITWISE_AND = 2
OP_BITWISE_OR = 3
OP_BITWISE_XOR = 4
OP_LSHIFT = 5
OP_RSHIFT = 6
OP_MUL = 7
OP_TRUEDIV = 8


TYPE_CLASS_TO_TYPE_CODE_MAP = {
    lldb.eTypeClassInvalid: TYPE_CODE_UNDEF,
    lldb.eTypeClassArray: TYPE_CODE_ARRAY,
    lldb.eTypeClassBlockPointer: TYPE_CODE_UNDEF,
    lldb.eTypeClassBuiltin: TYPE_CODE_UNDEF,
    lldb.eTypeClassClass: TYPE_CODE_STRUCT,
    lldb.eTypeClassComplexFloat: TYPE_CODE_COMPLEX,
    lldb.eTypeClassComplexInteger: TYPE_CODE_COMPLEX,
    lldb.eTypeClassEnumeration: TYPE_CODE_ENUM,
    lldb.eTypeClassFunction: TYPE_CODE_FUNC,
    lldb.eTypeClassMemberPointer: TYPE_CODE_PTR,
    lldb.eTypeClassObjCObject: TYPE_CODE_UNDEF,
    lldb.eTypeClassObjCInterface: TYPE_CODE_UNDEF,
    lldb.eTypeClassObjCObjectPointer:TYPE_CODE_UNDEF,
    lldb.eTypeClassPointer: TYPE_CODE_UNDEF,
    lldb.eTypeClassReference: TYPE_CODE_REF,
    lldb.eTypeClassStruct: TYPE_CODE_STRUCT,
    lldb.eTypeClassTypedef: TYPE_CODE_TYPEDEF,
    lldb.eTypeClassUnion: TYPE_CODE_UNION,
    lldb.eTypeClassVector: TYPE_CODE_UNDEF,
    lldb.eTypeClassOther:TYPE_CODE_UNDEF,
    lldb.eTypeClassAny: TYPE_CODE_UNDEF

}


BASIC_TYPE_TO_TYPE_CODE_MAP = {
    lldb.eBasicTypeInvalid: TYPE_CODE_UNDEF,
    lldb.eBasicTypeVoid: TYPE_CODE_VOID,
    lldb.eBasicTypeChar: TYPE_CODE_CHAR,
    lldb.eBasicTypeSignedChar: TYPE_CODE_CHAR,
    lldb.eBasicTypeUnsignedChar: TYPE_CODE_CHAR,
    lldb.eBasicTypeWChar: TYPE_CODE_CHAR,
    lldb.eBasicTypeSignedWChar: TYPE_CODE_CHAR,
    lldb.eBasicTypeUnsignedWChar: TYPE_CODE_CHAR,
    lldb.eBasicTypeChar16: TYPE_CODE_CHAR,
    lldb.eBasicTypeChar32: TYPE_CODE_CHAR,
    lldb.eBasicTypeShort: TYPE_CODE_INT,
    lldb.eBasicTypeUnsignedShort: TYPE_CODE_INT,
    lldb.eBasicTypeInt: TYPE_CODE_INT,
    lldb.eBasicTypeUnsignedInt: TYPE_CODE_INT,
    lldb.eBasicTypeLong: TYPE_CODE_INT,
    lldb.eBasicTypeUnsignedLong: TYPE_CODE_INT,
    lldb.eBasicTypeLongLong: TYPE_CODE_INT,
    lldb.eBasicTypeUnsignedLongLong: TYPE_CODE_INT,
    lldb.eBasicTypeInt128: TYPE_CODE_INT,
    lldb.eBasicTypeUnsignedInt128: TYPE_CODE_INT,
    lldb.eBasicTypeBool: TYPE_CODE_BOOL,
    lldb.eBasicTypeHalf: TYPE_CODE_UNDEF,
    lldb.eBasicTypeFloat: TYPE_CODE_FLT,
    lldb.eBasicTypeDouble: TYPE_CODE_FLT,
    lldb.eBasicTypeLongDouble: TYPE_CODE_FLT,
    lldb.eBasicTypeFloatComplex: TYPE_CODE_COMPLEX,
    lldb.eBasicTypeDoubleComplex: TYPE_CODE_COMPLEX,
    lldb.eBasicTypeLongDoubleComplex: TYPE_CODE_COMPLEX,
    lldb.eBasicTypeObjCID: TYPE_CODE_UNDEF,
    lldb.eBasicTypeObjCClass: TYPE_CODE_UNDEF,
    lldb.eBasicTypeObjCSel: TYPE_CODE_UNDEF,
    lldb.eBasicTypeNullPtr: TYPE_CODE_UNDEF,
    lldb.eBasicTypeOther:TYPE_CODE_UNDEF,
}


BUILTIN_TYPE_NAME_TO_SBTYPE_MAP = {
    'char': None,
    'unsigned char': None,
    'short': None,
    'unsigned short': None,
    'int': None,
    'unsigned': None,
    'unsigned int': None,
    'long': None,
    'unsigned long': None,
    'long long': None,
    'unsigned long long': None,
    'float': None,
    'double': None,
    'long double': None
}

def get_builtin_sbtype(typename):
    sbtype = BUILTIN_TYPE_NAME_TO_SBTYPE_MAP.get(typename)
    if not sbtype:
        target = lldb.debugger.GetSelectedTarget()
        sbtype = target.FindFirstType(typename)
        BUILTIN_TYPE_NAME_TO_SBTYPE_MAP[typename] = sbtype
    return sbtype


class EnumField(object):
    def __init__(self, name, enumval, type):
        self.name = name
        self.enumval = enumval
        self.type = type
        self.is_base_class = False
    

class MemberField(object):
    def __init__(self, name, type, bitsize, parent_type):
        self.name = name
        self.type = type
        self.bitsize = bitsize
        self.parent_type = parent_type
        self.is_base_class = False


class BaseClassField(object):
    def __init__(self, name, type):
        self.name = name
        self.type = type
        self.is_base_class = True


class Type(object):
    def __init__(self, sbtype_object):
        self._sbtype_object = sbtype_object

    def sbtype(self):
        return self._sbtype_object

    def _is_baseclass(self, baseclass_sbtype):
        base_sbtype = Type(baseclass_sbtype).strip_typedefs().sbtype()
        self_sbtype = self.strip_typedefs().sbtype()
        for i in range(self_sbtype.GetNumberOfDirectBaseClasses()):
            base_mem = self_sbtype.GetDirectBaseClassAtIndex(i)
            base_sbtype_i = Type(base_mem.GetType()).strip_typedefs().sbtype()
            if base_sbtype_i == base_sbtype:
                return (True, base_mem.GetOffsetInBytes())
            else:
                is_baseclass, offset = Type(base_sbtype_i)._is_baseclass(
                    baseclass_sbtype)
                if is_baseclass:
                    return (True, base_mem.GetOffsetInBytes() + offset)
        return (False, None)

    def __str__(self):
        return self._sbtype_object.GetName()

    @property
    def code(self):
        type_class = self._sbtype_object.GetTypeClass()
        type_code = TYPE_CLASS_TO_TYPE_CODE_MAP.get(type_class,
                                                    TYPE_CODE_UNDEF)
        if int(type_code) != int(TYPE_CODE_UNDEF):
            return int(type_code)

        if type_class == lldb.eTypeClassBuiltin:
            basic_type = self._sbtype_object.GetBasicType()
            return int(
                BASIC_TYPE_TO_TYPE_CODE_MAP.get(basic_type, TYPE_CODE_UNDEF))

        return TYPE_CODE_UNDEF

    @property
    def name(self):
        return self._sbtype_object.GetName()

    @property
    def sizeof(self):
        return self._sbtype_object.GetByteSize()

    @property
    def tag(self):
        return self._sbtype_object.GetName()

    def target(self):
        type_class = self._sbtype_object.GetTypeClass()
        if type_class == lldb.eTypeClassPointer:
            return Type(self._sbtype_object.GetPointeeType())
        elif type_class == lldb.eTypeClassReference:
            return Type(self._sbtype_object.GetDereferencedType())
        elif type_class == lldb.eTypeClassArray:
            return Type(self._sbtype_object.GetArrayElementType())
        elif type_class == lldb.eTypeClassFunction:
            return Type(self._sbtype_object.GetFunctionReturnType())
        else:
            raise TypeError('Type "%s" cannot have target type.' %
                            self._sbtype_object.GetName())

    def strip_typedefs(self):
        sbtype = self._sbtype_object
        while sbtype.GetTypedefedType():
            if sbtype == sbtype.GetTypedefedType():
                break
            sbtype = sbtype.GetTypedefedType()
        return Type(sbtype)

    def unqualified(self):
        return Type(self._sbtype_object.GetUnqualifiedType())

    def array(self, higher_bound):
        # lldb expects size instead of higher_bound. gdb is pretty permissive
        # with the type of the bound as long as it's somewhat numeric, so we
        # cast it to an int to avoid type errors.
        return Type(self._sbtype_object.GetArrayType(int(higher_bound) + 1))

    def pointer(self):
        return Type(self._sbtype_object.GetPointerType())

    def template_argument(self, n):
        # TODO: This is woefully incomplete!
        return Type(self._sbtype_object.GetTemplateArgumentType(n))

    def fields(self):
        type_class = self._sbtype_object.GetTypeClass()
        fields = []
        if type_class == lldb.eTypeClassEnumeration:
            enum_list = self._sbtype_object.GetEnumMembers()
            for i in range(0, enum_list.GetSize()):
                e = enum_list.GetTypeEnumMemberAtIndex(i)
                fields.append(EnumField(e.GetName(),
                                        e.GetValueAsSigned(),
                                        Type(e.GetType())))
        elif (type_class == lldb.eTypeClassUnion or
              type_class == lldb.eTypeClassStruct or
              type_class == lldb.eTypeClassClass):
            n_baseclasses = self._sbtype_object.GetNumberOfDirectBaseClasses()
            for i in range(0, n_baseclasses):
                c = self._sbtype_object.GetDirectBaseClassAtIndex(i)
                fields.append(BaseClassField(c.GetName(), Type(c.GetType())))
            for i in range(0, self._sbtype_object.GetNumberOfFields()):
                f = self._sbtype_object.GetFieldAtIndex(i)
                fields.append(MemberField(f.GetName(),
                                          Type(f.GetType()),
                                          f.GetBitfieldSizeInBits(),
                                          self))
        else:
            raise TypeError('Type "%s" cannot have fields.' %
                            self._sbtype_object.GetName())
        return fields


class Value(object):
    def __init__(self, sbvalue_object):
        self._sbvalue_object = sbvalue_object

    def sbvalue(self):
        return self._sbvalue_object

    def _stripped_sbtype(self):
        sbtype = self._sbvalue_object.GetType()
        stripped_sbtype = Type(sbtype).strip_typedefs().sbtype()
        type_class = stripped_sbtype.GetTypeClass()
        return stripped_sbtype, type_class

    def _as_number(self):
        sbtype, _ = self._stripped_sbtype()
        type_flags = sbtype.GetTypeFlags()
        if type_flags & lldb.eTypeIsEnumeration:
            sbtype = sbtype.GetEnumerationIntegerType().GetCanonicalType()
            type_flags = sbtype.GetTypeFlags()
        if type_flags & lldb.eTypeIsPointer or type_flags & lldb.eTypeIsInteger:
            if type_flags & lldb.eTypeIsSigned:
                numval = self._sbvalue_object.GetValueAsSigned()
            else:
                numval = self._sbvalue_object.GetValueAsUnsigned()
        elif type_flags & lldb.eTypeIsFloat:
            basic_type = sbtype.GetBasicType()
            err = lldb.SBError()
            if basic_type == lldb.eBasicTypeFloat:
                numval = self._sbvalue_object.GetData().GetFloat(err, 0)
            elif basic_type == lldb.eBasicTypeDouble:
                numval = self._sbvalue_object.GetData().GetDouble(err, 0)
            elif basic_type == lldb.eBasicTypeLongDouble:
                numval = self._sbvalue_object.GetData().GetLongDouble(err, 0)
            else:
                raise RuntimeError('Unknown float type %s.' % sbtype.name)
            if not err.Success():
                raise RuntimeError(
                    'Could not convert float type value to a number:\n%s' %
                    err.GetCString())
        elif type_flags & lldb.eTypeIsArray:
            numval = self._sbvalue_object.GetLoadAddress()
        else:
            raise TypeError(
                'Conversion of type %s to number is not supported.'%sbtype.name)
        return numval

    def _binary_op(self, other, op, reverse=False):
        sbtype, type_class = self._stripped_sbtype()
        if type_class == lldb.eTypeClassPointer:
            if not (op == OP_ADD or op == OP_SUB) or reverse:
                raise TypeError(
                    'Invalid binary operation on/with pointer value.')
        if isinstance(other, int):
            other_val = other
            other_sbtype = get_builtin_sbtype('long')
            other_type_class = lldb.eTypeClassBuiltin
        elif isinstance(other, float):
            other_val = other
            other_sbtype = get_builtin_sbtype('double')
            other_type_class = lldb.eTypeClassBuiltin
        elif isinstance(other, Value):
            other_sbtype, other_type_class = other._stripped_sbtype()
            if (other_type_class == lldb.eTypeClassPointer and
                not (type_class == lldb.eTypeClassPointer and op == OP_SUB)):
                raise TypeError(
                    'Invalid binary operation on/with pointer value.')
            other_val = other._as_number()
        else:
            raise TypeError('Cannot perform binary operation with/on value '
                            'of type "%s".' % str(type(other)))
        if op == OP_BITWISE_AND:
            res = self._as_number() & other_val
        elif op == OP_BITWISE_OR:
            res = self._as_number() | other_val
        elif op == OP_BITWISE_XOR:
            res = self._as_number() ^ other_val
        elif op == OP_ADD:
            if type_class == lldb.eTypeClassPointer:
                addr = self._sbvalue_object.GetValueAsUnsigned()
                new_addr = (addr +
                            other_val * sbtype.GetPointeeType().GetByteSize())
                new_sbvalue = self._sbvalue_object.CreateValueFromAddress(
                    '', new_addr, sbtype.GetPointeeType())
                return Value(new_sbvalue.AddressOf().Cast(
                    self._sbvalue_object.GetType()))
            else:
                res = self._as_number() + other_val
        elif op == OP_SUB:
            if reverse:
                res = other_val - self._as_number()
            else:
                if type_class == lldb.eTypeClassPointer:
                    if other_type_class == lldb.eTypeClassPointer:
                        if sbtype != other_sbtype:
                            raise TypeError('Arithmetic operation on '
                                            'incompatible pointer types.')
                        diff = self._as_number() - other_val
                        return diff / sbtype.GetPointeeType().GetByteSize()
                    else:
                        return self._binary_op(- other_val, OP_ADD)
                else:
                    res = self._as_number() - other_val
        elif op == OP_MUL:
            if reverse:
                res = other_val * self._as_number()
            else:
                res = self._as_number() * other_val
        elif op == OP_TRUEDIV:
            self_val = self._as_number()
            if reverse:
                res = other_val / self_val
            else:
                res = self_val / other_val
            # gdb does integer division for integer gdb.Values, even in py3.
            # Check if we're doing int/int and convert the result accordingly.
            if isinstance(self_val, int) and isinstance(other_val, int):
                res = int(res)
        elif op == OP_LSHIFT:
            if reverse:
                return other_val << self._as_number()
            else:
                res = self._as_number() << other_val
        elif op == OP_RSHIFT:
            if reverse:
                return other_val >> self._as_number()
            else:
                res = self._as_number() >> other_val
        else:
            raise RuntimeError('Unsupported or incorrect binary operation.')
        data = lldb.SBData()
        if isinstance(res, int):
            data.SetDataFromUInt64Array([res])
            result_type = get_builtin_sbtype('long')
        elif isinstance(res, float):
            data.SetDataFromDoubleArray([res])
            result_type = get_builtin_sbtype('double')
        else:
            raise RuntimeError('Unsupported result type in binary operation.')
        return Value(self._sbvalue_object.CreateValueFromData(
            '', data, result_type))

    def _cmp(self, other):
        if (isinstance(other, int) or isinstance(other, float)):
            other_val = other
        elif isinstance(other, Value):
            other_val = other._as_number()
        else:
            raise TypeError('Comparing incompatible types.')
        self_val = self._as_number()
        if self_val == other_val:
            return 0
        elif self_val < other_val:
            return -1
        else:
            return 1

    def __str__(self):
        valstr = self._sbvalue_object.GetSummary()
        if not valstr:
            valstr = self._sbvalue_object.GetValue()
        if not valstr:
            valstr = str(self._sbvalue_object)
        return valstr

    def __index__(self):
        return int(self._as_number())

    def __int__(self):
        return int(self._as_number())

    def __float__(self):
        return float(self._as_number())

    def __getitem__(self, index):
        sbtype = self._sbvalue_object.GetType()
        stripped_sbtype, type_class = self._stripped_sbtype()
        # If ptr["member name"], we need to dereference the pointer.
        if type_class == lldb.eTypeClassPointer and isinstance(index, str):
            val = Value(
                self._sbvalue_object.Cast(stripped_sbtype).Dereference())
            stripped_sbtype, type_class = val._stripped_sbtype()
            stripped_sbval = val.sbvalue().Cast(stripped_sbtype)
        else:
            stripped_sbval = self._sbvalue_object.Cast(stripped_sbtype)
        if (type_class == lldb.eTypeClassClass or
            type_class == lldb.eTypeClassStruct or
            type_class == lldb.eTypeClassUnion):
            if not isinstance(index, str):
                raise KeyError('Key value used to subscript a '
                               'class/struct/union value is not a string.')
            mem_sbval = (stripped_sbval.GetNonSyntheticValue()
                         .GetChildMemberWithName(index))
            if (not mem_sbval) or (not mem_sbval.IsValid()):
                raise KeyError(
                    'No member with name "%s" in value of type "%s".' %
                    (index, sbtype.GetName()))
            return Value(mem_sbval)

        if not isinstance(index, int):
            # The index can also be a numeric gdb.Value.
            try:
              index = int(index)
            except TypeError:
              raise error("Value can't be converted to integer.")

        if type_class == lldb.eTypeClassPointer:
            addr = self._sbvalue_object.GetValueAsUnsigned()
            elem_sbtype = self._sbvalue_object.GetType().GetPointeeType()
        elif type_class == lldb.eTypeClassArray:
            addr = self._sbvalue_object.GetLoadAddress()
            elem_sbtype = self._sbvalue_object.GetType().GetArrayElementType()
        else:
            raise TypeError('Cannot use "[]" operator on values of type "%s".' %
                            str(sbtype))
        new_addr = addr + index * elem_sbtype.GetByteSize()
        return Value(self._sbvalue_object.CreateValueFromAddress(
             "", new_addr, elem_sbtype))

    def __add__(self, number):
        return self._binary_op(number, OP_ADD)

    def __radd__(self, number):
        return self._binary_op(number, OP_ADD, reverse=True)

    def __sub__(self, number):
        return self._binary_op(number, OP_SUB)

    def __rsub__(self, number):
        return self._binary_op(number, OP_SUB, reverse=True)

    def __mul__(self, number):
        return self._binary_op(number, OP_MUL)

    def __rmul__(self, number):
        return self._binary_op(number, OP_MUL, reverse=True)

    # gdb with python3 uses the truediv (/) operator, but still does integer
    # division.
    def __truediv__(self, number):
        return self._binary_op(number, OP_TRUEDIV)

    def __rtruediv__(self, number):
        return self._binary_op(number, OP_TRUEDIV, reverse=True)

    def __bool__(self):
        sbtype, type_class = self._stripped_sbtype()
        type_flags = sbtype.GetTypeFlags()
        if ((type_flags & lldb.eTypeIsPointer) or
            (type_flags & lldb.eTypeIsEnumeration) or
            (type_flags & lldb.eTypeIsInteger) or
            (type_flags & lldb.eTypeIsFloat)):
            return self._as_number() != 0
        else:
            return self._sbvalue_object.IsValid()

    def __eq__(self, other):
        if self._cmp(other) == 0:
            return True
        else:
            return False

    def __ne__(self, other):
        if self._cmp(other) != 0:
            return True
        else:
            return False

    def __lt__(self, other):
        if self._cmp(other) < 0:
            return True
        else:
            return False

    def __le__(self, other):
        if self._cmp(other) <= 0:
            return True
        else:
            return False

    def __gt__(self, other):
        if self._cmp(other) > 0:
            return True
        else:
            return False

    def __ge__(self, other):
        if self._cmp(other) >= 0:
            return True
        else:
            return False

    def __and__(self, other):
        return self._binary_op(other, OP_BITWISE_AND)

    def __rand__(self, other):
        return self._binary_op(other, OP_BITWISE_AND, reverse=True)

    def __or__(self, other):
        return self._binary_op(other, OP_BITWISE_OR)

    def __ror__(self, other):
        return self._binary_op(other, OP_BITWISE_OR, reverse=True)

    def __xor__(self, other):
        return self._binary_op(other, OP_BITWISE_XOR)

    def __rxor__(self, other):
        return self._binary_op(other, OP_BITWISE_XOR, reverse=True)

    def __lshift__(self, other):
        return self._binary_op(other, OP_LSHIFT)

    def __rlshift__(self, other):
        return self._binary_op(other, OP_LSHIFT, reverse=True)

    def __rshift__(self, other):
        return self._binary_op(other, OP_RSHIFT)

    def __rrshift__(self, other):
        return self._binary_op(other, OP_RSHIFT, reverse=True)

    @property
    def type(self):
        return Type(self._sbvalue_object.GetType())

    @property
    def address(self):
        ptr_sbvalue = self._sbvalue_object.AddressOf()
        if not ptr_sbvalue.IsValid():
            load_address = self._sbvalue_object.GetLoadAddress()
            new_sbvalue = self._sbvalue_object.CreateValueFromAddress(
                '', load_address, self._sbvalue_object.GetType())
            ptr_sbvalue = new_sbvalue.AddressOf()
        return Value(ptr_sbvalue)

    def cast(self, gdbtype):
        target_sbtype = gdbtype.sbtype()
        self_sbtype = self._sbvalue_object.GetType()
        is_baseclass, offset = Type(self_sbtype)._is_baseclass(target_sbtype)
        if is_baseclass:
            return Value(self._sbvalue_object.CreateChildAtOffset(
                self._sbvalue_object.GetName(), offset, target_sbtype))
        return Value(self._sbvalue_object.Cast(gdbtype.sbtype()))

    def reinterpret_cast(self, gdbtype):
        # lldb SBValue.Cast should work correctly to cast between pointer types.
        # TODO: error out if types are not correct for a reinterpret_cast.
        return Value(self._sbvalue_object.Cast(gdbtype.sbtype()))

    def dereference(self):
        stripped_sbtype, _ = self._stripped_sbtype()
        stripped_sbval = self._sbvalue_object.Cast(stripped_sbtype)
        # gdb allows calling dereference() on arrays, and it's supposed to be
        # equivalent to *array_name.
        if stripped_sbtype.GetTypeFlags() & lldb.eTypeIsArray:
          return Value(stripped_sbval.GetChildAtIndex(0))
        return Value(stripped_sbval.Dereference())

    def referenced_value(self):
        return Value(self._sbvalue_object.Dereference())

    def string(self, encoding='utf-8', errors='strict', length = None):
        """Returns this value as a string.

        If `length` is not given, bytes will be fetched from memory until a null
        byte is found. The `encoding` and `errors` arguments are passed directly
        to `bytes.decode()` to convert bytes read from memory to the final
        result string.
        """
        if length is not None and length < 0:
            raise ValueError("length argument can't be negative.")
        target = lldb.debugger.GetSelectedTarget()
        sberr = lldb.SBError()
        result_bytes = b''
        num_bytes_read = 0
        while True:
            if length is not None and num_bytes_read == length:
                break
            sbaddr = lldb.SBAddress(
                self._sbvalue_object.GetValueAsUnsigned() + num_bytes_read,
                target)
            byte = target.ReadMemory(sbaddr, 1, sberr)
            num_bytes_read += 1
            if length is None and byte == b'\0':
                break
            result_bytes += byte
        return result_bytes.decode(encoding, errors)


class Command:
    pass


class Parameter:
    pass


def parameter(s):
    return None


class Inferior:
    def __init__(self, sbprocess):
        self._sbprocess = sbprocess

    def read_memory(self, address, length):
        """Reads `length` bytes at `address`. Returns a bytes object."""
        # SBProcess.ReadMemory expects a positive length, so we need to handle
        # the empty case here.
        if length == 0:
            return memoryview(b'')
        err = lldb.SBError()
        result = self._sbprocess.ReadMemory(int(address), int(length), err)
        if not err.Success():
            raise RuntimeError(err)
        return memoryview(result)


def selected_inferior():
    return Inferior(lldb.debugger.GetSelectedTarget().GetProcess())


def parse_and_eval(expr):
    opts = lldb.SBExpressionOptions()
    sbvalue = lldb.debugger.GetSelectedTarget().EvaluateExpression(expr, opts)
    if sbvalue and sbvalue.IsValid():
        return Value(sbvalue)
    return RuntimeError('Unable to evaluate "%s".', expr)


def lookup_type(name, block=None):
    chunks = name.split('::')
    unscoped_name = chunks[-1]
    typelist = lldb.debugger.GetSelectedTarget().FindTypes(unscoped_name)
    count = typelist.GetSize()
    for i in range(count):
        t = typelist.GetTypeAtIndex(i)
        if t.GetName() == name:
            return Type(t)
        else:
            canonical_sbtype = t.GetCanonicalType()
            if canonical_sbtype.GetName() == name:
                return Type(canonical_sbtype)
    raise RuntimeError('Type "%s" not found in %d matches.' % (name, count))


def current_objfile():
    return None


def current_progspace():
    return None


def default_visualizer(value):
    for p in pretty_printers:
        pp = p(value)
        if pp:
            return pp
