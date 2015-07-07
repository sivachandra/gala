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

import os
import os.path
import subprocess

import lldb


LOG_FILE_NAME = 'gala-test.log'
GALA_PATH = None


def run_cmd(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    out, err = p.communicate()
    return (p.returncode, out, err)


def errmsg(msg, stdout=None, stderr=None):
    s = '>>> %s\n'
    if stdout:
        s += '>>> stdout: %s\n'
    if stderr:
        s += '>>> stderr: %s\n'
    return s


def log(msg):
    print(msg)


def load_pretty_printers(debugger, script_path, stmt):
    """ Load pretty printers defined in |script_path| into |debugger|.

    The pretty printers are loaded by running the Python statement |stmt|.
    """
    print('Loading pretty-printer script %s ...' % script_path)
    ci = debugger.GetCommandInterpreter()
    result = lldb.SBCommandReturnObject()
    ci.HandleCommand('script import sys', result)
    ci.HandleCommand('script sys.path.append("%s")' % GALA_PATH, result)
    ci.HandleCommand(
        'script sys.path.append("%s")' % (os.path.split(script_path)[0]),
        result)
    ci.HandleCommand('script import gdb', result)
    ci.HandleCommand('script import gdb.printing', result)
    ci.HandleCommand(
        'script import %s' % os.path.split(script_path)[1][:-3], result)
    ci.HandleCommand('script %s' % stmt, result)


class VariableTests(object):
    def __init__(self, var, substrs):
        """ A simple encapsulation of a variable name and the substrings that
        which should appear when it is printed.
        """
        self.var = var
        self.substrs = substrs


def get_line_number_for_str(match_str, src_file):
    with open(src_file) as f:
        lines = f.readlines()
        i = 0
        for l in lines:
            i += 1
            if match_str in l:
                return i
    return -1
