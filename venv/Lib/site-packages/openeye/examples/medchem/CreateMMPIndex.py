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
# Utility to perform a matched pair analysis on a set of structures
#  and save the index for subsequent analysis
# ---------------------------------------------------------------------------
# CreateMMPIndex.py index_mols output_index
#
# index_mols: filename of input molecules to analyze
# output_index: filename of MMP index
#############################################################################
from __future__ import print_function

from openeye import oechem
from openeye import oemedchem
import sys


class FilterSDData:
    def __init__(self, fields, asFloating):
        if len(fields) == 1 and '-ALLSD' in fields[0].upper():
            self.fields = None
        elif len(fields) == 1 and '-CLEARSD' in fields[0].upper():
            self.fields = []
        else:
            self.fields = fields
        self.asFloating = asFloating

    def FilterMolData(self, mol):
        if not oechem.OEHasSDData(mol):
            return 0

        if self.fields is None:
            return -1

        if len(self.fields) == 0:
            oechem.OEClearSDData(mol)
            return 0

        validdata = 0
        deletefields = []
        for dp in oechem.OEGetSDDataPairs(mol):
            tag = dp.GetTag()
            if tag not in self.fields:
                deletefields.append(tag)
                continue

            value = oechem.OEGetSDData(mol, tag)
            if self.asFloating:
                try:
                    float(value)
                except ValueError:
                    oechem.OEThrow.Warning("Failed to convert %s to numeric value (%s) in %s" %
                                           (tag, value, mol.GetTitle()))
                    deletefields.append(tag)
                    continue

            validdata += 1

        if not validdata:
            oechem.OEClearSDData(mol)
        else:
            for nuke in deletefields:
                oechem.OEDeleteSDData(mol, nuke)

        return validdata


def MMPIndex(itf):
    # output index file
    mmpindexfile = itf.GetString("-output")
    if not oemedchem.OEIsMatchedPairAnalyzerFileType(mmpindexfile):
        oechem.OEThrow.Fatal("Output file is not a matched pair index type - \
                             needs .mmpidx extension: {}"
                             .format(mmpindexfile))

    # create options class with defaults
    mmpopts = oemedchem.OEMatchedPairAnalyzerOptions()
    # set up options from command line
    if not oemedchem.OESetupMatchedPairIndexOptions(mmpopts, itf):
        oechem.OEThrow.Fatal("Error setting matched pair indexing options!")

    # input structures to index
    ifsindex = oechem.oemolistream()
    if not ifsindex.open(itf.GetString("-input")):
        oechem.OEThrow.Fatal("Unable to open {} for reading"
                             .format(itf.GetString("-input")))

    # get requested verbosity setting
    verbose = itf.GetBool("-verbose")
    vverbose = itf.GetBool("-vverbose")
    if vverbose:
        verbose = vverbose

    maxrec = max(itf.GetInt("-maxrec"), 0)
    statusrec = itf.GetInt("-status")

    if itf.GetBool("-exportcompress"):
        if not mmpopts.SetOptions(mmpopts.GetOptions() |
                                  oemedchem.OEMatchedPairOptions_ExportCompression):
            oechem.OEThrow.Warning("Error enabling export compression!")

    stripstereo = itf.GetBool("-stripstereo")
    stripsalts = itf.GetBool("-stripsalts")

    keepFields = []
    if itf.HasString("-keepSD"):
        for field in itf.GetStringList("-keepSD"):
            keepFields.append(field)
        if verbose:
            oechem.OEThrow.Info('Retaining SD data fields: {}'.format(' '.join(keepFields)))

    alldata = itf.GetBool("-allSD")
    cleardata = itf.GetBool("-clearSD")

    if keepFields:
        if verbose and (alldata or cleardata):
            oechem.OEThrow.Info("Option -keepSD overriding -allSD, -clearSD")
        alldata = False
        cleardata = False
    elif cleardata:
        alldata = False
        if verbose:
            oechem.OEThrow.Info("Forced clearing of all input SD data")
    elif alldata:
        if verbose:
            oechem.OEThrow.Info("Retaining all input SD data")
        cleardata = False
    elif verbose:
        oechem.OEThrow.Info("No SD data handling option specified, -allSD assumed")

    if cleardata:
        keepFields = ['-CLEARSD']
    elif alldata or not keepFields:
        keepFields = ['-ALLSD']

    if verbose:
        if not mmpopts.HasIndexableFragmentHeavyAtomRange():
            oechem.OEThrow.Info("Indexing all fragments")
        else:
            oechem.OEThrow.Info("Limiting fragment cores to {0:.2f}-{1:.2f}% of input molecules"
                                .format(mmpopts.GetIndexableFragmentRangeMin(),
                                        mmpopts.GetIndexableFragmentRangeMax()))
        if statusrec:
            oechem.OEThrow.Info("Status output after every {0} records".format(statusrec))
        if maxrec:
            oechem.OEThrow.Info("Indexing a maximum of {0} records".format(maxrec))

        if itf.GetBool("-exportcompress"):
            oechem.OEThrow.Info("Removing singleton index nodes from index")

        if stripstereo:
            oechem.OEThrow.Info("Stripping stereo")

        if stripsalts:
            oechem.OEThrow.Info("Stripping salts")

        if itf.GetBool("-clearSD"):
            oechem.OEThrow.Info("Clearing all input SD data")
        elif alldata:
            oechem.OEThrow.Info("Retaining all input SD data")
        elif keepFields:
            oechem.OEThrow.Info('Retaining floating point SD data fields: {}'
                                .format(''.join(keepFields)))

    # create indexing engine
    mmp = oemedchem.OEMatchedPairAnalyzer(mmpopts)

    # interpret SD fields as floating point data
    validdata = FilterSDData(keepFields, True)

    # add molecules to be indexed
    record = 0
    unindexed = 0
    for mol in ifsindex.GetOEGraphMols():
        if not alldata:
            # filter the input molecule SD data based on allowed fields
            validdata.FilterMolData(mol)

        if stripsalts:
            oechem.OEDeleteEverythingExceptTheFirstLargestComponent(mol)

        if stripstereo:
            oechem.OEUncolorMol(mol,
                                (oechem.OEUncolorStrategy_RemoveAtomStereo |
                                 oechem.OEUncolorStrategy_RemoveBondStereo |
                                 oechem.OEUncolorStrategy_RemoveGroupStereo))

        status = mmp.AddMol(mol, record)
        if status != record:
            unindexed += 1
            if vverbose:
                oechem.OEThrow.Info('Input structure not added to index, record=%d status=%s' %
                                    (record, oemedchem.OEMatchedPairIndexStatusName(status)))
        record += 1
        if maxrec and record >= maxrec:
            break
        if statusrec and (record % statusrec) == 0:
            oechem.OEThrow.Info("Records: {} Indexed: {} Unindexed: {}"
                                .format(record, (record - unindexed), unindexed))

    if not mmp.NumMols():
        oechem.OEThrow.Fatal('No records in index structure file')

    if not mmp.NumMatchedPairs():
        oechem.OEThrow.Fatal('No matched pairs found from indexing, ' +
                             'use -fragGe,-fragLe options to extend indexing range')

    if not oemedchem.OEWriteMatchedPairAnalyzer(mmpindexfile, mmp):
        oechem.OEThrow.Fatal('Error serializing MMP index: {}'
                             .format(mmpindexfile))

    # return some status information
    oechem.OEThrow.Info("Records: {}, Indexed: {}, matched pairs: {:,d}"
                        .format(record,
                                mmp.NumMols(),
                                mmp.NumMatchedPairs()))
    return 0


