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

import functools
import re
import sys
import traceback
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional


# Type aliases for different lldb and gdb callable types.
GdbMakePrinterFunc = Callable[[gdb.Value], 'PrettyPrinter']
LldbSummaryFunc = Callable[[lldb.SBValue, Dict], str]
GdbTypeCallback = Callable[[gdb.Type], bool]
LldbTypeCallback = Callable[[lldb.SBType, Dict], bool]
# lldb doesn't document what's in an internal_dict, and it's internal, so we
# treat the actual types in the dict as an opaque implementation detail.
LldbInternalDict = Dict
# TODO: Find a better definition for these.
LldbChildProvider = Any
GdbObjectFile = Any


def _print_exc(err_msg: str):
    """Prints the current exception with `err_msg`."""
    print('<<< %s >>>' % err_msg)
    traceback.print_exc()
    print('<<< --- >>>')


def _object_name(obj: Any) -> Optional[str]:
    """Returns a user-readable name for an object."""
    if hasattr(obj, 'name'):
        return obj.name
    elif hasattr(obj, '__name__'):
        return obj.__name__
    elif hasattr(obj, '__class__'):
        # class instances don't have a __name__, but we can get their class.
        return obj.__class__.__name__
    else:
        return None


_name_count : Dict[str, int] = defaultdict(int)


def _add_attribute_to_current_module(prefix: str, value: Any) -> str:
    """Adds `value` as an attribute of the current module.

    Args:
      prefix: A prefix that will be added to the value name. The final returned
              name can also gave a suffix appended to it for uniqueness.
      value: the value of the new attribute.

    Returns:
      The qualified name of the attribute that was added, so the caller can
      pass it to lldb by name later.
    """
    global _name_count
    current_module = sys.modules[__name__]
    object_name = _object_name(value) or 'unnamed_callback'
    name = f'{prefix}_{object_name}'
    suffix = _name_count[name]
    _name_count[name] += 1
    if suffix > 0:
        name = f'{name}_{suffix}'
    setattr(current_module, name, value)
    return 'gdb.printing.' + name


def _make_lldb_type_callback(f: GdbTypeCallback) -> LldbTypeCallback:
    """Wraps a gdb type predicate into a formatter matching callback in lldb."""
    @functools.wraps(f)
    def wrapped_function(
            sbtype: lldb.SBType, internal_dict: LldbInternalDict) -> bool:
        return f(gdb.Type(sbtype))
    return wrapped_function

def _make_lldb_summary_function(
    make_printer_func: GdbMakePrinterFunc) -> LldbSummaryFunc:
    """Returns an lldb summary function for a given gdb prettyprinter.

    make_printer_func can be a function, or also a class where the constructor
    takes a gdb.Value and returns a prettyprinter object.
    """
    @functools.wraps(make_printer_func)
    def wrapper(sbvalue: lldb.SBValue, internal_dict: LldbInternalDict) -> str:
        old_target = gdb.gala_set_current_target(sbvalue.GetTarget())
        try:
            pp = make_printer_func(gdb.Value(sbvalue.GetNonSyntheticValue()))
            if pp:
                try:
                    summary = str(pp.to_string())
                except:
                    _print_exc(
                        'Error calling "to_string" method of a '
                        'GDB pretty printer.')
                    summary = ''
                if (hasattr(pp, 'display_hint') and
                    pp.display_hint() == 'string'):
                    summary = '"%s"' % summary
                return summary
            raise RuntimeError('Prettyprinter does not match given value.')
        finally:
            gdb.gala_set_current_target(old_target)
    return wrapper


def _set_current_target(method: Callable) -> Callable:
    """Decorator that sets the current target for the SBValue being printed.

    lldb supports multiple debuggers and multiple targets, so we need to get
    the right ones from the value we're trying to print.
    """
    @functools.wraps(method)
    def wrapper(self, *args):
        # Keep the old target so that decorated functions can call other
        # decorated functions and still reset the current target at the end.
        old_target = gdb.gala_set_current_target(self._sbvalue.GetTarget())
        try:
            return method(self, *args)
        finally:
            gdb.gala_set_current_target(old_target)
    return wrapper


def _named_sbvalue(name: str, v: lldb.SBValue) -> lldb.SBValue:
    """Creates an SBValue equivalent to `val`, but with name `name`.

    For a child provider we want to create children with the appropriate name,
    because these value names are shown as keys. However, the SB API doesn't
    provide a way to clone an existing SBValue with a different name. So we use
    CreateValueFromAddress if possible (so that we can call AddressOf() on the
    children values, for example), and fall back to CreateValueFromData if not.
    """
    if v.GetLoadAddress() != lldb.LLDB_INVALID_ADDRESS:
        return v.CreateValueFromAddress(name, v.GetLoadAddress(), v.GetType())
    else:
        return v.CreateValueFromData(name, v.GetData(), v.GetType())

