############################################################################
## Copyright 2015-2021 Google LLC
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
from typing import Any, Dict, List, Optional


class error(RuntimeError):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


pretty_printers = []

default_debugger = None
current_target = None


# lldb allows for multiple debuggers and targets to exist at the same time. It
# also allows to print values from targets not currently selected. So we
# shouldn't rely on `lldb.debugger` or `lldb.debugger.GetSelectedTarget()`.
# Instead, we use the `SBValue` we're currently trying to print as the main
# source of truth.
#
# NOTE: we also need a debugger for prettyprinter registration, so we save
# `default_debugger` set from `__lldb_init_module`, and will be used when there
# is no `current_target` set from a prettyprinter.
def gala_set_current_target(sbtarget: lldb.SBTarget) -> None:
    global current_target
    old_target = current_target
    current_target = sbtarget
    return old_target


def gala_reset_current_target() -> None:
    global current_target
    current_target = None


def gala_get_current_target() -> lldb.SBTarget:
    # If we aren't called from a prettyprinter, fall back to the current target.
    # This is useful, for example, in our unit tests that just import gdb and run
    # gdb.parse_and_eval("whatever") to test properties of `gdb.Value` objects.
    if current_target:
        return current_target
    elif gala_get_current_debugger():
        return gala_get_current_debugger().GetSelectedTarget()
    else:
        return lldb.target


def gala_get_current_debugger() -> lldb.SBDebugger:
    if current_target:
        return current_target.GetDebugger()
    elif default_debugger:
        return default_debugger
    else:
        return lldb.debugger


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
    lldb.eTypeClassMemberPointer: TYPE_CODE_MEMBERPTR,
    lldb.eTypeClassObjCObject: TYPE_CODE_UNDEF,
    lldb.eTypeClassObjCInterface: TYPE_CODE_UNDEF,
    lldb.eTypeClassObjCObjectPointer:TYPE_CODE_UNDEF,
    lldb.eTypeClassPointer: TYPE_CODE_PTR,
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
    # In the "type_code" test case, gdb maps char types to TYPE_CODE_INT. I
    # don't know how I can make it produce a type with TYPE_CODE_CHAR, so for
    # now we'll map char types to int.
    lldb.eBasicTypeChar: TYPE_CODE_INT,
    lldb.eBasicTypeSignedChar: TYPE_CODE_INT,
    lldb.eBasicTypeUnsignedChar: TYPE_CODE_INT,
    lldb.eBasicTypeWChar: TYPE_CODE_INT,
    lldb.eBasicTypeSignedWChar: TYPE_CODE_INT,
    lldb.eBasicTypeUnsignedWChar: TYPE_CODE_INT,
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

BUILTIN_TYPE_NAME_TO_BASIC_TYPE = {
    'void': lldb.eBasicTypeVoid,
    'char': lldb.eBasicTypeChar,
    'signed char': lldb.eBasicTypeSignedChar,
    'unsigned char': lldb.eBasicTypeUnsignedChar,
    'short': lldb.eBasicTypeShort,
    'unsigned short': lldb.eBasicTypeUnsignedShort,
    'int': lldb.eBasicTypeInt,
    'unsigned': lldb.eBasicTypeUnsignedInt,
    'unsigned int': lldb.eBasicTypeUnsignedInt,
    'long': lldb.eBasicTypeLong,
    'unsigned long': lldb.eBasicTypeUnsignedLong,
    'long long': lldb.eBasicTypeLongLong,
    'unsigned long long': lldb.eBasicTypeUnsignedLongLong,
    'bool': lldb.eBasicTypeBool,
    'float': lldb.eBasicTypeFloat,
    'double': lldb.eBasicTypeDouble,
    'long double': lldb.eBasicTypeLongDouble,
    'nullptr_t': lldb.eBasicTypeNullPtr,
}


def get_builtin_sbtype(typename: str) -> lldb.SBType:
    return gala_get_current_target().GetBasicType(
        BUILTIN_TYPE_NAME_TO_BASIC_TYPE[typename])


