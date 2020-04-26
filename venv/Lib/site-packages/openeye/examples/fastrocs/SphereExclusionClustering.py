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

# Shape clustering
from __future__ import print_function
import sys
import os

from openeye import oechem
from openeye import oeshape
from openeye import oefastrocs

oepy = os.path.join(os.path.dirname(__file__), "..", "python")
sys.path.insert(0, os.path.realpath(oepy))


def GetScoreGetter(shapeOnly=False):
    if shapeOnly:
        return oefastrocs.OEShapeDatabaseScore.GetShapeTanimoto
    return oefastrocs.OEShapeDatabaseScore.GetTanimotoCombo


class ShapeCluster:
    def __init__(self, dbname, cutoff, shapeOnly):
        self.cutoff = cutoff

        # set up and options and database based upon shapeOnly
        self.defaultOptions = oefastrocs.OEShapeDatabaseOptions()
        dbtype = oefastrocs.OEShapeDatabaseType_Default
        if shapeOnly:
            dbtype = oefastrocs.OEShapeDatabaseType_Shape

        self.defaultOptions.SetScoreType(dbtype)
        self.shapedb = oefastrocs.OEShapeDatabase(dbtype)
        self.dbmols = []
        volumes = []

        # read in database
        ifs = oechem.oemolistream()
        if not ifs.open(dbname):
            oechem.OEThrow.Fatal("Unable to open '%s'" % dbname)

        count = 0
        for mol in ifs.GetOEGraphMols():
            title = mol.GetTitle()
            if not title:
                title = "Untitled" + str(count)
                mol.SetTitle(title)
                count += 1

            idx = self.shapedb.AddMol(oechem.OEMol(mol))

            volume = oeshape.OEGetCachedSelfShape(mol)
            if volume == 0.0:
                volume = oeshape.OESelfShape(mol)
            volumes.append((volume, idx))

            dbmol = oechem.OEGraphMol(mol, oechem.OEMolBaseType_OEDBMol)
            dbmol.Compress()
            self.dbmols.append(dbmol)

        numMols = len(volumes)

        # find the molecule with the median volume as our first query
        volumes.sort()
        medianVolume, medianIdx = volumes[numMols // 2]

        self.nextClusterHeadIdx = medianIdx
        self.remainingMolecules = numMols

        self.tanimotos = [0.0] * numMols

        self.scoreGetter = GetScoreGetter(shapeOnly)

    def HasRemainingMolecules(self):
        return self.remainingMolecules != 0

    def _removeMolecule(self, idx):
        self.remainingMolecules -= 1

        assert self.dbmols[idx] is not None
        dbmol = self.dbmols[idx]
        dbmol.UnCompress()
        self.dbmols[idx] = None

        assert self.tanimotos[idx] is not None
        self.tanimotos[idx] = sys.float_info.max

        return dbmol

    def GetNextClusterHead(self):
        assert self.nextClusterHeadIdx is not None
        return self._removeMolecule(self.nextClusterHeadIdx)

    def GetCluster(self, query):
        options = oefastrocs.OEShapeDatabaseOptions(self.defaultOptions)

        dots = oechem.OEDots(10000, 200, "molecules searched")

        minTani = sys.float_info.max
        minIdx = None
        for score in self.shapedb.GetScores(query, options):
            idx = score.GetMolIdx()
            # check if already in a cluster
            if self.dbmols[idx] is None:
                continue

            if self.cutoff < self.scoreGetter(score):
                yield self._removeMolecule(idx), score
            else:
                self.tanimotos[idx] = max(self.tanimotos[idx], self.scoreGetter(score))

                minTani, minIdx = min((minTani, minIdx), (self.tanimotos[idx], idx))
            dots.Update()
        dots.Total()

        self.nextClusterHeadIdx = minIdx


InterfaceData = """\
!BRIEF [-shapeOnly] [-cutoff 0.75] [-dbase] <database> [-clusters] <clusters.oeb>
!PARAMETER -dbase
  !TYPE string
  !REQUIRED true
  !BRIEF Input database to select from
  !KEYLESS 1
!END
!PARAMETER -clusters
  !TYPE string
  !REQUIRED true
  !BRIEF Output to write clusters to
  !KEYLESS 2
!END
!PARAMETER -shapeOnly
  !ALIAS -s
  !TYPE bool
  !DEFAULT false
  !BRIEF Run FastROCS in shape only mode.
!END
!PARAMETER -cutoff
  !ALIAS -c
  !TYPE float
  !DEFAULT 0.75
  !BRIEF Number of random pairs to sample.
!END
"""


def main(argv=[__name__]):
    itf = oechem.OEInterface(InterfaceData, argv)

    cutoff = itf.GetFloat("-cutoff")

    ofs = oechem.oemolostream()
    if not ofs.open(itf.GetString("-clusters")):
        oechem.OEThrow.Fatal("Unable to open '%s'" % itf.GetString("-clusters"))

    if ofs.GetFormat() != oechem.OEFormat_OEB:
        oechem.OEThrow.Fatal("Output file must be OEB")

    sdtag = "TanimotoComboFromHead"
    if itf.GetBool("-shapeOnly"):
        sdtag = "ShapeTanimotoFromHead"
    getter = GetScoreGetter(itf.GetBool("-shapeOnly"))

    cluster = ShapeCluster(itf.GetString("-dbase"), cutoff, itf.GetBool("-shapeOnly"))

    # do the clustering
    while cluster.HasRemainingMolecules():
        clusterHead = cluster.GetNextClusterHead()
        print("Searching for neighbors of %s" % clusterHead.GetTitle())

        for nbrMol, score in cluster.GetCluster(clusterHead):
            oechem.OESetSDData(nbrMol, sdtag, "%.4f" % getter(score))

            score.Transform(nbrMol)

            clusterHead.AddData(nbrMol.GetTitle(), nbrMol)

        oechem.OEWriteMolecule(ofs, clusterHead)

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