############################################################
InterfaceData = """
# createmmpindex interface file
!CATEGORY CreateMMPIndex

    !CATEGORY I/O
        !PARAMETER -input 1
          !ALIAS -in
          !TYPE string
          !REQUIRED true
          !BRIEF Input filename of structures to index
          !KEYLESS 1
        !END

        !PARAMETER -output 2
          !ALIAS -out
          !TYPE string
          !REQUIRED true
          !BRIEF Output filename for serialized MMP index
          !KEYLESS 2
        !END
    !END

    !CATEGORY indexing_options
        !PARAMETER -maxrec 1
           !TYPE int
           !DEFAULT 0
           !LEGAL_RANGE 0 inf
           !BRIEF process at most -maxrec records from -input (0: all)
        !END
        !PARAMETER -status 2
           !TYPE int
           !DEFAULT 0
           !LEGAL_RANGE 0 inf
           !BRIEF emit progress information every -status records (0: off)
        !END
        !PARAMETER -exportcompress 3
          !TYPE bool
          !DEFAULT 0
          !BRIEF Whether to remove singleton nodes on export of the MMP index
          !DETAIL
               True indicates no additional structures will be added to the index
        !END
        !PARAMETER -verbose 4
           !TYPE bool
           !DEFAULT 0
           !BRIEF generate verbose output
        !END
        !PARAMETER -vverbose 5
           !TYPE bool
           !DEFAULT 0
           !BRIEF generate very verbose output
        !END
    !END
    !CATEGORY molecule_SDData
        !PARAMETER -allSD 1
           !TYPE bool
           !DEFAULT 0
           !BRIEF retain all input SD data
        !END
        !PARAMETER -clearSD 2
           !TYPE bool
           !DEFAULT 0
           !BRIEF clear all input SD data
        !END
        !PARAMETER -keepSD 3
           !TYPE string
           !LIST true
           !BRIEF list of SD data tags of floating point data to *retain* \
                  for indexing (all other SD data is removed)
        !END
    !END

    !CATEGORY molecule_processing
        !PARAMETER -stripstereo 1
          !TYPE bool
          !DEFAULT 0
          !BRIEF Whether to strip stereo from -input structures
        !END
        !PARAMETER -stripsalts 2
          !TYPE bool
          !DEFAULT 0
          !BRIEF Whether to strip salt fragments from -input structures
        !END
    !END
!END
"""


def main(argv=[__name__]):
    itf = oechem.OEInterface(InterfaceData)
    oemedchem.OEConfigureMatchedPairIndexOptions(itf)

    if not oechem.OEParseCommandLine(itf, argv):
        oechem.OEThrow.Fatal("Unable to interpret command line!")

    MMPIndex(itf)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
