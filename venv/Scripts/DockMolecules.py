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
    # @ <SNIPPET-DOCK-MOLECULES-CONFIGURE>
    oedocking.OEDockMethodConfigure(itf, "-method")
    oedocking.OESearchResolutionConfigure(itf, "-resolution")
    # @ </SNIPPET-DOCK-MOLECULES-CONFIGURE>
    if not oechem.OEParseCommandLine(itf, argv):
        return 1

    imstr = oechem.oemolistream(itf.GetString("-in"))
    omstr = oechem.oemolostream(itf.GetString("-out"))

    receptor = oechem.OEGraphMol()
    if not oedocking.OEReadReceptorFile(receptor, itf.GetString("-receptor")):
        oechem.OEThrow.Fatal("Unable to read receptor")

    # @ <SNIPPET-DOCK-MOLECULES-GET-VALUE>
    dockMethod = oedocking.OEDockMethodGetValue(itf, "-method")
    dockResolution = oedocking.OESearchResolutionGetValue(itf, "-resolution")
    # @ </SNIPPET-DOCK-MOLECULES-GET-VALUE>
    # @ <SNIPPET-DOCK-MOLECULES-SETUP>
    dock = oedocking.OEDock(dockMethod, dockResolution)
    # @ </SNIPPET-DOCK-MOLECULES-SETUP>
    # @ <SNIPPET-DOCK-MOLECULES-INITIALIZE>
    dock.Initialize(receptor)
    # @ </SNIPPET-DOCK-MOLECULES-INITIALIZE>

    for mcmol in imstr.GetOEMols():
        print("docking", mcmol.GetTitle())
        dockedMol = oechem.OEGraphMol()
        # @ <SNIPPET-DOCK-MOLECULES-DOCK>
        retCode = dock.DockMultiConformerMolecule(dockedMol, mcmol)
        if (retCode != oedocking.OEDockingReturnCode_Success):
            oechem.OEThrow.Fatal("Docking Failed with error code " + oedocking.OEDockingReturnCodeGetName(retCode))

        # @ </SNIPPET-DOCK-MOLECULES-DOCK>
        sdtag = oedocking.OEDockMethodGetName(dockMethod)
        # @ <SNIPPET-DOCK-MOLECULES-ASSIGN-SCORE>
        oedocking.OESetSDScore(dockedMol, dock, sdtag)
        # @ </SNIPPET-DOCK-MOLECULES-ASSIGN-SCORE>
        # @ <SNIPPET-DOCK-MOLECULES-ANNOTATE>
        dock.AnnotatePose(dockedMol)
        # @ </SNIPPET-DOCK-MOLECULES-ANNOTATE>
        oechem.OEWriteMolecule(omstr, dockedMol)

    return 0


InterfaceData = """
!PARAMETER -receptor
  !ALIAS -rec
  !TYPE string
  !REQUIRED true
  !LEGAL_VALUE *.oeb
  !LEGAL_VALUE *.oeb.gz
  !BRIEF A receptor file the molecules pass to the -in flag will be docked to
!END

!PARAMETER -in
  !TYPE string
  !REQUIRED true
  !BRIEF Multiconformer file of molecules to be docked.
!END

!PARAMETER -out
  !TYPE string
  !REQUIRED true
  !BRIEF Docked molecules will be written to this file
!END
"""

if __name__ == "__main__":
    sys.exit(main(sys.argv))
