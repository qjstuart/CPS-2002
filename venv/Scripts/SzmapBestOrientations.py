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

# generate szmap points and probe orientations at ligand atoms

import sys
from openeye import oechem
from openeye import oeszmap

InterfaceData = """
!BRIEF SzmapBestOrientations.py [-prob #.#] [-p] <molfile> [-l] <molfile> [-o] <molfile>
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
!PARAMETER -o
  !TYPE string
  !BRIEF Output file for points and probes molecules
  !REQUIRED true
  !KEYLESS 3
!END
!PARAMETER -prob
  !TYPE double
  !DEFAULT 0.5
  !BRIEF Cutoff for cumulative probability of probes
  !REQUIRED false
!END
"""


def GenerateSzmapProbes(oms, cumulativeProb, lig, prot):
    """
    generate multiconf probes and data-rich points at ligand coords
    @rtype : None
    @param oms: output mol stream for points and probes
    @param cumulativeProb: cumulative probability for cutoff of point set
    @param lig: mol defining coordinates for szmap calcs
    @param prot: context mol for szmap calcs (must have charges and radii)
    """

    sz = oeszmap.OESzmapEngine(prot)

    rslt = oeszmap.OESzmapResults()

    points = oechem.OEGraphMol()
    points.SetTitle("points %s" % lig.GetTitle())
    probes = oechem.OEMol()

    coord = oechem.OEFloatArray(3)

    for i, atom in enumerate(lig.GetAtoms()):
        lig.GetCoords(atom, coord)

        if not oeszmap.OEIsClashing(sz, coord):
            oeszmap.OECalcSzmapResults(rslt, sz, coord)

            rslt.PlaceNewAtom(points)

            clear = False
            rslt.PlaceProbeSet(probes, cumulativeProb, clear)

            name = oeszmap.OEGetEnsembleName(oeszmap.OEEnsemble_NeutralDiffDeltaG)
            nddG = rslt.GetEnsembleValue(oeszmap.OEEnsemble_NeutralDiffDeltaG)
            print("%2d (%7.3f, %7.3f, %7.3f): %s = %.3f"
                  % (i, coord[0], coord[1], coord[2], name, nddG))
        else:
            print("%2d (%7.3f, %7.3f, %7.3f): CLASH"
                  % (i, coord[0], coord[1], coord[2]))

    oechem.OEWriteMolecule(oms, points)
    oechem.OEWriteMolecule(oms, probes)


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

    outputFile = itf.GetString("-o")
    oms = oechem.oemolostream()
    if not oms.open(outputFile):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % outputFile)

    GenerateSzmapProbes(oms, itf.GetDouble("-prob"), lig, prot)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
