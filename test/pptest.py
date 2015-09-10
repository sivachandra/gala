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
import unittest

import lldb

import testutils


class VarStrings(object):
    def __init__(self, var, substrs):
        self.var = var
        self.substrs = substrs


class PrettyPrinterTest(unittest.TestCase):
    def __init__(self, name, src_file, cc, bp_test_map, ppscript, load_stmt):
        """ Create a pretty printer test object.

        Arguments:
            name - Name of the test.
            src_file - The path to the C/C++ source file to compile.
            cc - Compiler command. For example, to compile with GCC, cc should
                be "gcc". It is assumed here that "gcc" is in path.
            bp_test_map - This is map from breakpoint line numbers to tests that
            ppscript - The path to the script implementing the pretty printers.
            load_stmt - The Python statement which will load the above pretty
                printers.
        """
        unittest.TestCase.__init__(self)
        self.name = name
        self.cc = cc
        self.src_file = src_file
        self.exe_file = os.path.basename(src_file).replace('.', '_') + '__'
        self.bp_test_map = bp_test_map
        self.ppscript = ppscript
        self.load_stmt = load_stmt

    def setUp(self):
        r, out, err = testutils.run_cmd(
            [self.cc, '-g', '-std=c++11', self.src_file, '-o', self.exe_file])
        if r != 0:
            raise RuntimeError(testutils.errmsg(
                'Compiling source file "%s" failed.' % self.src_file))

    def tearDown(self):
        os.remove(self.exe_file)

    def runTest(self):
        testutils.log('Starting pptest "%s" ...' % self.name)
        db = lldb.SBDebugger.Create()
        self.assertTrue(db.IsValid())
        testutils.log('Debugger created successfully...')
        testutils.load_pretty_printers(db, self.ppscript, self.load_stmt)
        db.SetAsync(False)

        target = db.CreateTarget(self.exe_file)
        self.assertTrue(target.IsValid())
        testutils.log('Target "%s" created successfully...' % self.exe_file)
        bp_count = 0
        # TODO: This for loop assumes that the breakpoints in self.bp_test_map
        # are in the order they will be hit. This needs to fixed. For now, if
        # there is only one breakpoint, it works.
        found_failure = False
        for bp_loc in self.bp_test_map:
            bp_count += 1
            bp = target.BreakpointCreateByLocation(self.src_file, bp_loc)
            self.assertTrue(bp.IsValid())
            testutils.log(
                'Breakpoint at %d set in %s...' % (bp_loc, self.src_file))

            if bp_count == 1:
                process = target.LaunchSimple(None, None, os.getcwd())
                self.assertTrue(process.IsValid())
                testutils.log('Process launched successfully...')
            else:
                process.Continue()
                testutils.log('Continuing...')
            self.assertEqual(process.GetState(), lldb.eStateStopped)
            testutils.log('Process stopped...\n')

            var_strings_list = self.bp_test_map[bp_loc]
            for var_strings in var_strings_list:
                testutils.log('Evaluating expression: %s' % var_strings.var)
                val = target.EvaluateExpression(var_strings.var)
                self.assertTrue(val.IsValid())
                testutils.log('Expression evaluated successfully')
                val_str = str(val)
                testutils.log('<expression_evaluation_result>\n' +
                              val_str +
                              '\n</expression_evaluation_result>\n')
                for s in var_strings.substrs:
                    try:
                        self.assertTrue(s in val_str,
                                        '"%s" not found in "%s"' % (s, val_str))
                    except AssertionError as e:
                        testutils.log(str(e))
                        found_failure = True
                frame = process.GetSelectedThread().GetSelectedFrame()
                val = frame.FindVariable(var_strings.var)
                testutils.log('Running "frame var %s"' % var_strings.var)
                self.assertTrue(val.IsValid())
                testutils.log('Looking up frame var successful.')
                val_str = str(val)
                testutils.log('Got value:\n' +
                              '<value>\n' +
                              val_str +
                              '\n</value>\n')
                for s in var_strings.substrs:
                    try:
                        self.assertTrue(s in val_str)
                    except AssertionError as e:
                        testutils.log(str(e))
                        found_failure = True
        process.Continue()
        lldb.SBDebugger.Destroy(db)
        if found_failure:
            self.fail('One or more failures detected in "%s"' % self.name)
