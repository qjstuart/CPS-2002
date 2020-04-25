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

# Split a multi-conformer database into N chunks keeping molecules
# with the same number of atoms in each chunk. Also caches other
# useful information onto the molecule to improve database load time.

import sys
import os

from openeye import oechem
from openeye import oefastrocs

oepy = os.path.join(os.path.dirname(__file__), "..", "python")
sys.path.insert(0, os.path.realpath(oepy))


def main(argv=[__name__]):
    if len(argv) != 4:
        oechem.OEThrow.Usage("%s <database> <prefix> <n_servers>" % argv[0])

    # input - preserve rotor-offset-compression
    ifs = oechem.oemolistream()
    oechem.OEPreserveRotCompress(ifs)

    ifname = argv[1]
    if not ifs.open(ifname):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % argv[1])

    # output
    prefix = argv[2]
    ext = oechem.OEGetFileExtension(prefix)
    extstrt = len(prefix)
    if ext:
        extstrt = -(len(ext) + 1)
    else:
        ext = oechem.OEGetFileExtension(ifname)
    base = prefix[:extstrt]
    fmt = base + "_%i." + ext

    nservers = int(argv[3])
    outstrms = []
    for i in range(1, nservers + 1):
        ofs = oechem.oemolostream()
        if not ofs.open(fmt % i):
            oechem.OEThrow.Fatal("Unable to open %s for writing" % argv[2])

        outstrms.append(ofs)

    dots = oechem.OEDots(10000, 200, "molecules")
    for mol in ifs.GetOEMols():
        oefastrocs.OEPrepareFastROCSMol(mol)

        nhvyatoms = oechem.OECount(mol, oechem.OEIsHeavy())

        ofs = outstrms[nhvyatoms % nservers]
        oechem.OEWriteMolecule(ofs, mol)

        dots.Update()

    dots.Total()

    for strm in outstrms:
        fname = strm.GetFileName()
        strm.close()
        oechem.OEThrow.Info("Indexing %s" % fname)
        if not oechem.OECreateMolDatabaseIdx(fname):
            oechem.OEThrow.Fatal("Failed to index %s" % fname)

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