def _make_child_provider_class(
    make_printer_func: GdbMakePrinterFunc) -> LldbChildProvider:
    """Returns an lldb child provider class for a given gdb prettyprinter.

    make_printer_func can be a function, or also a class where the constructor
    takes a gdb.Value and returns a prettyprinter object.
    """

    class Provider:
        def __init__(
                self, sbvalue: lldb.SBValue, internal_dict: LldbInternalDict):
            self._sbvalue = sbvalue
            self._pp = None
            self._children = []
            self._children_iterator = None
            self._iter_count = 0
            self.find_pretty_printer()

        @_set_current_target
        def find_pretty_printer(self):
            try:
                self._pp = make_printer_func(gdb.Value(self._sbvalue))
            except:
                _print_exc(
                    'Error calling into GDB printer "%s".' % p.name)
            if not self._pp:
                raise RuntimeError('Prettyprinter does not match given value.')

        @_set_current_target
        def _get_children(self, max_count: int) -> None:
            if len(self._children) >= max_count:
                return
            if not hasattr(self._pp, 'children'):
                return
            if not self._children_iterator:
                try:
                    self._children_iterator = self._pp.children()
                except:
                    _print_exc(
                        'Error calling "children" on a GDB pretty printer.')
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
                _print_exc(
                    'Error iterating over pretty printer children.')

        @_set_current_target
        def _get_display_hint(self) -> str:
            if hasattr(self._pp, 'display_hint'):
                return self._pp.display_hint()

        @_set_current_target
        def num_children(self, max_count: int) -> int:
            if self._get_display_hint() == 'map':
                self._get_children(2 * max_count)
                return min(len(self._children) // 2, max_count)
            else:
                self._get_children(max_count)
                return min(len(self._children), max_count)

        @_set_current_target
        def get_child_index(self, name: str) -> int:
            if self._get_display_hint() == 'array':
                try:
                    return int(name.lstrip('[').rstrip(']'))
                except:
                    raise NameError(
                        'Value does not have a child with name "%s".' % name)

        @_set_current_target
        def get_child_at_index(self, index: int) -> Optional[lldb.SBValue]:
            # lldb-vscode currently relies on the fact that passing an invalid
            # index to SBValue.GetChildAtIndex "works" (it returns a non-valid
            # SBValue). Asserting here causes scary error messages in the log,
            # so just return None for compatibility.
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
            return None

        @_set_current_target
        def update(self) -> None:
            self._children = []
            self._children_iterator = None
            self._iter_count = 0

        @_set_current_target
        def has_children(self) -> bool:
            return hasattr(self._pp, 'children')

        @_set_current_target
        def get_value(self) -> lldb.SBValue:
            return self._sbvalue

    # Make __name__ the closest possible to the original gdb class name, so we
    # can have an informative display name in the output of `type synth list`.
    Provider.__name__ = _object_name(make_printer_func)
    return Provider


class PrettyPrinter:
    """A base prettyprinter class.

    gdb doesn't require prettyprinter classes to derive from this, but gives
    script authors the option to do so, so we implement it as well.
    """
    def __init__(self, name: str, subprinters : Optional[List] = None):
        self.enabled = True
        self.name = name
        self.subprinters = subprinters

    def __call__(self, val: gdb.Value):
        raise NotImplementedError(
                '__call__ must be defined in the PrettyPrinter subclass')


class SubPrettyPrinter:
    """A base sub-prettyprinter class

    gdb doesn't require prettyprinter classes to derive from this, but gives
    script authors the option to do so, so we implement it as well.
    """
    def __init__(self, name):
        self.name = name
        self.enabled = True


class RegexpCollectionPrettyPrinter(PrettyPrinter):
    """Implements a collection of prettyprinters with regexp matching.

    Unlike gdb's equivalent, this class doesn't do any regex matching. Instead,
    it registers the subprinters directly with lldb in order to use the native
    regex support in lldb.
    """

    # The Subprinter class doesn't have logic of its own. It just stores what's
    # given so that gdb.register_pretty_printer() has the info it needs.
    class Subprinter:
        def __init__(self, name: str, regexp: str,
                     make_printer_func: GdbMakePrinterFunc):
            self.enabled = True
            self.name = name
            self.regexp = regexp
            self.compiled_regexp = re.compile(regexp)
            self.gala_make_printer_function = make_printer_func

    def __init__(self, name: str):
        super(RegexpCollectionPrettyPrinter, self).__init__(name, [])

    def add_printer(self, name: str, regexp: str,
                    make_printer_func: GdbMakePrinterFunc):
        # prepend so lldb precedence order when matching regexes matches gdb.
        self.subprinters.insert(0, self.Subprinter(name, regexp,
                                                   make_printer_func))


# Formatter matching in lldb is less flexible than gdb.
# - gdb has a list of (gdb.Value -> printer) functions. The first
#   function that returns a printer wins.
#
# - lldb has regex matching on type names and, coming soon,
#   (lldb.SBType -> printer) callback matching.
#
# So this register_pretty_printer can't possibly be correctly implemented in
# lldb. However, we support some common cases using the following rules.
#
# 1. The printer object must have a `subprinters` attribute.
#
# 2. The objects in `subprinters` must have one of the following attributes,
#    listed in precedence order.
#
#   - `gala_matching_function`: a function that takes a `gdb.Type` and returns
#     True iff the prettyprinter should be used for that type.
#
#   - `regexp`: we'll pass the regexp as-is to lldb.
#
#   - `name`: as a last resort fallback, if there is a `name` attribute we'll
#     create a regexp based on it (see code below) and use that.
#
# Using existing helper classes like gdb.printing.RegexpCollectionPrettyprinter
# is the easiest way to meet these requirements.
#
# As an optimization, we also look for a `gala_make_printer_func` subprinter
# attribute. For example, the gdb version of RegexpCollectionPrettyPrinter does
# the regex matching in the python lookup function. But in lldb, by the time we
# reach python code we know we already have a regex match, so we can hook up
# the subprinter callback directly to lldb.
def register_pretty_printer(obj: Optional[GdbObjectFile],
                            printer: GdbMakePrinterFunc,
                            replace: bool = False) -> None:
    """Registers a prettyprinter.

    Args:
        obj: ignored. We always register prettyprinters globally.
        printer: something that takes an argument and returns a printer object.
        replace: If True, replace an existing registered printer. If False,
            duplicate printer registration throws an exception.

    Returns:
        Nothing.
    """

    # Default type options for all GALA formatters.
    type_options = (lldb.eTypeOptionCascade |
                    lldb.eTypeOptionSkipPointers |
                    lldb.eTypeOptionSkipReferences |
                    lldb.eTypeOptionHideEmptyAggregates)

    # Create a category named after the printer.
    printer_name = _object_name(printer)
    if not printer_name:
        raise TypeError('Prettyprinter must have a name.')

    if gdb.gala_get_current_debugger().GetCategory(printer_name).IsValid():
        if replace:
            gdb.gala_get_current_debugger().DeleteCategory(printer_name)
        else:
            raise RuntimeError(
                'WARNING: A type category with name "%s" already exists.' %
                printer_name)
    gdb.pretty_printers.append(printer)

    cat = gdb.gala_get_current_debugger().CreateCategory(printer_name)
    cat.SetEnabled(True)

    # Add a pair of (summary, synthetic child provider) for each subprinter.
    for sp in printer.subprinters:
        # First, find the right matching strategy.
        if hasattr(sp, 'gala_matching_function'):
            callback_name = _add_attribute_to_current_module('gala_type_cb',
                    _make_lldb_type_callback(sp.gala_matching_function))
            type_name_specifier = lldb.SBTypeNameSpecifier(
                    callback_name, lldb.eFormatterMatchCallback)
        elif hasattr(sp, 'regexp'):
            type_name_specifier = lldb.SBTypeNameSpecifier(sp.regexp, True)
        else:
            regexp = '^%s(<.+>)?(( )?&)?$' % sp.name
            type_name_specifier = lldb.SBTypeNameSpecifier(regexp, True)

        # Then get the right gdb callable for lldb to call.
        if hasattr(sp, 'gala_make_printer_function'):
          make_printer_function = sp.gala_make_printer_function
        else:
          make_printer_function = printer

        # And register everything with lldb, creating the actual summary
        # provider function and child provider class as wrappers around the
        # gdb prettyprinter object.
        summary_provider = lldb.SBTypeSummary.CreateWithFunctionName(
                _add_attribute_to_current_module('gala_summary',
                        _make_lldb_summary_function(make_printer_function)),
                type_options)
        synth_provider = lldb.SBTypeSynthetic.CreateWithClassName(
                _add_attribute_to_current_module('gala_synth',
                        _make_child_provider_class(make_printer_function)),
                type_options)
        cat.AddTypeSummary(type_name_specifier, summary_provider)
        cat.AddTypeSynthetic(type_name_specifier, synth_provider)
