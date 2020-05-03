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

# Cache custom color atoms onto a molecule to be used by FastROCS

import os
import sys

from openeye import oechem
from openeye import oeshape
from openeye import oefastrocs

oepy = os.path.join(os.path.dirname(__file__), "..", "python")
sys.path.insert(0, os.path.realpath(oepy))

COLOR_FORCE_FIELD = """#
TYPE negative
#
#
PATTERN negative [-]
PATTERN negative [OD1+0]-[!#7D3]~[OD1+0]
PATTERN negative [OD1+0]-[!#7D4](~[OD1+0])~[OD1+0]
#
#
INTERACTION negative negative attractive gaussian weight=1.0 radius=1.0
"""


def main(argv=[__name__]):
    if len(argv) != 3:
        oechem.OEThrow.Usage("%s <input> <output>" % argv[0])

    # input - preserve rotor-offset-compression
    ifs = oechem.oemolistream()
    ihand = ifs.GetBinaryIOHandler()
    ihand.Clear()
    oechem.OEInitHandler(ihand, oechem.OEBRotCompressOpts(), oechem.OEBRotCompressOpts())

    ifname = argv[1]
    if not ifs.open(ifname):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % argv[1])

    # output
    ofname = argv[2]
    oformt = oechem.OEGetFileType(oechem.OEGetFileExtension(ofname))
    if oformt != oechem.OEFormat_OEB:
        oechem.OEThrow.Fatal("Output file format much be OEB")

    ofs = oechem.oemolostream()
    if not ofs.open(ofname):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % ofname)

    iss = oechem.oeisstream(COLOR_FORCE_FIELD)
    cff = oeshape.OEColorForceField()
    if not cff.Init(iss):
        oechem.OEThrow.Fatal("Unable to initialize OEColorForceField")

    dots = oechem.OEDots(10000, 200, "molecules")
    for mol in ifs.GetOEMols():
        oefastrocs.OEPrepareFastROCSMol(mol, cff)

        oechem.OEWriteMolecule(ofs, mol)

        dots.Update()

    dots.Total()
    ofs.close()

    print("Indexing %s" % ofname)
    if not oechem.OECreateMolDatabaseIdx(ofname):
        oechem.OEThrow.Fatal("Failed to index %s" % argv[2])

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
