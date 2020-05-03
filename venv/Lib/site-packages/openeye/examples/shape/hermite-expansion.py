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

import sys
from openeye import oechem
from openeye import oeshape
from openeye import oegrid


def main(argv=[__name__]):
    itf = oechem.OEInterface(InterfaceData, argv)

    NPolyMax = itf.GetInt("-NPolyMax")
    gridspacing = itf.GetFloat("-gridspacing")

    ifname = itf.GetString("-inputfile")
    ofname = itf.GetString("-outputgrid")\

    ifs = oechem.oemolistream()
    if (not ifs.open(ifname)):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % ifname)

    if (not ofname.endswith(".grd")):
        oechem.OEThrow.Fatal("Output grid file extension hast to be '.grd' ")

    mol = oechem.OEMol()

    if (not oechem.OEReadMolecule(ifs, mol)):
        oechem.OEThrow.Fatal("Unable to read molecule in %s" % ifname)

    prep = oeshape.OEOverlapPrep()
    prep.SetAssignColor(False)
    prep.Prep(mol)
    transfm = oechem.OETrans()
    oeshape.OEOrientByMomentsOfInertia(mol, transfm)

    hermiteoptions = oeshape.OEHermiteOptions()
    hermiteoptions.SetNPolyMax(NPolyMax)
    hermiteoptions.SetUseOptimalLambdas(True)

    hermite = oeshape.OEHermite(hermiteoptions)

    if (not hermite.Setup(mol)):
        oechem.OEThrow.Fatal("Was not able to Setup the molecule for the OEHermite class.")

    hopts = hermite.GetOptions()
    print("Best lambdas found X=" + str(hopts.GetLambdaX()) + "  Y="
          + str(hopts.GetLambdaY()) + "  Z=" + str(hopts.GetLambdaZ()))

    print("Hermite self-overlap=", hermite.GetSelfOverlap())

    basis_size = int((NPolyMax+1)*(NPolyMax+2)*(NPolyMax+3)/6)
    coeffs = oechem.OEDoubleVector(basis_size)
    hermite.GetCoefficients(coeffs)
    NPolyMaxstring = str(NPolyMax)
    print("Hermite coefficients f_{l,m,n} in the following order l = 0..."
          + NPolyMaxstring + ", m = 0..." + NPolyMaxstring+"-l, n = " + NPolyMaxstring + "-l-m :")

    for x in coeffs:
        print(str(x) + " "),

    grid = oegrid.OEScalarGrid()

    hermite.CreateGrid(grid, gridspacing)

    if (not oegrid.OEWriteGrid(ofname, grid)):
        oechem.OEThrow.Fatal("Unable to write grid file")

    return 0


#############################################################################
InterfaceData = '''
!BRIEF [-inputfile] <InputFileName> [-outputgrid] <OutputGridFileName> [-NPolyMax] <NPolyMax> \
[-numgridpoints] <numgridpoints> [-gridspacing] <gridspacing>

!CATEGORY "input/output options :" 1

  !PARAMETER -inputfile 1
    !ALIAS -in
    !TYPE string
    !REQUIRED true
    !BRIEF Filename of the input molecule
    !KEYLESS 1
  !END

  !PARAMETER -outputgrid 2
  !ALIAS -out
    !TYPE string
    !REQUIRED true
    !BRIEF Filename of the output Hermite grid (needs to have .grd file extension)
    !KEYLESS 2
  !END

!END

!CATEGORY "Hermite options :" 2

  !PARAMETER -NPolyMax 3
    !ALIAS -NP
    !TYPE int
    !REQUIRED false
    !DEFAULT 5
    !LEGAL_RANGE 0 30
    !BRIEF Resolution parameter of Hermite Prep
    !KEYLESS 3
  !END


  !PARAMETER -gridspacing 4
    !ALIAS -gs
    !TYPE float
    !REQUIRED false
    !DEFAULT 1.0
    !LEGAL_RANGE 0.01 10.0
    !BRIEF Grid spacing of the output Hermite grid
    !KEYLESS 4
  !END

!END
'''

#############################################################################
if __name__ == "__main__":
    sys.exit(main(sys.argv))
