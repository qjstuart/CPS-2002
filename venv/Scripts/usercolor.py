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

from openeye import oechem
from openeye import oeshape


def main(argv=[__name__]):
    if len(argv) != 3:
        oechem.OEThrow.Usage("%s <reffile> <overlayfile>" % argv[0])

    reffs = oechem.oemolistream(argv[1])
    fitfs = oechem.oemolistream(argv[2])

    refmol = oechem.OEGraphMol()
    oechem.OEReadMolecule(reffs, refmol)

    # Modify ImplicitMillsDean color force field by
    # adding user defined color interactions
    cff = oeshape.OEColorForceField()
    cff.Init(oeshape.OEColorFFType_ImplicitMillsDean)
    cff.ClearInteractions()
    donorType = cff.GetType("donor")
    accepType = cff.GetType("acceptor")
    cff.AddInteraction(donorType, donorType, "gaussian", -1.0, 1.0)
    cff.AddInteraction(accepType, accepType, "gaussian", -1.0, 1.0)

    # Prepare reference molecule for calculation
    # With default options this will add required color atoms
    # Set the modified color force field for addignment
    prep = oeshape.OEOverlapPrep()
    prep.SetColorForceField(cff)
    prep.Prep(refmol)

    # Get appropriate function to calculate exact color
    # Set appropriate options to use the user defined color
    options = oeshape.OEColorOptions()
    options.SetColorForceField(cff)
    colorFunc = oeshape.OEExactColorFunc(options)
    colorFunc.SetupRef(refmol)

    res = oeshape.OEOverlapResults()
    for fitmol in fitfs.GetOEGraphMols():
        prep.Prep(fitmol)
        colorFunc.Overlap(fitmol, res)
        print("Fit Title: %s  Color Tanimoto: %.2f" %
              (fitmol.GetTitle(), res.GetColorTanimoto()))


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))
