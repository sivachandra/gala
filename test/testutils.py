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