def _format_enum_value_name(enum_sbtype: lldb.SBType, name: str) -> str:
    # We need to special-case nested and scoped enums because the default
    # behavior of lldb for enum values is different from gdb. We want this:
    # - plain:         'VALUE'
    # - scoped:        'ScopedEnum::VALUE'
    # - nested:        'EnclosingClass::VALUE'
    # - nested scoped: 'EnclosingClass::ScopedEnum::VALUE'
    typename = enum_sbtype.GetName()
    if '::' in typename or enum_sbtype.IsScopedEnumerationType():
      if enum_sbtype.IsScopedEnumerationType():
        prefix = typename  # prefix is the whole type, nested or not.
      else:
        # nested but non-scoped, remove the last component from type name.
        prefix = typename[:typename.rfind('::')]
      return '%s::%s' % (prefix, name)
    else:
      return name


class Field(object):
  def __init__(self,
               name: str,
               type: 'Type',
               bitpos: int,
               bitsize: int,
               parent_type: 'Type',
               is_base_class: bool,
               enumval: Optional[int] = None):
        self.name = name
        self.type = type
        # Enum fields have enumval, but not bitpos. Note that 0 is falsey, so
        # we have to check explicitly for not None.
        if enumval is not None:
            self.enumval = enumval
        else:
            self.bitpos = bitpos
        self.bitsize = bitsize
        self.parent_type = parent_type
        self.is_base_class = is_base_class
        self.artificial = False


class Type(object):
    def __init__(self, sbtype_object: lldb.SBType):
        self._sbtype_object = sbtype_object

    def sbtype(self) -> lldb.SBType:
        return self._sbtype_object

    def _is_baseclass(
            self, baseclass_sbtype: lldb.SBType) -> tuple[bool, Optional[int]]:
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
    def code(self) -> int:
        type_class = self._sbtype_object.GetTypeClass()
        type_code = TYPE_CLASS_TO_TYPE_CODE_MAP.get(type_class,
                                                    TYPE_CODE_UNDEF)
        # Both member pointers and method pointers have eTypeClassMemberPointer
        # in lldb. We need extra logic to distinguish them.
        if (type_class == lldb.eTypeClassMemberPointer and
            self._sbtype_object.GetPointeeType().IsFunctionType()):
          type_code = TYPE_CODE_METHODPTR

        if int(type_code) != int(TYPE_CODE_UNDEF):
            return int(type_code)

        if type_class == lldb.eTypeClassBuiltin:
            basic_type = self._sbtype_object.GetBasicType()
            return int(
                BASIC_TYPE_TO_TYPE_CODE_MAP.get(basic_type, TYPE_CODE_UNDEF))

        return TYPE_CODE_UNDEF

    @property
    def name(self) -> str:
        return self._sbtype_object.GetName()

    @property
    def sizeof(self) -> int:
        return self._sbtype_object.GetByteSize()

    @property
    def tag(self) -> str:
        return self._sbtype_object.GetName()

    def target(self) -> 'Type':
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

    def strip_typedefs(self) -> 'Type':
        sbtype = self._sbtype_object
        while sbtype.GetTypedefedType():
            if sbtype == sbtype.GetTypedefedType():
                break
            sbtype = sbtype.GetTypedefedType()
        return Type(sbtype)

    def unqualified(self) -> 'Type':
        return Type(self._sbtype_object.GetUnqualifiedType())

    def array(self, higher_bound: int) -> 'Type':
        # lldb expects size instead of higher_bound. gdb is pretty permissive
        # with the type of the bound as long as it's somewhat numeric, so we
        # cast it to an int to avoid type errors.
        return Type(self._sbtype_object.GetArrayType(int(higher_bound) + 1))

    def pointer(self) -> 'Type':
        return Type(self._sbtype_object.GetPointerType())

    def template_argument(self, n: int) -> 'Type | Value':
        # TODO: This is woefully incomplete!
        return Type(self._sbtype_object.GetTemplateArgumentType(n))

    def fields(self) -> List[Field]:
        t = self._sbtype_object.GetCanonicalType()
        type_class = t.GetTypeClass()
        fields = []
        if type_class == lldb.eTypeClassEnumeration:
            enum_list = t.GetEnumMembers()
            for i in range(0, enum_list.GetSize()):
                e = enum_list.GetTypeEnumMemberAtIndex(i)
                field_name = _format_enum_value_name(t, e.GetName())
                fields.append(Field(name=field_name,
                                    type=None,
                                    bitpos=None,
                                    bitsize=0,
                                    parent_type=self,
                                    is_base_class=False,
                                    enumval=e.GetValueAsSigned()))
        elif (type_class == lldb.eTypeClassUnion or
              type_class == lldb.eTypeClassStruct or
              type_class == lldb.eTypeClassClass):
            n_baseclasses = t.GetNumberOfDirectBaseClasses()
            for i in range(0, n_baseclasses):
                c = t.GetDirectBaseClassAtIndex(i)
                fields.append(Field(name=c.GetName(),
                                    type=Type(c.GetType()),
                                    bitpos=c.GetOffsetInBits(),
                                    bitsize=0,
                                    parent_type=self,
                                    is_base_class=True))
            for i in range(0, t.GetNumberOfFields()):
                f = t.GetFieldAtIndex(i)
                fields.append(Field(name=f.GetName(),
                                    type=Type(f.GetType()),
                                    bitpos=f.GetOffsetInBits(),
                                    bitsize=f.GetBitfieldSizeInBits(),
                                    parent_type=self,
                                    is_base_class=False))
        else:
            raise TypeError('Type "%s" cannot have fields.' % t.GetName())
        return fields


