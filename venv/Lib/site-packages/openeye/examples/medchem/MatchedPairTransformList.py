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
# Utility to load a previously generated MMP index
#  and dump a listing of the transformations derived from matched pairs found
# ---------------------------------------------------------------------------
# MatchedPairTransformList.py index_file
#
# index_file: filename of MMP index
#############################################################################
from __future__ import print_function
from openeye import oechem
from openeye import oemedchem
import sys

# simple statistics
import math


def average(x):
    return (sum(x) * 1.0 / len(x))


def variance(x):
    return list(map(lambda y: (y - average(x)) ** 2, x))


def stddev(x):
    return math.sqrt(average(variance(x)))


def cmp(x, y):
    """
    Replacement for built-in function cmp that was removed in Python 3

    Compare the two objects x and y and return an integer according to
    the outcome. The return value is negative if x < y, zero if x == y
    and strictly positive if x > y.
    """

    return (x > y) - (x < y)


class MMPXform:
    def __init__(self, xform, avg, std, num):
        self.xform = xform
        self.avg = avg
        self.std = std
        self.num = num

    def __cmp__(self, other):
        return cmp(self.avg, other.avg)


def MMPTransformList(itf):

    # check MMP index
    mmpimport = itf.GetString("-mmpindex")
    if not oemedchem.OEIsMatchedPairAnalyzerFileType(mmpimport):
        oechem.OEThrow.Fatal('Not a valid matched pair index input file, {}'.format(mmpimport))

    # load MMP index
    mmp = oemedchem.OEMatchedPairAnalyzer()
    if not oemedchem.OEReadMatchedPairAnalyzer(mmpimport, mmp):
        oechem.OEThrow.Fatal("Unable to load index {}".format(mmpimport))

    if not mmp.NumMols():
        oechem.OEThrow.Fatal('No records in loaded MMP index file: {}'.format(mmpimport))

    if not mmp.NumMatchedPairs():
        oechem.OEThrow.Fatal('No matched pairs found in MMP index file, ' +
                             'use -fragGe,-fragLe options to extend indexing range')

    # request a specific context for the transform activity, here 0-bonds
    chemctxt = oemedchem.OEMatchedPairContext_Bond0
    askcontext = itf.GetString("-context")[:1]
    if askcontext == '0':
        chemctxt = oemedchem.OEMatchedPairContext_Bond0
    elif askcontext == '1':
        chemctxt = oemedchem.OEMatchedPairContext_Bond1
    elif askcontext == '2':
        chemctxt = oemedchem.OEMatchedPairContext_Bond2
    elif askcontext == '3':
        chemctxt = oemedchem.OEMatchedPairContext_Bond3
    elif askcontext == 'a' or askcontext == 'A':
        chemctxt = oemedchem.OEMatchedPairContext_AllBonds
    else:
        oechem.OEThrow.Fatal("Invalid context specified: " +
                             askcontext + ", only 0|1|2|3|A allowed")

    bPrintTransforms = itf.GetBool("-printlist")
    # if a data field was specified, retrieve the SD data field name
    field = None
    if itf.HasString("-datafield"):
        field = itf.GetString("-datafield")

    if not bPrintTransforms and field is None:
        oechem.OEThrow.Info('Specify one of -datafield or -printlist, otherwise nothing to do!')
        return

    extractOptions = oemedchem.OEMatchedPairTransformExtractOptions()
    # specify amount of chemical context at the site of the substituent change
    extractOptions.SetContext(chemctxt)
    # controls how transforms are extracted (direction and allowed properties)
    extractOptions.SetOptions(oemedchem.OEMatchedPairTransformExtractMode_Sorted |
                              oemedchem.OEMatchedPairTransformExtractMode_NoSMARTS)

    # walk the transforms from the indexed matched pairs
    xforms = []

    xfmidx = 0
    for mmpxform in oemedchem.OEMatchedPairGetTransforms(mmp, extractOptions):
        xfmidx += 1
        if bPrintTransforms:
            print("{0:2} {1}".format(xfmidx, mmpxform.GetTransform()))

        # compute delta property
        mmpidx = 0
        prop = []
        for mmppair in mmpxform.GetMatchedPairs():
            mmpidx += 1
            mmpinfo = "\t{0:2}: ({1:2},{2:2})".format(mmpidx,
                                                      mmppair.FromIndex(),
                                                      mmppair.ToIndex())
            for tag in mmppair.GetDataTags():
                mmpinfo = mmpinfo + " {0}=({1},{2})".format(tag,
                                                            mmppair.GetFromSDData(tag),
                                                            mmppair.GetToSDData(tag))
                if tag == field:
                    fromData = None
                    toData = None
                    try:
                        fromData = float(mmppair.GetFromSDData(tag))
                    except ValueError:
                        fromData = None
                    try:
                        toData = float(mmppair.GetToSDData(tag))
                    except ValueError:
                        toData = None
                    if fromData is not None and toData is not None:
                        prop.append(toData - fromData)

            if bPrintTransforms:
                print(mmpinfo)

        # skip if property not found
        if len(prop):
            xforms.append(MMPXform(mmpxform, average(prop), stddev(prop), len(prop)))

    if not field:
        return 0

    if field and not len(xforms):
        oechem.OEThrow.Error("No matched pairs found with {} data".format(field))

    print("")
    print("*** Transforms sorted by delta ({})".format(field))

    xforms.sort(key=lambda c: -abs(float(c.avg)))
    idx = 0
    for xfm in xforms:
        idx += 1
        if (extractOptions.GetOptions() &
                oemedchem.OEMatchedPairTransformExtractMode_NoSMARTS) != 0:
            # not 'invertable' if SMARTS qualifiers were applied
            if xfm.avg < 0.:
                xfm.avg = -1. * xfm.avg
                xfm.xform.Invert()
        print("{0:2} {2}=(avg={3:.2f},stdev={4:.2f},num={5}) {1}".format(idx,
                                                                         xfm.xform.GetTransform(),
                                                                         field,
                                                                         xfm.avg,
                                                                         xfm.std,
                                                                         xfm.num))


############################################################
InterfaceData = """
# matchedpairtransformlist interface file
!BRIEF -mmpindex index.mmpidx [ -datafield sdDataField ]
!CATEGORY MatchedPairTransformList

    !CATEGORY I/O
        !PARAMETER -mmpindex 1
          !TYPE string
          !REQUIRED true
          !BRIEF Input filename of serialized matched pair index to load
        !END
    !END

    !CATEGORY options
        !PARAMETER -context 1
           !ALIAS -c
           !TYPE string
           !DEFAULT 0
           !BRIEF chemistry context to use for the transformation [0|1|2|3|A]
        !END

        !PARAMETER -printlist 2
           !ALIAS -p
           !TYPE bool
           !DEFAULT 1
           !BRIEF print all transforms and matched pairs
        !END

        !PARAMETER -datafield 3
           !ALIAS -d
           !TYPE string
           !BRIEF sort transforms based on delta change in this property
        !END
    !END
!END
"""


def main(argv=[__name__]):
    itf = oechem.OEInterface(InterfaceData)
    if not oechem.OEParseCommandLine(itf, argv):
        oechem.OEThrow.Fatal("Unable to interpret command line!")

    MMPTransformList(itf)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
