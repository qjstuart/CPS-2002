#!/usr/bin/env python
# (C) 2017 OpenEye Scientific Software Inc. All rights reserved.
#
# TERMS FOR USE OF SAMPLE CODE The software below ("Sample Code") is
# provided to current licensees or subscribers of OpenEye products or
# SaaS offerings (each a "Customer").
# Customer is hereby permitted to use, copy, and modify the Sample Code,
# subject to these terms. OpenEye claims no rights to Customer's
# modifications. Modification of Sample Code is at Customer's sole and
# exclusive risk. Sample Code may require Customer to have a then
# current license or subscription to the applicable OpenEye offering.
# THE SAMPLE CODE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED.  OPENEYE DISCLAIMS ALL WARRANTIES, INCLUDING, BUT
# NOT LIMITED TO, WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. In no event shall OpenEye be
# liable for any damages or liability in connection with the Sample Code
# or its use.
"""
 Test suite for Python Toolkit
 Copyright (C) 1997 - 2015 OpenEye Scientific Software, Inc.
"""

from __future__ import print_function
import os
import sys
import subprocess


def find_executable(exename):
    if (sys.platform.startswith("win") and
            not exename.endswith(".exe") and
            not exename.endswith(".py")):
        exename = exename + ".exe"

    prefix = sys.prefix

    path = os.path.join(prefix, exename)
    if os.path.exists(path):
        return path

    path = os.path.join(prefix, "bin", exename)
    if os.path.exists(path):
        return path

    path = os.path.join(prefix, "Scripts", exename)
    if os.path.exists(path):
        return path

    raise ValueError("Unable to find '%s' in the '%s' directory" % (exename, prefix))


def run_test_suite(argv):
    """
    Run a small suite of tests to test this installation
    """

    pipexe = find_executable('pip')

    cmd = [pipexe]
    if not sys.platform.startswith("win"):
        cmd = [sys.executable, pipexe]

    subprocess.call(cmd + ['install', 'pytest'])
    subprocess.call(cmd + ['install', 'scripttest'])

    pytestexe = find_executable('pytest')

    cmd = [pytestexe]
    if not sys.platform.startswith("win"):
        cmd = [sys.executable, pytestexe]

    subprocess.call(cmd + ['--pyargs', 'openeye.tests', '-q', '-ra'] + argv)

    return 0


if __name__ == '__main__':
    sys.exit(run_test_suite(sys.argv))
