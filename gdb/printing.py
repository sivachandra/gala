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

import gdb
import gdb.types
import lldb

import re
import traceback

def print_exc(err_msg):
    print('<<< %s >>>' % err_msg)
    traceback.print_exc()
    print('<<< --- >>>')


# We use the same type summary and synthetic child provider logic for all gdb
# pretty printers. They are just a generic layer that interfaces with the gdb
# script that defines the actual pretty printer.
#
# There are two ways this could be done, and this area is very sparsely
# documented, so I'm going to describe some details here:
#
# - SBTypeSummary.CreateWithFunctionName and SBTypeSynthetic.CreateWithClassName
#   would be the "normal" way. However, if we define the function here we must
#   register it with the name "gdb.printing.type_summary_function", and that
#   means we must tell lldb to `script import gdb.printing` in lldbinit, which
#   would be very confusing. The same applies to the synthetic child provider
#   class.
#
# - SBTypeSummary.CreateWithScriptCode and SBTypeSynthetic.CreateWithScriptCode
#   are uglier, but they allow us to sidestep this problem. As long as the
#   GALA `gdb` module is in the PYTHONPATH, scripts will be able to import it
#   and registration will just work.
#
#   SBTypeSummary.CreateWithScriptCode gets the body of a function (that is, NO
#   "def function(...):", that receives the value to be printed as `valobj`.
#
#   SBTypeSynthetic.CreateWithScriptCode gets the body of a class (just the
#   method definitions, no "class MyProvider:") as described in the docs.
type_summary_function_body = """
    import gdb
    for p in gdb.pretty_printers:
        pp = p(gdb.Value(valobj.GetNonSyntheticValue()))
        if pp:
            try:
                summary = str(pp.to_string())
            except:
                print_exc('Error calling "to_string" method of a '
                          'GDB pretty printer.')
                summary = ''
            if hasattr(pp, 'display_hint') and pp.display_hint() == 'string':
                summary = '"%s"' % summary
            return summary
    raise RuntimeError('Could not find a pretty printer!')
"""

synth_provider_class_body = """
    def __init__(self, sbvalue, internal_dict):
        import gdb
        self._sbvalue = sbvalue
        self._pp = None
        self._children = []
        self._children_iterator = None
        self._iter_count = 0
        for p in gdb.pretty_printers:
            try:
                self._pp = p(gdb.Value(self._sbvalue))
            except:
                print_exc('Error calling into GDB printer "%s".' % p.name)
            if self._pp:
                break
        if not self._pp:
            raise RuntimeError('Could not find a pretty printer!')

    def _get_children(self, max_count):
        if len(self._children) >= max_count:
            return
        if not hasattr(self._pp, 'children'):
            return
        if not self._children_iterator:
            try:
                self._children_iterator = self._pp.children()
            except:
                print_exc('Error calling "children" method of a '
                          'GDB pretty printer.')
                return

        try:
            while self._iter_count < max_count:
                try:
                    next_child = next(self._children_iterator)
                except StopIteration:
                    break
                self._children.append(next_child)
                self._iter_count += 1
        except:
            print_exc('Error iterating over pretty printer children.')

    def _get_display_hint(self):
        if hasattr(self._pp, 'display_hint'):
            return self._pp.display_hint()

    def num_children(self, max_count):
        if self._get_display_hint() == 'map':
            self._get_children(2 * max_count)
            return min(len(self._children) / 2, max_count)
        else:
            self._get_children(max_count)
            return min(len(self._children), max_count)

    def get_child_index(self, name):
        if self._get_display_hint() == 'array':
            try:
                return int(name.lstrip('[').rstrip(']'))
            except:
                raise NameError(
                    'Value does not have a child with name "%s".' % name)

    def get_child_at_index(self, index):
        import gdb
        assert hasattr(self._pp, 'children')
        if self._get_display_hint() == 'map':
            self._get_children(2 * (index + 1))
            if index < (len(self._children) / 2):
                key = self._children[index * 2][1]
                val = self._children[index * 2 + 1][1]
                if isinstance(key, gdb.Value):
                    key_str = key.sbvalue().GetSummary()
                    if not key_str:
                        key_str = key.sbvalue().GetValue()
                    if not key_str:
                        key_str = str(key)
                else:
                    key_str = str(key)
                if isinstance(val, gdb.Value):
                    return self._sbvalue.CreateValueFromData(
                        '[%s]' % key_str,
                        val.sbvalue().GetData(), val.sbvalue().GetType())
                else:
                    data = lldb.SBData()
                    data.SetDataFromUInt64Array([int(val)])
                    return self._sbvalue.CreateValueFromData(
                        '[%s]' % key_str,
                        data,
                        lldb.debugger.GetSelectedTarget().FindFirstType('int'))
        else:
            self._get_children(index + 1)
            if index < len(self._children):
                c = self._children[index]
                if not isinstance(c[1], gdb.Value):
                    data = lldb.SBData()
                    data.SetDataFromUInt64Array([int(c[1])])
                    return self._sbvalue.CreateValueFromData(
                        c[0],
                        data,
                        lldb.debugger.GetSelectedTarget().FindFirstType('int'))
                else:
                    return self._sbvalue.CreateValueFromData(
                        c[0],
                        c[1].sbvalue().GetData(), c[1].sbvalue().GetType())
                return sbvalue
        raise IndexError('Child not present at given index.')

    def update(self):
        self._children = []
        self._children_iterator = None
        self._iter_count = 0

    def has_children(self):
        return hasattr(self._pp, 'children')

    def get_value(self):
        return self._sbvalue
"""