def _get_child_member_with_name(
        sbvalue: lldb.SBValue, name: str) -> lldb.SBValue:
    result = sbvalue.GetChildMemberWithName(name)
    if not result.IsValid() or result.GetName() != name:
        # Look for anonymous union members. gdb transparently looks through them
        # on __getitem__, but lldb doesn't so we have to do it here.
        for i in range(sbvalue.GetNumChildren()):
            child = sbvalue.GetChildAtIndex(i)
            if (child.GetName() is None and
                child.GetType().GetTypeClass() == lldb.eTypeClassUnion):
                result = child.GetChildMemberWithName(name)
                if result.IsValid():
                    break
    return result


class Value(object):
    def __init__(self, sbvalue_object: lldb.SBValue):
        self._sbvalue_object = sbvalue_object

    def sbvalue(self) -> lldb.SBValue:
        return self._sbvalue_object

    def _stripped_sbtype(self) -> tuple[lldb.SBType, int]:
        sbtype = self._sbvalue_object.GetType()
        stripped_sbtype = Type(sbtype).strip_typedefs().sbtype()
        type_class = stripped_sbtype.GetTypeClass()
        return stripped_sbtype, type_class

    def _as_number(self) -> int | float:
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

    def _binary_op(self,
                   other: 'Value | int | float',
                   op: int,
                   reverse: bool = False) -> 'Value':
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
                        res = diff // sbtype.GetPointeeType().GetByteSize()
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

    def _cmp(self, other: 'Value | int | float') -> int:
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

    def __str__(self) -> str:
        # For values of enum types we need to check if the value is one of the
        # enumerators in order to return a properly-formatted name. However, if
        # it's any other random integer value we just print the number.
        t = self._sbvalue_object.GetType()
        if t.GetTypeClass() == lldb.eTypeClassEnumeration:
            enum_list = t.GetEnumMembers()
            for i in range(enum_list.GetSize()):
                e = enum_list.GetTypeEnumMemberAtIndex(i)
                if self._as_number() == e.GetValueAsSigned():
                    return _format_enum_value_name(t, e.GetName())
            return str(self._as_number())

        # For pointers, make sure we always print the numeric value.
        # TODO: print a summary of what the pointer points to (for example,
        # `0x404060 <i>`), like gdb does.
        type_flags = t.GetTypeFlags()
        if type_flags & lldb.eTypeIsPointer:
            return "0x%x" % self._as_number()

        valstr = self._sbvalue_object.GetSummary()
        if not valstr:
            valstr = self._sbvalue_object.GetValue()
        if not valstr:
            valstr = str(self._sbvalue_object)
        return valstr

    def __index__(self) -> int:
        return int(self._as_number())

    def __int__(self) -> int:
        return int(self._as_number())

    def __float__(self) -> float:
        return float(self._as_number())

    def __getitem__(self, index: int) -> 'Value':
        sbtype = self._sbvalue_object.GetType()
        # Keep the value to print in `val`. It's not always `self`:
        # - If ptr["member name"], we need to dereference the pointer.
        # - If array["member name"], decay to pointer and dereference.
        val = self
        if (sbtype.GetCanonicalType().GetTypeClass() == lldb.eTypeClassPointer
            and isinstance(index, str)):
            val = Value(self._sbvalue_object.Dereference())
        elif (sbtype.GetCanonicalType().GetTypeClass() == lldb.eTypeClassArray
              and isinstance(index, str)):
            val = Value(self._sbvalue_object.GetChildAtIndex(0))
        else:
            val = self

        stripped_sbtype, type_class = val._stripped_sbtype()
        # Casting to stripped_sbtype directly can, in some cases, make us lose
        # the underlying address of the SBValue. Apply the Cast to a pointer
        # instead, converting to and fro.
        stripped_sbval = val.sbvalue().AddressOf().Cast(stripped_sbtype.GetPointerType()).Dereference()

        if (type_class == lldb.eTypeClassClass or
            type_class == lldb.eTypeClassStruct or
            type_class == lldb.eTypeClassUnion):
            # gdb also allows using a gdb.Field as a struct index.
            if isinstance(index, Field):
                index = index.name

            if not isinstance(index, str):
                raise error('Key value used to subscript a '
                            'class/struct/union value is not a string.')
            mem_sbval = _get_child_member_with_name(
                    stripped_sbval.GetNonSyntheticValue(), index)

            if not mem_sbval.IsValid():
                raise error(
                    'No member with name "%s" in value of type "%s".' %
                    (index, sbtype.GetName()))
            return Value(mem_sbval)

        # Not a struct/class/union.
        if isinstance(index, str):
          raise error('Attempt to extract a component of a value that is not a '
                      'struct/class/union.')

        if isinstance(index, Value):
          # The index can also be a numeric gdb.Value.
          try:
            index = int(index)
          except:
            raise error("Value can't be converted to integer.")

        if type_class == lldb.eTypeClassPointer:
            addr = self._sbvalue_object.GetValueAsUnsigned()
            elem_sbtype = self._sbvalue_object.GetType().GetPointeeType()
        elif type_class == lldb.eTypeClassArray:
            addr = self._sbvalue_object.GetLoadAddress()
            elem_sbtype = self._sbvalue_object.GetType().GetArrayElementType()
        else:
            raise error('Cannot subscript something of type `%s`.' %
                        str(sbtype))
        new_addr = addr + index * elem_sbtype.GetByteSize()
        return Value(self._sbvalue_object.CreateValueFromAddress(
             "", new_addr, elem_sbtype))

    def __add__(self, number: 'Value | int | float') -> 'Value':
        return self._binary_op(number, OP_ADD)

    def __radd__(self, number: 'Value | int | float') -> 'Value':
        return self._binary_op(number, OP_ADD, reverse=True)

    def __sub__(self, number: 'Value | int | float') -> 'Value':
        return self._binary_op(number, OP_SUB)

    def __rsub__(self, number: 'Value | int | float') -> 'Value':
        return self._binary_op(number, OP_SUB, reverse=True)

    def __mul__(self, number: 'Value | int | float') -> 'Value':
        return self._binary_op(number, OP_MUL)

    def __rmul__(self, number: 'Value | int | float') -> 'Value':
        return self._binary_op(number, OP_MUL, reverse=True)

    # gdb with python3 uses the truediv (/) operator, but still does integer
    # division.
    def __truediv__(self, number: 'Value | int | float') -> 'Value':
        return self._binary_op(number, OP_TRUEDIV)

    def __rtruediv__(self, number: 'Value | int | float') -> 'Value':
        return self._binary_op(number, OP_TRUEDIV, reverse=True)

    def __bool__(self) -> bool:
        sbtype, type_class = self._stripped_sbtype()
        type_flags = sbtype.GetTypeFlags()
        if ((type_flags & lldb.eTypeIsPointer) or
            (type_flags & lldb.eTypeIsEnumeration) or
            (type_flags & lldb.eTypeIsInteger) or
            (type_flags & lldb.eTypeIsFloat)):
            return self._as_number() != 0
        else:
            return self._sbvalue_object.IsValid()

    def __eq__(self, other: 'Value | int | float') -> bool:
        return self._cmp(other) == 0

    def __ne__(self, other: 'Value | int | float') -> bool:
        return self._cmp(other) != 0

    def __lt__(self, other: 'Value | int | float') -> bool:
        return self._cmp(other) < 0

    def __le__(self, other: 'Value | int | float') -> bool:
        return self._cmp(other) <= 0

    def __gt__(self, other: 'Value | int | float') -> bool:
        return self._cmp(other) > 0

    def __ge__(self, other: 'Value | int | float') -> bool:
        return self._cmp(other) >= 0

    def __and__(self, other: 'Value | int | float') -> 'Value':
        return self._binary_op(other, OP_BITWISE_AND)

    def __rand__(self, other: 'Value | int | float') -> 'Value':
        return self._binary_op(other, OP_BITWISE_AND, reverse=True)

    def __or__(self, other: 'Value | int | float') -> 'Value':
        return self._binary_op(other, OP_BITWISE_OR)

    def __ror__(self, other: 'Value | int | float') -> 'Value':
        return self._binary_op(other, OP_BITWISE_OR, reverse=True)

    def __xor__(self, other: 'Value | int | float') -> 'Value':
        return self._binary_op(other, OP_BITWISE_XOR)

    def __rxor__(self, other: 'Value | int | float') -> 'Value':
        return self._binary_op(other, OP_BITWISE_XOR, reverse=True)

    def __lshift__(self, other: 'Value | int | float') -> 'Value':
        return self._binary_op(other, OP_LSHIFT)

    def __rlshift__(self, other: 'Value | int | float') -> 'Value':
        return self._binary_op(other, OP_LSHIFT, reverse=True)

    def __rshift__(self, other: 'Value | int | float') -> 'Value':
        return self._binary_op(other, OP_RSHIFT)

    def __rrshift__(self, other: 'Value | int | float') -> 'Value':
        return self._binary_op(other, OP_RSHIFT, reverse=True)

    def __invert__(self) -> 'Value':
        value = self._as_number()
        if not isinstance(value, int):
            raise TypeError("Bad operand type for unary ~")
        res = ~value
        data = lldb.SBData()
        data.SetDataFromUInt64Array([res])
        return Value(self._sbvalue_object.CreateValueFromData(
            '', data, get_builtin_sbtype('long')))

    @property
    def type(self) -> Type:
        return Type(self._sbvalue_object.GetType())

    @property
    def address(self) -> 'Value':
        ptr_sbvalue = self._sbvalue_object.AddressOf()
        if not ptr_sbvalue.IsValid():
            load_address = self._sbvalue_object.GetLoadAddress()
            new_sbvalue = self._sbvalue_object.CreateValueFromAddress(
                '', load_address, self._sbvalue_object.GetType())
            ptr_sbvalue = new_sbvalue.AddressOf()
        return Value(ptr_sbvalue)

    def cast(self, gdbtype: Type) -> 'Value':
        target_sbtype = gdbtype.sbtype()
        self_sbtype = self._sbvalue_object.GetType()
        is_baseclass, offset = Type(self_sbtype)._is_baseclass(target_sbtype)
        if is_baseclass:
            return Value(self._sbvalue_object.CreateChildAtOffset(
                self._sbvalue_object.GetName(), offset, target_sbtype))
        # SBValue::Cast doesn't work correctly when casting an integer value to
        # a larger type (for example, char -> int). Performing such a cast
        # results in a garbage value from reading adjacent memory.
        #
        # Some prettyprinters do this kind of cast to prevent the debugger from
        # printing as 'A' an uint8_t variable known to be used as a number.
        if (self_sbtype.GetTypeFlags() & lldb.eTypeIsInteger and
            target_sbtype.GetTypeFlags() & lldb.eTypeIsInteger and
            self_sbtype.GetByteSize() < target_sbtype.GetByteSize()):
            result = gala_get_current_target().CreateValueFromExpression(
                self._sbvalue_object.GetName(), str(self._as_number()))
            return Value(result)
        return Value(self._sbvalue_object.Cast(target_sbtype))

    def reinterpret_cast(self, gdbtype: Type) -> 'Value':
        # lldb SBValue.Cast should work correctly to cast between pointer types.
        # TODO: error out if types are not correct for a reinterpret_cast.
        return Value(self._sbvalue_object.Cast(gdbtype.sbtype()))

    def dereference(self) -> 'Value':
        stripped_sbtype, _ = self._stripped_sbtype()
        stripped_sbval = self._sbvalue_object.Cast(stripped_sbtype)
        # gdb allows calling dereference() on arrays, and it's supposed to be
        # equivalent to *array_name.
        if stripped_sbtype.GetTypeFlags() & lldb.eTypeIsArray:
          return Value(stripped_sbval.GetChildAtIndex(0))
        return Value(stripped_sbval.Dereference())

    def referenced_value(self) -> 'Value':
        return Value(self._sbvalue_object.Dereference())

    def string(self,
               encoding: str = 'utf-8',
               errors: str = 'strict',
               length: Optional[int] = None) -> str:
        """Returns this value as a string.

        If `length` is not given, bytes will be fetched from memory until a null
        byte is found. The `encoding` and `errors` arguments are passed directly
        to `bytes.decode()` to convert bytes read from memory to the final
        result string.
        """
        if length is not None and length < 0:
            raise ValueError("length argument can't be negative.")
        target = gala_get_current_target()
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


