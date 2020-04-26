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
from openeye import oestats


def main(argv=[__name__]):
    itf = oechem.OEInterface(Interface, argv)
    oechem.OEWriteSettings(itf)

    # Create the Krige object
    krige = oestats.OEMolKrige()

    # Add the training molecules to the Krige
    imstr = oechem.oemolistream(itf.GetString("-train"))
    for mol in imstr.GetOEMols():
        mw = oechem.OECalculateMolecularWeight(mol)
        krige.AddTraining(mol, mw)
    imstr.close()

    # Train the Krige on the molecules we added
    krige.Train()

    # Krige for MW of the test molecules, and compare to actual MW
    imstr.open(itf.GetString("-test"))
    for mol in imstr.GetOEMols():
        result = krige.GetResult(mol)
        if not result.Valid():
            continue
        krigeMW = result.GetResponse()
        print("Krige MW %f, Actual MW %f" % (krigeMW, oechem.OECalculateMolecularWeight(mol)))

    print("Finished")


Interface = """
!PARAMETER -train
  !TYPE string
  !LIST true
  !REQUIRED true
  !LEGAL_VALUE *.oeb.gz
  !LEGAL_VALUE *.sdf.gz
  !LEGAL_VALUE *.oeb
  !LEGAL_VALUE *.sdf
  !BRIEF Training molecules for the krige
!END

!PARAMETER -test
  !TYPE string
  !REQUIRED true
  !BRIEF Input molecules to predict
!END


"""


if __name__ == "__main__":
    sys.exit(main(sys.argv))
