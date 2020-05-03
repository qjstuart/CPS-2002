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

from __future__ import print_function
import os
import sys

try:
    from xmlrpclib import ServerProxy
except ImportError:  # python 3
    from xmlrpc.client import ServerProxy

from openeye import oechem

oepy = os.path.join(os.path.dirname(__file__), "..", "python")
sys.path.insert(0, os.path.realpath(oepy))

InterfaceData = """\
!BRIEF (-debug|-verbose|-info|-warning|-error) [-h] <server:port>
!PARAMETER -host
  !ALIAS -h
  !TYPE string
  !REQUIRED true
  !BRIEF The host whose verbosity level will be changed
  !KEYLESS 1
!END
!PARAMETER -debug
  !ALIAS -d
  !TYPE bool
  !DEFAULT false
  !BRIEF Debug error level
!END
!PARAMETER -verbose
  !ALIAS -v
  !TYPE bool
  !DEFAULT false
  !BRIEF Verbose error level
!END
!PARAMETER -info
  !ALIAS -i
  !TYPE bool
  !DEFAULT false
  !BRIEF Info error level
!END
!PARAMETER -warning
  !ALIAS -w
  !TYPE bool
  !DEFAULT false
  !BRIEF Warning error level
!END
!PARAMETER -error
  !ALIAS -e
  !TYPE bool
  !DEFAULT false
  !BRIEF Unrecoverable error level
!END
"""


def main(argv=[__name__]):
    itf = oechem.OEInterface(InterfaceData, argv)

    levels = {"-debug": (oechem.OEErrorLevel_Debug,   "oechem.OEErrorLevel_Debug"),
              "-verbose": (oechem.OEErrorLevel_Verbose, "oechem.OEErrorLevel_Verbose"),
              "-info": (oechem.OEErrorLevel_Info,    "oechem.OEErrorLevel_Info"),
              "-warning": (oechem.OEErrorLevel_Warning, "oechem.OEErrorLevel_Warning"),
              "-error": (oechem.OEErrorLevel_Error,   "oechem.OEErrorLevel_Error")}

    onFlags = [key for key in levels if itf.GetBool(key)]
    if not onFlags:
        oechem.OEThrow.Fatal("Need specify exactly one error level: " +
                             "|".join(levels.keys()))
    elif len(onFlags) > 1:
        oechem.OEThrow.Fatal("This flags are mutually exclusive: " +
                             "|".join(onFlags))

    level, name = levels[onFlags[0]]

    s = ServerProxy("http://" + itf.GetString("-host"))
    if s.OEThrowSetLevel(level):
        print("oechem.OEThrow.SetLevel(" + name + ") successful")
    else:
        print("oechem.OEThrow.SetLevel(" + name + ") failed")

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
