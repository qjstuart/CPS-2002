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


def main(argv=[__name__]):
    itf = oechem.OEInterface(InterfaceData, argv)

    NPolyMax_MAX = itf.GetInt("-NPolyMax_MAX")

    ifrefname = itf.GetString("-inputreffile")
    iffitname = itf.GetString("-inputfitfile")
    ofname = itf.GetString("-outputfile")

    ifsref = oechem.oemolistream()
    if not ifsref.open(ifrefname):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % ifrefname)

    ifsfit = oechem.oemolistream()
    if not ifsfit.open(iffitname):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % iffitname)

    refmol = oechem.OEMol()

    if not oechem.OEReadMolecule(ifsref, refmol):
        oechem.OEThrow.Fatal("Unable to read molecule in %s" % ifrefname)

    prep = oeshape.OEOverlapPrep()
    prep.SetAssignColor(False)
    prep.Prep(refmol)
    reftransfm = oechem.OETrans()
    oeshape.OEOrientByMomentsOfInertia(refmol, reftransfm)

    hermiteoptionsref = oeshape.OEHermiteOptions()
    hermiteoptionsref.SetNPolyMax(NPolyMax_MAX)
    hermiteoptionsref.SetUseOptimalLambdas(True)

    hermiteoptionsfit = oeshape.OEHermiteOptions()
    hermiteoptionsfit.SetNPolyMax(NPolyMax_MAX)
    hermiteoptionsfit.SetUseOptimalLambdas(True)

    hermitefunc = oeshape.OEHermiteShapeFunc(hermiteoptionsref, hermiteoptionsfit)

    options = oeshape.OEOverlayOptions()
    options.SetOverlapFunc(hermitefunc)
    overlay = oeshape.OEOverlay(options)
    overlay.SetupRef(refmol)

    ofs = oechem.oemolostream()
    if not ofs.open(ofname):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % ofname)

    transfm = oechem.OETrans()
    fitmol = oechem.OEMol()
    while oechem.OEReadMolecule(ifsfit, fitmol):
        prep.Prep(fitmol)
        oeshape.OEOrientByMomentsOfInertia(fitmol, transfm)

        score = oeshape.OEBestOverlayScore()
        overlay.BestOverlay(score, fitmol)
        print("Hermite Tanimoto = ", score.GetTanimoto())

        oechem.OESetSDData(fitmol, "HermiteTanimoto_"+str(NPolyMax_MAX), str(score.GetTanimoto()))
        score.Transform(fitmol)

        # Transform from the inertial frame to the original reference mol frame
        reftransfm.Transform(fitmol)

        oechem.OEWriteMolecule(ofs, fitmol)


#############################################################################
InterfaceData = '''
!BRIEF [-inputreffile] <InputReferenceFileName> [-inputfitfile] <InputFitFileName> \
[-outputfile] <OutputFileName> [-NPolyMax_MAX] <NPolyMax_MAX>

!CATEGORY "input/output options :" 1

  !PARAMETER -inputreffile 1
    !ALIAS -inref
    !TYPE string
    !REQUIRED true
    !BRIEF Input file name with reference molecule (will only read the first molecule).
    !KEYLESS 1
  !END
  !PARAMETER -inputfitfile 2
    !ALIAS -infit
    !TYPE string
    !REQUIRED true
    !BRIEF Input file name with fit molecules
    !KEYLESS 2
  !END
  !PARAMETER -outputfile 3
    !ALIAS -out
    !TYPE string
    !REQUIRED true
    !BRIEF Output file name
    !KEYLESS 3
  !END

!END

!CATEGORY "Hermite options :" 2

  !PARAMETER -NPolyMax_MAX 4
    !ALIAS -NP_MAX
    !TYPE int
    !REQUIRED false
    !DEFAULT 5
    !LEGAL_RANGE 0 30
    !BRIEF Maximum value of the parameter of the NPolyMax parameter of the Hermite prep
    !KEYLESS 4
  !END

!END
'''

#############################################################################
if __name__ == "__main__":
    sys.exit(main(sys.argv))
