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

# Write out a csv file of the similarity matrix of a multi-conformer
# database. Note, all conformers will be compared to each other,
# however, only the best match will be reported between two molecules.

import sys
import os
import csv

from openeye import oechem
from openeye import oefastrocs

oepy = os.path.join(os.path.dirname(__file__), "openeye", "python")
sys.path.insert(0, os.path.realpath(oepy))

InterfaceData = """\
!BRIEF [-shapeOnly] [-dbase] <database> [-matrix] <clusters.csv>
!PARAMETER -dbase
  !TYPE string
  !REQUIRED true
  !BRIEF Input database to select from
  !KEYLESS 1
!END
!PARAMETER -matrix
  !TYPE string
  !REQUIRED true
  !BRIEF csv file to write similarity matrix to
  !KEYLESS 2
!END
!PARAMETER -shapeOnly
  !ALIAS -s
  !TYPE bool
  !DEFAULT false
  !BRIEF Run FastROCS in shape only mode.
!END
"""


def GetScoreGetter(shapeOnly=False):
    if shapeOnly:
        return oefastrocs.OEShapeDatabaseScore.GetShapeTanimoto
    return


def main(argv=[__name__]):
    itf = oechem.OEInterface(InterfaceData, argv)

    ifs = oechem.oemolistream()
    if not ifs.open(itf.GetString("-dbase")):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % itf.GetString("-dbase"))

    colname = "TanimotoCombo"
    getter = oefastrocs.OEShapeDatabaseScore.GetTanimotoCombo
    dbtype = oefastrocs.OEShapeDatabaseType_Default
    if itf.GetBool("-shapeOnly"):
        colname = "ShapeTanimoto"
        getter = oefastrocs.OEShapeDatabaseScore.GetShapeTanimoto
        dbtype = oefastrocs.OEShapeDatabaseType_Shape

    csvwriter = csv.writer(open(itf.GetString("-matrix"), 'w'))
    csvwriter.writerow(["Title1", "Title2", colname])

    shapedb = oefastrocs.OEShapeDatabase(dbtype)
    options = oefastrocs.OEShapeDatabaseOptions()
    options.SetScoreType(dbtype)

    lmat = [[]]
    titles = []
    for mol in ifs.GetOEMols():
        if titles:
            bestscores = [0.0] * len(titles)
            for conf in mol.GetConfs():
                for score in shapedb.GetScores(conf, options):
                    midx = score.GetMolIdx()
                    bestscores[midx] = max(bestscores[midx], getter(score))

            lmat.append(bestscores)

        shapedb.AddMol(mol)

        title = mol.GetTitle()
        if not title:
            title = str(len(titles) + 1)
        titles.append(title)

    # write csv file
    csvwriter = csv.writer(open(itf.GetString("-matrix"), 'w'))
    csvwriter.writerow(titles)
    nrows = len(titles)
    for i in range(nrows):
        row = [i+1]
        for j in range(nrows):
            val = 2.0
            if itf.GetBool("-shapeOnly"):
                val = 1.0

            if j > i:
                val -= lmat[j][i]
            elif j < i:
                val -= lmat[i][j]
            elif j == i:
                val = 0.0

            row.append("%.3f" % val)

        csvwriter.writerow(row)

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
