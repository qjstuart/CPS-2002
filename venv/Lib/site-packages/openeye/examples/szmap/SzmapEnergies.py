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

# analyze binding site energies with szmaptk

import sys
from openeye import oechem
from openeye import oeszmap

InterfaceData = """
!BRIEF SzmapEnergies.py [-p] <molfile> [-l] <molfile>
!PARAMETER -p
  !TYPE string
  !BRIEF Input protein (or other) context mol
  !REQUIRED true
  !KEYLESS 1
!END
!PARAMETER -l
  !TYPE string
  !BRIEF Input ligand coordinates for calculations
  !REQUIRED true
  !KEYLESS 2
!END
!PARAMETER -high_res
  !TYPE bool
  !DEFAULT false
  !BRIEF If true, increase the number of rotations to 360
  !REQUIRED false
!END
"""


def GetSzmapEnergies(lig, prot, highRes):
    """
    run szmap at ligand coordinates in the protein context
    @rtype : None
    @param lig: mol defining coordinates for szmap calcs
    @param prot: context mol for szmap calcs (must have charges and radii)
    @param highRes: if true, use 360 rotations rather than the default of 60
    """

    opt = oeszmap.OESzmapEngineOptions()
    if highRes:
        opt.SetProbe(360)

    sz = oeszmap.OESzmapEngine(prot, opt)
    coord = oechem.OEFloatArray(3)
    rslt = oeszmap.OESzmapResults()

    print("num\tatom\t%s\t%s\t%s\t%s\t%s"
          % (oeszmap.OEGetEnsembleName(oeszmap.OEEnsemble_NeutralDiffDeltaG),
             oeszmap.OEGetEnsembleName(oeszmap.OEEnsemble_PSolv),
             oeszmap.OEGetEnsembleName(oeszmap.OEEnsemble_WSolv),
             oeszmap.OEGetEnsembleName(oeszmap.OEEnsemble_VDW),
             oeszmap.OEGetEnsembleName(oeszmap.OEEnsemble_OrderParam)))

    for i, atom in enumerate(lig.GetAtoms()):
        lig.GetCoords(atom, coord)

        if not oeszmap.OEIsClashing(sz, coord):
            oeszmap.OECalcSzmapResults(rslt, sz, coord)

            print("%2d\t%s\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f"
                  % (i, atom.GetName(),
                     rslt.GetEnsembleValue(oeszmap.OEEnsemble_NeutralDiffDeltaG),
                     rslt.GetEnsembleValue(oeszmap.OEEnsemble_PSolv),
                     rslt.GetEnsembleValue(oeszmap.OEEnsemble_WSolv),
                     rslt.GetEnsembleValue(oeszmap.OEEnsemble_VDW),
                     rslt.GetEnsembleValue(oeszmap.OEEnsemble_OrderParam)))
        else:
            print("%2d\t%s CLASH" % (i, atom.GetName()))


def main(argv=(__name__)):
    """
    the protein should have charges and radii but the ligand need not
    """
    itf = oechem.OEInterface()

    if not oechem.OEConfigure(itf, InterfaceData):
        oechem.OEThrow.Fatal("Problem configuring OEInterface!")

    if not oechem.OEParseCommandLine(itf, argv):
        oechem.OEThrow.Fatal("Unable to parse command line")

    ligFile = itf.GetString("-l")
    ims = oechem.oemolistream()
    if not ims.open(ligFile):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % ligFile)
    lig = oechem.OEGraphMol()
    oechem.OEReadMolecule(ims, lig)

    contextFile = itf.GetString("-p")
    ims = oechem.oemolistream()
    if not ims.open(contextFile):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % contextFile)
    prot = oechem.OEGraphMol()
    oechem.OEReadMolecule(ims, prot)

    highRes = itf.GetBool("-high_res")
    GetSzmapEnergies(lig, prot, highRes)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
