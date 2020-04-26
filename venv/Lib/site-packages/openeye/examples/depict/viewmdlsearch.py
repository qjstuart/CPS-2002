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
# Performs substructure search on a molecule using a MDL query and
# generates an image file depicting one match per molecule.
# The output file format depends on its file extension.
#############################################################################

import sys
from openeye import oechem
from openeye import oedepict


def main(argv=[__name__]):

    itf = oechem.OEInterface(InterfaceData)
    oedepict.OEConfigureReportOptions(itf)
    oedepict.OEConfigure2DMolDisplayOptions(itf)
    oedepict.OEConfigureHighlightParams(itf)

    if not oechem.OEParseCommandLine(itf, argv):
        return 1

    qname = itf.GetString("-query")
    tname = itf.GetString("-target")
    oname = itf.GetString("-out")

    ext = oechem.OEGetFileExtension(oname)
    if not oedepict.OEIsRegisteredMultiPageImageFile(ext):
        oechem.OEThrow.Fatal("Unknown multipage image type!")

    qfile = oechem.oemolistream()
    if not qfile.open(qname):
        oechem.OEThrow.Fatal("Cannot open mdl query file!")
    if qfile.GetFormat() != oechem.OEFormat_MDL and qfile.GetFormat() != oechem.OEFormat_SDF:
        oechem.OEThrow.Fatal("Query file has to be an MDL file!")

    ifs = oechem.oemolistream()
    if not ifs.open(tname):
        oechem.OEThrow.Fatal("Cannot open target input file!")

    depictquery = oechem.OEGraphMol()
    if not oechem.OEReadMDLQueryFile(qfile, depictquery):
        oechem.OEThrow.Fatal("Cannot read query molecule!")
    oedepict.OEPrepareDepiction(depictquery)
    queryopts = oechem.OEMDLQueryOpts_Default | oechem.OEMDLQueryOpts_SuppressExplicitH
    qmol = oechem.OEQMol()
    oechem.OEBuildMDLQueryExpressions(qmol, depictquery, queryopts)

    ss = oechem.OESubSearch()
    if not ss.Init(qmol):
        oechem.OEThrow.Fatal("Cannot initialize substructure search!")

    hstyle = oedepict.OEGetHighlightStyle(itf)
    hcolor = oedepict.OEGetHighlightColor(itf)
    align = itf.GetBool("-align")

    ropts = oedepict.OEReportOptions()
    oedepict.OESetupReportOptions(ropts, itf)
    ropts.SetHeaderHeight(140.0)
    report = oedepict.OEReport(ropts)

    dopts = oedepict.OE2DMolDisplayOptions()
    oedepict.OESetup2DMolDisplayOptions(dopts, itf)
    cellwidth, cellheight = report.GetCellWidth(), report.GetCellHeight()
    dopts.SetDimensions(cellwidth, cellheight, oedepict.OEScale_AutoScale)

    unique = True
    for mol in ifs.GetOEGraphMols():

        oechem.OEPrepareSearch(mol, ss)

        miter = ss.Match(mol, unique)
        if not miter.IsValid():
            continue  # no match

        alignres = oedepict.OEAlignmentResult(miter.Target())
        if align:
            alignres = oedepict.OEPrepareAlignedDepiction(mol, ss)
        else:
            oedepict.OEPrepareDepiction(mol)

        cell = report.NewCell()
        disp = oedepict.OE2DMolDisplay(mol, dopts)
        if alignres.IsValid():
            oedepict.OEAddHighlighting(disp, hcolor, hstyle, alignres)
        oedepict.OERenderMolecule(cell, disp)
        oedepict.OEDrawBorder(cell, oedepict.OELightGreyPen)

    # render query structure in each header
    headwidth, headheight = report.GetHeaderWidth(), report.GetHeaderHeight()
    dopts.SetDimensions(headwidth, headheight, oedepict.OEScale_AutoScale)
    disp = oedepict.OE2DMolDisplay(depictquery, dopts)
    for header in report.GetHeaders():
        oedepict.OERenderMolecule(header, disp)
        oedepict.OEDrawBorder(header, oedepict.OELightGreyPen)

    oedepict.OEWriteReport(oname, report)

    return 0


#############################################################################
# INTERFACE
#############################################################################

InterfaceData = '''
!BRIEF [-query] <input> [-target] <input> [-out] <output multipage image> [-align]

!CATEGORY "input/output options :"

  !PARAMETER -query
    !ALIAS -q
    !TYPE string
    !REQUIRED true
    !KEYLESS 1
    !VISIBILITY simple
    !BRIEF Input query filename
  !END

  !PARAMETER -target
    !ALIAS -t
    !TYPE string
    !REQUIRED true
    !KEYLESS 2
    !VISIBILITY simple
    !BRIEF Input target filename
  !END

  !PARAMETER -out
    !ALIAS -o
    !TYPE string
    !REQUIRED true
    !KEYLESS 3
    !VISIBILITY simple
    !BRIEF Output image filename
  !END

!END

!CATEGORY "general options :"

  !PARAMETER -align
    !TYPE bool
    !REQUIRED false
    !DEFAULT false
    !VISIBILITY simple
    !BRIEF Align hits to query
  !END

!END
'''

if __name__ == "__main__":
    sys.exit(main(sys.argv))
