#!/usr/bin/env python
#
# Copyright 2011 Markus Pielmeier
#
# This file is part of tagfs-gui.
#
# tagfs-gui is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# tagfs-gui is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with tagfs-gui.  If not, see <http://www.gnu.org/licenses/>.
#

from distutils.core import setup, Command
import sys
import os
from os.path import (
        basename,
        dirname,
        abspath,
        splitext,
        join as pjoin
)
from glob import glob
from unittest import TestLoader, TextTestRunner

projectDir = dirname(abspath(__file__))
srcDir = pjoin(projectDir, 'src')
modulesDir = pjoin(srcDir, 'modules')
testDir = pjoin(srcDir, 'test')

def printEnv():
    print "..using:"
    print "  modulesDir:", modulesDir
    print "  testDir:", testDir
    print "  sys.path:", sys.path

def setUpTagFsGuiSysPath():
    sys.path.insert(0, modulesDir)
    sys.path.insert(0, testDir)

class AbstractCommand(Command):

    def initialize_options(self):
        self._cwd = os.getcwd()
        self._verbosity = 2

    def finalize_options(self):
        pass

class test(AbstractCommand):
    description = 'run tests'
    user_options = []

    def run(self):
        import re
        testPyMatcher = re.compile('(.*/)?test[^/]*[.]py', re.IGNORECASE)
        
        tests = [splitext(basename(f))[0] for f in glob(pjoin(testDir, '*.py')) if testPyMatcher.match(f)]

        setUpTagFsGuiSysPath()

        printEnv()
        print "  tests:", tests

        # configure logging
        # TODO not sure how to enable this... it's a bit complicate to enable
        # logging only for 'make mt' and disable it then for
        # 'python setup.py test'. 'python setup.py test' is such a gabber...
        #if 'DEBUG' in os.environ:
        #    from tagfs import log_config
        #    log_config.setUpLogging()

        suite = TestLoader().loadTestsFromNames(tests)
        TextTestRunner(verbosity = self._verbosity).run(suite)

class DemoEditGui(AbstractCommand):

    description = 'launch gtagfs-edit demo'
    user_options = []

    def run(self):
        setUpTagFsGuiSysPath()

        printEnv()

        from tagfs_gui import edit
        edit.main([sys.argv[0], pjoin('etc', 'demo', '2008-12-25 - holiday india')])

setup(
    cmdclass = {
        'test': test,
        'demo_gtagfs_edit': DemoEditGui
    },
    name = 'tagfs-gui',
    version = '0.0.1',
    description = 'GUI framework for tagfs tag editors.',
    long_description = '',
    author = 'Markus Pielmeier',
    author_email = 'markus.pielmeier@googlemail.com',
    license = 'GPLv3',
    requires = [],
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python'
    ],
    scripts = [pjoin('src', 'bin', 'gtagfs-edit')],
    packages = ['tagfs_gui'],
    package_dir = {'': pjoin('src', 'modules')}
)