def _RunCommand(command: str) -> str:
    """Runs an LLDB command and returns its output as a string."""
    result = lldb.SBCommandReturnObject()
    target = gala_get_current_target()
    # Run the command in the context of the currently selected frame to behave
    # as if we were running it from the command line. Note that there may be
    # no process (the user can print globals before running the program, for
    # example), so we default to just the target in that case.
    execution_context = lldb.SBExecutionContext(target.GetProcess(
    ).GetSelectedThread().GetSelectedFrame() if target.GetProcess() else target)
    gala_get_current_debugger().GetCommandInterpreter().HandleCommand(
        command, execution_context, result)
    return result.GetOutput()

def _GetSetting(name: str) -> str:
    """Returns the value of setting `name` as a string."""
    result = _RunCommand("settings show %s" % name)
    return result.split(" = ", maxsplit=1)[1]

class Parameter:
    pass


def parameter(s: str) -> Any:
    # gdb's 'print elements' is used for number of array elements to print and
    # also max number of chars in a string. lldb has 'target.max-children-count'
    # and 'target.max-string-summary-length', but max-children-count seems like
    # a closer match.
    if s == "print elements":
        return int(_GetSetting('target.max-children-count'))
    return None


class Inferior:
    def __init__(self, sbprocess: lldb.SBProcess):
        self._sbprocess = sbprocess

    def read_memory(
            self, address: Value | int, length: Value | int) -> memoryview:
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


