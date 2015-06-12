# The MIT License (MIT)
# 
# Copyright (c) 2015 Siva Chandra
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import lldb


pretty_printers = []


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


BASIC_UNSIGNED_INTEGER_TYPES = [
    lldb.eBasicTypeUnsignedChar, lldb.eBasicTypeUnsignedWChar,
    lldb.eBasicTypeUnsignedShort, lldb.eBasicTypeUnsignedInt,
    lldb.eBasicTypeUnsignedLong, lldb.eBasicTypeUnsignedLongLong,
    lldb.eBasicTypeUnsignedInt128
]

BASIC_SIGNED_INTEGER_TYPES = [
    lldb.eBasicTypeChar, lldb.eBasicTypeSignedChar, lldb.eBasicTypeWChar,
    lldb.eBasicTypeChar16, lldb.eBasicTypeChar32, lldb.eBasicTypeShort,
    lldb.eBasicTypeInt, lldb.eBasicTypeLong, lldb.eBasicTypeLongLong,
    lldb.eBasicTypeInt128
]

BASIC_FLOAT_TYPES = [
    lldb.eBasicTypeFloat, lldb.eBasicTypeDouble, lldb.eBasicTypeLongDouble
]


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

    def __str__(self):
        return str(self._sbvalue_object)

    def __getitem__(self, index):
        # TODO: Clean this method up and add support to get members from
        # pointers to struct/class values.
        sbtype = self._sbvalue_object.GetType()
        stripped_sbtype = Type(sbtype).strip_typedefs().sbtype()
        type_class = stripped_sbtype.GetTypeClass()
        if (type_class == lldb.eTypeClassClass or
            type_class == lldb.eTypeClassStruct or
            type_class == lldb.eTypeClassUnion):
            if not isinstance(index, str):
                raise KeyError('Key value used to subscript a '
                               'class/struct/union value is not a string.')
            stripped_sbval = self._sbvalue_object.Cast(stripped_sbtype)
            mem_sbval = stripped_sbval.GetChildMemberWithName(index)
            if (not mem_sbval) or (not mem_sbval.IsValid()):
                raise KeyError(
                    'No member with name "%s" in value of type "%s".' %
                    (index, sbtype.GetName()))
            return Value(mem_sbval)

        if not (isinstance(index, int) or isinstance(index, long)):
            raise KeyError('Unsupported key type for "[]" operator.')

        if type_class == lldb.eTypeClassPointer:
            addr = self._sbvalue_object.GetValueAsUnsigned()
            elem_sbtype = self._sbvalue_object.GetType().GetPointeeType()
        elif type_class == lldb.eTypeClassArray:
            addr = self._sbvalue_object.GetLoadAddress()
            elem_sbtype = self._sbvalue_object.GetType().GetArrayElementType()
        else:
            raise TypeError('Cannot use "[]" operator on values of type "%s".' %
                            sbtype)
        new_addr = addr + index * elem_sbtype.GetByteSize()
        return Value(self._sbvalue_object.CreateValueFromAddress(
             "", new_addr, elem_sbtype))

    def _sum(self, number):
        # TODO: Make this method more general. It currently only supports
        # int or long second operand.
        if not (isinstance(number, int) or isinstance(number, long)):
            raise TypeError(
                'Cannot perform add/sub with "%s" as second operand.',
                str(type(number)))
        sbtype = self._sbvalue_object.GetType()
        sbtype = Type(sbtype).strip_typedefs().sbtype()
        type_class = sbtype.GetTypeClass()
        if sbtype.IsPointerType():
        #if type_class == lldb.eTypeClassPointer:
            addr = self._sbvalue_object.GetValueAsUnsigned()
            new_addr = (addr +
                        number * sbtype.GetPointeeType().GetByteSize())
            new_sbvalue = self._sbvalue_object.CreateValueFromAddress(
                '', new_addr, sbtype.GetPointeeType())
            return Value(
                new_sbvalue.AddressOf().Cast(self._sbvalue_object.GetType()))
        elif type_class == lldb.eTypeClassBuiltin:
            res = self.__int__() + int(number)
            data = lldb.SBData()
            data.SetDataFromUInt64Array([int(res)])
            return Value(
                self._sbvalue_object.CreateValueFromData(
                    '', data, lldb.target.FindFirstType('int')))
        raise TypeError('Cannot perform arithmetic operations on objects'
                        'of type "%s".' % self._sbvalue_object)

    def __add__(self, number):
        return self._sum(number)

    def __sub__(self, number):
        sbtype = self._sbvalue_object.GetType()
        sbtype = Type(sbtype).strip_typedefs().sbtype()
        type_class = sbtype.GetTypeClass()
        if isinstance(number, int) or isinstance(number, long):
            return self._sum(-number)
        elif type_class == lldb.eTypeClassPointer:
            if isinstance(number, Value):
                number_sbtype = number.sbvalue().GetType()
                number_sbtype = Type(number_sbtype).strip_typedefs().sbtype()
                if number_sbtype == sbtype:
                    op1 = self._sbvalue_object.GetValueAsUnsigned()
                    op2 = number.sbvalue().GetValueAsUnsigned()
                    diff = (op1 - op2) / sbtype.GetPointeeType().GetByteSize()
                    return diff
        raise TypeError('Cannot perform arithmetic operations on objects'
                        'of type "%s".' % self._sbvalue_object.GetType())

    def __int__(self):
        sbtype = self._sbvalue_object.GetType()
        sbtype = Type(sbtype).strip_typedefs().sbtype()
        type_class = sbtype.GetTypeClass()
        if ((type_class == lldb.eTypeClassPointer) or
            (type_class in BASIC_UNSIGNED_INTEGER_TYPES)):
            intval = self._sbvalue_object.GetValueAsUnsigned()
        elif type_class in BASIC_SIGNED_INTEGER_TYPES:
            intval = self._sbvalue_object.GetValueAsSigned()
        else:
            return NotImplementedError(
                'Comparison of non-integral/non-pointer values is not '
                'implemented')
        return intval

    def _cmp(self, other):
        if self.__int__() == int(other):
            return 0
        elif self.__int__() < int(other):
            return -1
        else:
            return 1

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
        res = self.__int__() & int(other)
        data = lldb.SBData()
        data.SetDataFromUInt64Array([int(res)])
        return Value(self._sbvalue_object.CreateValueFromData(
            '', data, self._sbvalue_object.GetType()))

    def __or__(self, other):
        res = self.__int__() | int(other)
        data = lldb.SBData()
        data.SetDataFromUInt64Array([int(res)])
        return Value(self._sbvalue_object.CreateValueFromData(
            '', data, self._sbvalue_object.GetType()))

    def __xor__(self, other):
        res = self.__int__() ^ int(other)
        data = lldb.SBData()
        data.SetDataFromUInt64Array([int(res)])
        return Value(self._sbvalue_object.CreateValueFromData(
            '', data, self._sbvalue_object.GetType()))

    def __lshift__(self, other):
        res = self.__int__() << int(other)
        data = lldb.SBData()
        data.SetDataFromUInt64Array([int(res)])
        return Value(self._sbvalue_object.CreateValueFromData(
            '', data, self._sbvalue_object.GetType()))

    def __rshift__(self, other):
        res = self.__int__() >> int(other)
        data = lldb.SBData()
        data.SetDataFromUInt64Array([int(res)])
        return Value(self._sbvalue_object.CreateValueFromData(
            '', data, self._sbvalue_object.GetType()))

    def __rlshift__(self, other):
        res = int(other) << self.__int__()
        data = lldb.SBData()
        data.SetDataFromUInt64Array([int(res)])
        return Value(self._sbvalue_object.CreateValueFromData(
            '', data, self._sbvalue_object.GetType()))

    def __rrshift__(self, other):
        res = int(other) << self.__int__()
        data = lldb.SBData()
        data.SetDataFromUInt64Array([int(res)])
        return Value(self._sbvalue_object.CreateValueFromData(
            '', data, self._sbvalue_object.GetType()))

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
        return Value(self._sbvalue_object.Cast(gdbtype.sbtype()))

    def dereference(self):
        sbtype = self._sbvalue_object.GetType()
        stripped_sbtype = Type(sbtype).strip_typedefs().sbtype()
        stripped_sbval = self._sbvalue_object.Cast(stripped_sbtype)
        return Value(stripped_sbval.Dereference())

    def referenced_value(self):
        return Value(self._sbvalue_object.Dereference())

    def string(self, length):
        s = ''
        for i in range(0, length):
            sbaddr = lldb.SBAddress(
                self._sbvalue_object.GetValueAsUnsigned() + i, lldb.target)
            sberr = lldb.SBError()
            ss = str(lldb.target.ReadMemory(sbaddr, 1, sberr))
            s += ss
        return s


def parse_and_eval(expr):
    opts = lldb.SBExpressionOptions()
    sbvalue = lldb.target.EvaluateExpression(expr, opts)
    if sbvalue and sbvalue.IsValid():
        return Value(sbvalue)
    return RuntimeError('Unable to evaluate "%s".', expr)


def lookup_type(name, block=None):
    chunks = name.split('::')
    unscoped_name = chunks[-1]
    typelist = lldb.target.FindTypes(unscoped_name)
    if typelist.GetSize() == 1:
        return Type(typelist.GetTypeAtIndex(0))
    for i in range(0, typelist.GetSize()):
        t = typelist.GetTypeAtIndex(i)
        if t.GetName() == name:
            return Type(t)
    raise RuntimeError('Type "%s" not found.' % name)


def current_objfile():
    return None


def default_visualizer(value):
    for p in pretty_printers:
        pp = p(value)
        if pp:
            return pp
