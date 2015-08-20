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

import pptest
import testutils


session_vars = {
    'gcc_version': None,
    'gcc_version_src_path': None
}


def check_gcc():
    r, _, __ = testutils.run_cmd(['which', 'gcc'])
    return r == 0


def get_gcc_version():
    version = session_vars.get('gcc_version')
    if version:
        return version
    retcode, out, err = testutils.run_cmd(['gcc', '--version'])
    if retcode != 0:
        raise RuntimeError('>>> Unable to get version of GCC:\n'
                           '>>> stdout: %s\n>>> stderr: %s\n' % out, err)
    first_line = out.splitlines()[0]
    closing_paren = first_line.find(')')
    rest_of_line = first_line[closing_paren + 1:]
    version = rest_of_line.split()[0]
    session_vars['gcc_version'] = version
    return version


def get_gcc_version_src_path():
    path = session_vars.get('gcc_version_src_path')
    if path:
        return path
    path = os.path.abspath('gcc-%s' % get_gcc_version())
    session_vars['gcc_version_src_path'] = path
    return path


def get_ppscript_path():
    gcc_path = get_gcc_version_src_path()
    return os.path.join(
        gcc_path, 'libstdc++-v3', 'python', 'libstdcxx', 'v6', 'printers.py')


def download_gcc_src():
    version = get_gcc_version()
    gcc_ftp_path = ('ftp://ftp.gnu.org/gnu/gcc/gcc-%s/gcc-%s.tar.gz' %
                    (version, version))
    retcode, out, err = testutils.run_cmd(['wget', gcc_ftp_path])
    if retcode != 0:
        raise RuntimeError(
            '>>> Unable to download GCC source from "%s".\n'
            '>>> stdout: %s\n>>> stderr: %s\n' % (gcc_ftp_path, out, err))
    testutils.log('Extracting the source from the tarball.')
    retcode, _, __ = testutils.run_cmd(
        ['tar', '-xvf', 'gcc-%s.tar.gz' % version])
    if retcode != 0:
        raise RuntimeError('Unable to untar "gcc-%s.tar.gz".' % version)
    retcode, _, __ = testutils.run_cmd(
        ['rm', '-rf', 'gcc-%s.tar.gz' % version])
    if retcode != 0:
        testutils.log('WARNING: Unable to delete "gcc-%s.tar.gz"' % version)


def get_libstdcxx_tests_from_file(file_path):
    def get_var_strings(l):
        l = l.strip()
        l = l[2:]  # Remove the leading '//'
        l = l.strip()
        l = l[1:]  # Remove the leading '{'
        l = l[:-1] # Remove the trailing '}'
        l = l.strip()
        l = l[len('dg-final'):]
        l = l.strip()
        l = l[1:]  # Remove the leading '{'
        l = l[:-1] # Remove the trailing '}'
        l = l.strip()
        l = l[len('note-test'):]
        l = l.strip()
        var = l[0:l.find(' ')]
        pattern = l[l.find(' '):]
        pattern = pattern.strip()
        if pattern[0] == '{':
            pattern = pattern[1:]  # Remove the leading '{'
            pattern = pattern[:-1] # Remove the trailing '}'
            pattern = pattern.strip()
            summary = pattern[0:pattern.find('=')]
            summary = summary.strip()
            patterns = [summary]
            children = pattern[pattern.find('=') + 1:]
            children = children.strip()
            children = children[1:]  # Remove the leading '{'
            children = children[:-1] # Remove the trailing '}'
            children = children.strip()
            children = [c.strip() for c in children.split(',')]
            patterns.extend(children)
        elif pattern[0] == '"':
            pattern = pattern[1:]  # Remove the leading '"'
            pattern = pattern[:-1] # Remove the trailing '"'
            patterns = [pattern.replace('\\', '')]
        return pptest.VarStrings(var, patterns)

    with open(file_path) as f:
        lines = f.readlines()
    tests = []
    bp_loc = None
    i = 0
    for l in lines:
        i += 1
        if 'note-test' in l:
            tests.append(get_var_strings(l))
        elif 'Mark SPOT' in l:
            bp_loc = i
    if not bp_loc:
        testutils.log('ERROR: Unable to locate where to set breakpoint.')
        testutils.log('       Skipping tests from "%s".' % file_path)
        return 1
    if not tests:
        testutils.log('No tests found in "%s".' % file_path)
        return 0
    ppscript_path = get_ppscript_path()
    return pptest.PrettyPrinterTest(
        'libstdcxx_test_from_' + os.path.split(file_path)[1],
        file_path, 'g++', {bp_loc: tests},
        ppscript_path, 'printers.register_libstdcxx_printers(None)')


def get_libstdcxx_tests():
    if not check_gcc():
        testutils.log(
            'No GCC on the system. Will not run any libstdc++ tests.')
        return []

    gcc_version = get_gcc_version()
    testutils.log('Found gcc-%s on the system' % gcc_version)
    gcc_src_path = get_gcc_version_src_path()
    testutils.log('Checking for GCC source %s' % gcc_src_path)
    if os.path.exists(gcc_src_path):
        testutils.log('GCC source already exists.')
    else:
        testutils.log('GCC source not present. Downloading ...')
        download_gcc_src()
    testsuite_path = os.path.join(
        gcc_src_path, 'libstdc++-v3', 'testsuite', 'libstdc++-prettyprinters')
    files = os.listdir(testsuite_path)
    tests = []
    for f in files:
        if f[-3:] == '.cc':
            path = os.path.join(testsuite_path, f)
            file_tests = get_libstdcxx_tests_from_file(path)
            if file_tests:
                tests.append(file_tests)
    return tests
