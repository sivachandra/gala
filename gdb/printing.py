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


# Note that we must register this as `gdb.printing.type_summary_function`, which
# in turn requires us to `script import gdb.printing` in lldbinit. We already
# need lldbinit modifications since we added autoload, though.
def type_summary_function(valobj, internal_dict):
    old_target = gdb.gala_set_current_target(valobj.GetTarget())
    try:
        for p in gdb.pretty_printers:
            pp = p(gdb.Value(valobj.GetNonSyntheticValue()))
            if pp:
                try:
                    summary = str(pp.to_string())
                except:
                    gdb.printing.print_exc(
                        'Error calling "to_string" method of a '
                        'GDB pretty printer.')
                    summary = ''
                if (hasattr(pp, 'display_hint') and
                    pp.display_hint() == 'string'):
                    summary = '"%s"' % summary
                return summary
        raise RuntimeError('Could not find a pretty printer!')
    finally:
        gdb.gala_set_current_target(old_target)

def set_current_target(f):
    '''Decorator that sets the current target for the SBValue being printed.

    lldb supports multiple debuggers and multiple targets, so we need to get
    the right ones from the value we're trying to print.
    '''
    from functools import wraps
    @wraps(f)
    def wrapper(self, *args):
        # Keep the old target so that decorated functions can call other
        # decorated functions and still reset the current target at the end.
        old_target = gdb.gala_set_current_target(self._sbvalue.GetTarget())
        try:
            return f(self, *args)
        finally:
            gdb.gala_set_current_target(old_target)
    return wrapper


def _named_sbvalue(name, v):
    '''Creates an SBValue equivalent to `val`, but with name `name`.

    For a child provider we want to create children with the appropriate name,
    because these value names are shown as keys. However, the SB API doesn't
    provide a way to clone an existing SBValue with a different name. So we use
    CreateValueFromAddress if possible (so that we can call AddressOf() on the
    children values, for example), and fall back to CreateValueFromData if not.
    '''
    if v.GetLoadAddress() != lldb.LLDB_INVALID_ADDRESS:
        return v.CreateValueFromAddress(name, v.GetLoadAddress(), v.GetType())
    else:
        return v.CreateValueFromData(name, v.GetData(), v.GetType())


class GdbPrinterSynthProvider:
    def __init__(self, sbvalue, internal_dict):
        self._sbvalue = sbvalue
        self._pp = None
        self._children = []
        self._children_iterator = None
        self._iter_count = 0
        self.find_pretty_printer()

    @set_current_target
    def find_pretty_printer(self):
        for p in gdb.pretty_printers:
            try:
                self._pp = p(gdb.Value(self._sbvalue))
            except:
                gdb.printing.print_exc(
                    'Error calling into GDB printer "%s".' % p.name)
            if self._pp:
                break
        if not self._pp:
            raise RuntimeError('Could not find a pretty printer!')

    @set_current_target
    def _get_children(self, max_count):
        if len(self._children) >= max_count:
            return
        if not hasattr(self._pp, 'children'):
            return
        if not self._children_iterator:
            try:
                self._children_iterator = self._pp.children()
            except:
                gdb.printing.print_exc('Error calling "children" method of a '
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
            gdb.printing.print_exc(
                'Error iterating over pretty printer children.')

    @set_current_target
    def _get_display_hint(self):
        if hasattr(self._pp, 'display_hint'):
            return self._pp.display_hint()

    @set_current_target
    def num_children(self, max_count):
        if self._get_display_hint() == 'map':
            self._get_children(2 * max_count)
            return min(len(self._children) / 2, max_count)
        else:
            self._get_children(max_count)
            return min(len(self._children), max_count)

    @set_current_target
    def get_child_index(self, name):
        if self._get_display_hint() == 'array':
            try:
                return int(name.lstrip('[').rstrip(']'))
            except:
                raise NameError(
                    'Value does not have a child with name "%s".' % name)

    @set_current_target
    def get_child_at_index(self, index):
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
                    return _named_sbvalue('[%s]' % key_str, val.sbvalue())
                else:
                    data = lldb.SBData()
                    data.SetDataFromUInt64Array([int(val)])
                    return self._sbvalue.CreateValueFromData(
                        '[%s]' % key_str,
                        data,
                        gdb.gala_get_current_target().FindFirstType('int'))
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
                        gdb.gala_get_current_target().FindFirstType('int'))
                else:
                    return _named_sbvalue(c[0], c[1].sbvalue())
        raise IndexError('Child not present at given index.')

    @set_current_target
    def update(self):
        self._children = []
        self._children_iterator = None
        self._iter_count = 0

    @set_current_target
    def has_children(self):
        return hasattr(self._pp, 'children')

    @set_current_target
    def get_value(self):
        return self._sbvalue


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
    if gdb.gala_get_current_debugger().GetCategory(printer.name).IsValid():
        if replace:
            gdb.gala_get_current_debugger().DeleteCategory(printer.name)
        else:
            raise RuntimeError(
                'WARNING: A type category with name "%s" already exists.' %
                printer.name)
    cat = gdb.gala_get_current_debugger().CreateCategory(printer.name)
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
            lldb.SBTypeSummary.CreateWithFunctionName(
                'gdb.printing.type_summary_function', type_options))
        cat.AddTypeSynthetic(
            lldb.SBTypeNameSpecifier(regexp, True),
            lldb.SBTypeSynthetic.CreateWithClassName(
                'gdb.printing.GdbPrinterSynthProvider', type_options))
    cat.SetEnabled(True)