class PrettyPrinter:
    def __init__(self, name, subprinters=None):
        self.enabled = True
        self.name = name
        self.subprinters = subprinters

    def __call__(self, val):
        raise NotImplementedError(
                "__call__ must be defined in the PrettyPrinter subclass")

class RegexpCollectionPrettyPrinter(PrettyPrinter):
    # The Subprinter class doesn't do anything special. It just stores what's
    # given so that gdb.register_pretty_printer() has everything it needs.
    class Subprinter:
        def __init__(self, name, regexp, make_printer_func):
            self.enabled = True
            self.name = name
            self.regexp = regexp
            self.compiled_regexp = re.compile(regexp)
            self.make_printer_func = make_printer_func

    def __init__(self, name):
        super(RegexpCollectionPrettyPrinter, self).__init__(name, [])

    def __call__(self, val):
        # Match subprinter regexes and return the right subprinter object.
        typename = gdb.types.get_basic_type(val.type).name
        for sp in self.subprinters:
            if sp.enabled and sp.compiled_regexp.search(typename):
                return sp.make_printer_func(val)

    def add_printer(self, name, regexp, make_printer_func):
        self.subprinters.append(self.Subprinter(name, regexp, make_printer_func))


def register_pretty_printer(obj, printer, replace=False):
    gdb.pretty_printers.append(printer)
    if lldb.debugger.GetCategory(printer.name).IsValid():
        if replace:
            lldb.debugger.DeleteCategory(printer.name)
        else:
            raise RuntimeError(
                'WARNING: A type category with name "%s" already exists.' %
                printer.name)
    cat = lldb.debugger.CreateCategory(printer.name)
    type_options = (lldb.eTypeOptionCascade |
                    lldb.eTypeOptionSkipPointers |
                    lldb.eTypeOptionSkipReferences |
                    lldb.eTypeOptionHideEmptyAggregates)
    for sp in printer.subprinters:
        # lldb needs a regexp to know when to invoke our printer. If we don't
        # have one fall back to matching the printer name.
        regexp = sp.regexp if hasattr(sp, 'regexp') else '^%s(<.+>)?(( )?&)?$' % sp.name
        cat.AddTypeSummary(
            lldb.SBTypeNameSpecifier(regexp, True),
            lldb.SBTypeSummary.CreateWithScriptCode(type_summary_function_body,
                                                    type_options))
        cat.AddTypeSynthetic(
            lldb.SBTypeNameSpecifier(regexp, True),
            lldb.SBTypeSynthetic.CreateWithScriptCode(
                synth_provider_class_body, type_options))
    cat.SetEnabled(True)
