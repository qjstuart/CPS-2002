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
import sys

from openeye import oechem
from openeye import oedocking


def main(argv=[__name__]):
    itf = oechem.OEInterface(InterfaceData)
    if not oechem.OEParseCommandLine(itf, argv):
        return 1

    imstr = oechem.oemolistream(itf.GetString("-in"))
    omstr = oechem.oemolostream(itf.GetString("-out"))

    receptor = oechem.OEGraphMol()
    if not oedocking.OEReadReceptorFile(receptor, itf.GetString("-receptor")):
        oechem.OEThrow.Fatal("Unable to read receptor")

    # @ <SNIPPET-POSE-MOLECULES-SETUP>
    poser = oedocking.OEPosit()
    # @ </SNIPPET-POSE-MOLECULES-SETUP>
    # @ <SNIPPET-POSE-MOLECULES-INITIALIZE>
    poser.Initialize(receptor)
    # @ </SNIPPET-POSE-MOLECULES-INITIALIZE>

    for mcmol in imstr.GetOEMols():
        print("posing", mcmol.GetTitle())
        # @ <SNIPPET-POSE-MOLECULES-DOCK>
        result = oedocking.OESinglePoseResult()
        ret_code = poser.Dock(result, mcmol)
        # @ </SNIPPET-POSE-MOLECULES-DOCK>

        # @ <SNIPPET-POSE-MOLECULES-ASSIGN-SCORE>
        if ret_code == oedocking.OEDockingReturnCode_Success:
            posedMol = result.GetPose()
            oedocking.OESetSDScore(posedMol, poser)
        # @ </SNIPPET-POSE-MOLECULES-ASSIGN-SCORE>
            oechem.OEWriteMolecule(omstr, posedMol)
        else:
            errMsg = oedocking.OEDockingReturnCodeGetName(ret_code)
            oechem.OEThrow.Warning("%s: %s" % (mcmol.GetTitle(), errMsg))
    return 0


InterfaceData = """
!PARAMETER -receptor
  !ALIAS -rec
  !TYPE string
  !REQUIRED true
  !LEGAL_VALUE *.oeb
  !LEGAL_VALUE *.oeb.gz
  !BRIEF A receptor file the molecules pass to the -in flag will be posed to
!END

!PARAMETER -in
  !TYPE string
  !REQUIRED true
  !BRIEF Multiconformer file of molecules to be posed.
!END

!PARAMETER -out
  !TYPE string
  !REQUIRED true
  !BRIEF Posed molecules will be written to this file
!END
"""

if __name__ == "__main__":
    sys.exit(main(sys.argv))
