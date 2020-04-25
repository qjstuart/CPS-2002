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

#############################################################################
# Searching fingerprint database
#############################################################################
import sys
from openeye import oechem
from openeye import oegraphsim


def main(argv=[__name__]):

    itf = oechem.OEInterface()
    oechem.OEConfigure(itf, InterfaceData)

    defopts = oegraphsim.OEFPDatabaseOptions(10, oegraphsim.OESimMeasure_Tanimoto)
    oegraphsim.OEConfigureFPDatabaseOptions(itf, defopts)
    oegraphsim.OEConfigureFingerPrint(itf, oegraphsim.OEGetFPType(oegraphsim.OEFPType_Tree))

    if not oechem.OEParseCommandLine(itf, argv):
        return 0

    qfname = itf.GetString("-query")
    mfname = itf.GetString("-molfname")
    ofname = itf.GetString("-out")

    # initialize databases

    timer = oechem.OEWallTimer()
    timer.Start()

    ifs = oechem.oemolistream()
    if not ifs.open(qfname):
        oechem.OEThrow.Fatal("Cannot open input file!")

    query = oechem.OEGraphMol()
    if not oechem.OEReadMolecule(ifs, query):
        oechem.OEThrow.Fatal("Cannot read query molecule!")

    moldb = oechem.OEMolDatabase()
    if not moldb.Open(mfname):
        oechem.OEThrow.Fatal("Cannot open molecule database!")

    ofs = oechem.oemolostream()
    if not ofs.open(ofname):
        oechem.OEThrow.Fatal("Cannot open output file!")

    fptype = oegraphsim.OESetupFingerPrint(itf)
    oechem.OEThrow.Info("Using fingerprint type %s" % fptype.GetFPTypeString())
    fpdb = oegraphsim.OEFPDatabase(fptype)

    emptyfp = oegraphsim.OEFingerPrint()
    emptyfp.SetFPTypeBase(fptype)

    nrmols = moldb.GetMaxMolIdx()

    mol = oechem.OEGraphMol()
    for idx in range(0, nrmols):
        if moldb.GetMolecule(mol, idx):
            fpdb.AddFP(mol)
        else:
            fpdb.AddFP(emptyfp)

    nrfps = fpdb.NumFingerPrints()
    oechem.OEThrow.Info("%5.2f sec to initialize databases" % timer.Elapsed())

    opts = oegraphsim.OEFPDatabaseOptions()
    oegraphsim.OESetupFPDatabaseOptions(opts, itf)

    # search fingerprint database

    timer.Start()
    scores = fpdb.GetSortedScores(query, opts)
    oechem.OEThrow.Info("%5.2f sec to search %d fingerprints" % (timer.Elapsed(), nrfps))

    timer.Start()
    hit = oechem.OEGraphMol()
    for si in scores:
        if moldb.GetMolecule(hit, si.GetIdx()):
            oechem.OEWriteMolecule(ofs, hit)
    oechem.OEThrow.Info("%5.2f sec to write %d hits" % (timer.Elapsed(), opts.GetLimit()))

    return 0


InterfaceData = """
!BRIEF [-query] <molfile> [-molfname] <molfile> [-out] <molfile>

!CATEGORY "input/output options"

  !PARAMETER -query
    !ALIAS -q
    !TYPE string
    !REQUIRED true
    !KEYLESS 1
    !VISIBILITY simple
    !BRIEF Input query filename
  !END

  !PARAMETER -molfname
    !ALIAS -mol
    !TYPE string
    !REQUIRED true
    !KEYLESS 2
    !VISIBILITY simple
    !BRIEF Input molecule filename
  !END

  !PARAMETER -out
    !ALIAS -o
    !TYPE string
    !REQUIRED true
    !KEYLESS 3
    !VISIBILITY simple
    !BRIEF Output molecule filename
  !END

!END
"""

if __name__ == "__main__":
    sys.exit(main(sys.argv))
