#! /usr/bin/python
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

import json
import optparse
import os
import os.path
import sys
import unittest

import pptest
import testutils


def run_tests(tests):
    bad_count = 0
    for test in tests:
        result = unittest.TestResult()
        test.run(result)
        testutils.log('Found %d errors and %d failures.' %
              (len(result.errors), len(result.failures)))
        if result.errors:
            err_count = 0
            for e in result.errors:
                err_count += 1
                testutils.log('ERROR %d:\n%s' % (err_count, e[1]))
            bad_count += err_count
        if result.failures:
            failure_count = 0
            for f in result.failures:
                failure_count += 1
                testutils.log('FAILURE %d:\n%s' % (failure_count, f[1]))
            bad_count += failure_count
    return bad_count


def load_json_tests(json_file):
    """ Load the tests from the file given by the path |json_file|.

    TODO: Document the format of the JSON file.
    """
    json_tests = None
    with open(json_file) as f:
        json_tests = json.load(f)
    if not json_tests:
        testutils.log(
            'Could not load any tests from %s; could be empty.' % json_file)
        return []
    pptests = []
    testutils.log('Loading tests from %s ...' % json_file)
    for json_test in json_tests['pptests']:
        testutils.log('  Loading pptest "%s" ...' % json_test["name"])
        bp_test_map = {}
        for match_str in json_test["bp_test_map"]:
            testutils.log('    Break point marker "%s" ... ' % match_str)
            line_number = testutils.get_line_number_for_str(
                match_str, json_test["src_file"])
            if line_number <= 0:
                continue
            var_tests = []
            for var in json_test["bp_test_map"][match_str]:
                testutils.log('      Loading tests for variable "%s":' % var)
                # Cast the substrings to str type as they could be of unicode
                # type when loaded from JSON.
                substrs = [
                    str(s) for s in json_test["bp_test_map"][match_str][var]]
                testutils.log('        %s' % str(substrs))
                var_tests.append(testutils.VariableTests(str(var), substrs))
            bp_test_map[line_number] = var_tests
        # Bunch of params to the PrettyPrinterTest constructor are "casted" to
        # str# as the string values coming from JSON can be of unicode type but
        # the LLDB API expects strings.
        pptests.append(pptest.PrettyPrinterTest(
            str(json_test["name"]),
            str(json_test["src_file"]),
            str(json_test["cc"]),
            bp_test_map,
            str(json_test["ppscript"]),
            str(json_test["load_stmt"])))
    return pptests


def parse_options():
    parser = optparse.OptionParser()
    parser.add_option('-g', '--gala', dest='gala_path',
                      help="Path to GALA source directory.")
    parser.add_option('-j', '--json', dest='json_file', default=None,
                      help="Path to a JSON file describing tests.")
    options, args = parser.parse_args()
    if not options.gala_path:
        sys.exit('Path to GALA source is required. Use option "--gala".')
    if args:
        sys.exit('Invalid arguments "%s".' % str(args))
    return options


def main():
    options = parse_options()
    testutils.GALA_PATH = options.gala_path
    try:
        os.remove(testutils.LOG_FILE_NAME)
    except:
        pass
    tests = []
    if options.json_file:
        tests.extend(load_json_tests(options.json_file))
    bad_count = run_tests(tests)
    if bad_count > 0:
        sys.exit('Found %d unexpected failures and/or errors.' % bad_count)
    print('Tests completed successfully.')


if __name__ == '__main__':
    main()
