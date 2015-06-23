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

import gdb
import lldb

def type_summary_function(sbvalue, internal_dict):
    for p in gdb.pretty_printers:
        pp = p(gdb.Value(sbvalue.GetNonSyntheticValue()))
        if pp:
            summary = str(pp.to_string())
            if pp.display_hint() == 'string':
                summary = '"%s"' % summary
            return summary
    raise RuntimeError('Could not find a pretty printer!')


class GdbPrinterSynthProvider(object):
    def __init__(self, sbvalue, internal_dict):
        self._sbvalue = sbvalue
        self._pp = None
        self._children = []
        for p in gdb.pretty_printers:
            self._pp = p(gdb.Value(self._sbvalue))
            if self._pp:
                break
        if not self._pp:
            raise RuntimeError('Could not find a pretty printer!')

    def num_children(self):
        if hasattr(self._pp, 'children') and (not self._children):
            children = self._pp.children()
            for c in children:
                self._children.append(c)
        return len(self._children)

    def get_child_index(self, name):
        try:
            return int(name.lstrip('[').rstrip(']'))
        except:
            return -1

    def get_child_at_index(self, index):
        assert hasattr(self._pp, 'children')
        if not self._children:
            children = self._pp.children()
            for c in children:
                self._children.append(c)
        if index < len(self._children):
            c = self._children[index]
            if not isinstance(c[1], gdb.Value):
                data = lldb.SBData()
                data.SetDataFromUInt64Array([int(c[1])])
                return self._sbvalue.CreateValueFromData(
                    c[0], data, lldb.target.FindFirstType('int'))
            else:
                return c[1].sbvalue().CreateChildAtOffset(
                    c[0], 0, c[1].sbvalue().GetType())
            return sbvalue
        raise IndexError('Child not present at given index.')

    def update(self):
        self._children = []

    def has_children(self):
        return hasattr(self._pp, 'children')

    def get_value(self):
        return self._sbvalue


def register_pretty_printer(obj, printer):
    gdb.pretty_printers.append(printer)
    cat = lldb.debugger.CreateCategory(printer.name)
    for sp in printer.subprinters:
        # Cascade goes through typedefs etc.
        children_options = lldb.eTypeOptionCascade
        summary_options = lldb.eTypeOptionCascade
        if not hasattr(sp, 'children'):
            # If there is no 'children' method to a GDB pretty printer,
            # then hide children.
            summary_options |= lldb.eTypeOptionHideChildren
        cat.AddTypeSummary(
            lldb.SBTypeNameSpecifier('^%s<.+>(( )?&)?$' % sp.name, True),
            lldb.SBTypeSummary.CreateWithFunctionName(
                'gdb.printing.type_summary_function', summary_options))
        if hasattr(sp, 'children'):
            # Add synthetic children only if the GDB pretty printer has the
            # children method.
            cat.AddTypeSynthetic(
                lldb.SBTypeNameSpecifier('^%s<.+>(( )?&)?$' % sp.name, True),
                lldb.SBTypeSynthetic.CreateWithClassName(
                    'gdb.printing.GdbPrinterSynthProvider',
                    children_options))
    cat.SetEnabled(True)