def selected_inferior() -> Inferior:
    return Inferior(gala_get_current_target().GetProcess())


def parse_and_eval(expr) -> Value:
    opts = lldb.SBExpressionOptions()
    sbvalue = gala_get_current_target().EvaluateExpression(expr, opts)
    if sbvalue and sbvalue.IsValid():
        return Value(sbvalue)
    raise RuntimeError('Unable to evaluate "%s".', expr)


def lookup_type(name, block=None) -> Type:
    chunks = name.split('::')
    unscoped_name = chunks[-1]
    typelist = gala_get_current_target().FindTypes(unscoped_name)
    count = typelist.GetSize()
    for i in range(count):
        t = typelist.GetTypeAtIndex(i)
        if t.GetName() == name:
            return Type(t)
        else:
            canonical_sbtype = t.GetCanonicalType()
            if (canonical_sbtype.GetName() == name or
                (name.startswith('::') and
                 canonical_sbtype.GetName() == name[2:])):
                return Type(canonical_sbtype)
    # FIXME: When building with `-funsigned-char`, lookups for `char` can fail
    # because lldb will treat `char` as an alias of `unsigned char`. This is a
    # bug in lldb, and this hack should be removed once it's fixed.
    if name == 'char':
        return lookup_type('unsigned char')
    raise error('Type "%s" not found in %d matches.' % (name, count))


class Objfile:
    pass


def current_objfile() -> Optional[Objfile]:
    return None


class Progspace:
    pass


def current_progspace() -> Optional[Progspace]:
    return None


def default_visualizer(value: Value) -> Any:
    for p in pretty_printers:
        pp = p(value)
        if pp:
            return pp


def __lldb_init_module(debugger: lldb.SBDebugger, internal_dict: Dict):
    global default_debugger
    default_debugger = debugger
