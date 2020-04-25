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
from openeye import oeiupac


def Mol2Nam(itf):
    ifs = oechem.oemolistream()
    if not ifs.open(itf.GetString("-in")):
        oechem.OEThrow.Fatal("Unable to open '%s' for reading" % itf.GetString("-in"))

    ofs = oechem.oemolostream()
    outname = None
    if itf.HasString("-out"):
        outname = itf.GetString("-out")
        if not ofs.open(outname):
            oechem.OEThrow.Fatal("Unable to open '%s' for reading" % outname)

    language = oeiupac.OEGetIUPACLanguage(itf.GetString("-language"))
    charset = oeiupac.OEGetIUPACCharSet(itf.GetString("-encoding"))
    style = oeiupac.OEGetIUPACNamStyle(itf.GetString("-style"))

    for mol in ifs.GetOEGraphMols():
        name = oeiupac.OECreateIUPACName(mol, style)

        if language > 0:
            name = oeiupac.OEToLanguage(name, language)
        if itf.GetBool("-capitalize"):
            name = oeiupac.OECapitalizeName(name)

        if charset == oeiupac.OECharSet_ASCII:
            name = oeiupac.OEToAscii(name)
        elif charset == oeiupac.OECharSet_UTF8:
            name = oeiupac.OEToUTF8(name)
        elif charset == oeiupac.OECharSet_HTML:
            name = oeiupac.OEToHTML(name)
        elif charset == oeiupac.OECharSet_SJIS:
            name = oeiupac.OEToSJIS(name)
        elif charset == oeiupac.OECharSet_EUCJP:
            name = oeiupac.OEToEUCJP(name)

        if outname:
            if itf.HasString("-delim"):
                title = mol.GetTitle()
                name = title + itf.GetString("-delim") + name

            if itf.HasString("-tag"):
                oechem.OESetSDData(mol, itf.GetString("-tag"), name)

            mol.SetTitle(name)
            oechem.OEWriteMolecule(ofs, mol)

        else:
            print(name)


############################################################
InterfaceData = """
# mol2nam interface file
!CATEGORY mol2nam

    !CATEGORY I/O
        !PARAMETER -in 1
          !ALIAS -i
          !TYPE string
          !REQUIRED true
          !BRIEF Input filename
          !KEYLESS 1
        !END

        !PARAMETER -out 2
          !ALIAS -o
          !TYPE string
          !BRIEF Output filename
          !KEYLESS 2
        !END
    !END

    !CATEGORY Lexichem Features

        !PARAMETER -language 1
           !ALIAS -lang
           !TYPE string
           !DEFAULT american
           !LEGAL_VALUE american
           !LEGAL_VALUE english
           !LEGAL_VALUE us

           !LEGAL_VALUE british
           !LEGAL_VALUE uk

           !LEGAL_VALUE chinese
           !LEGAL_VALUE zh
           !LEGAL_VALUE cn

           !LEGAL_VALUE danish
           !LEGAL_VALUE dk
           !LEGAL_VALUE da

           !LEGAL_VALUE dutch
           !LEGAL_VALUE nl

           !LEGAL_VALUE french
           !LEGAL_VALUE fr

           !LEGAL_VALUE german
           !LEGAL_VALUE de

           !LEGAL_VALUE greek
           !LEGAL_VALUE el

           !LEGAL_VALUE hungarian
           !LEGAL_VALUE hu

           !LEGAL_VALUE irish
           !LEGAL_VALUE ie
           !LEGAL_VALUE ga

           !LEGAL_VALUE italian
           !LEGAL_VALUE it

           !LEGAL_VALUE japanese
           !LEGAL_VALUE jp
           !LEGAL_VALUE ja

           !LEGAL_VALUE polish
           !LEGAL_VALUE pl

           !LEGAL_VALUE portuguese
           !LEGAL_VALUE pt

           !LEGAL_VALUE romanian
           !LEGAL_VALUE ro

           !LEGAL_VALUE russian
           !LEGAL_VALUE ru

           !LEGAL_VALUE slovak
           !LEGAL_VALUE sk

           !LEGAL_VALUE spanish
           !LEGAL_VALUE es

           !LEGAL_VALUE swedish
           !LEGAL_VALUE se
           !LEGAL_VALUE sv

           !LEGAL_VALUE welsh
           !LEGAL_VALUE cy

           !REQUIRED false
           !BRIEF Language for output names.
        !END

        !PARAMETER -style 2
            !ALIAS -namestyle
            !TYPE string
            !DEFAULT openeye
            !LEGAL_VALUE openeye
            !LEGAL_VALUE iupac
            !LEGAL_VALUE cas
            !LEGAL_VALUE traditional
            !LEGAL_VALUE systematic
            !LEGAL_VALUE casindex
            !LEGAL_VALUE casidx
            !LEGAL_VALUE autonom
            !LEGAL_VALUE iupac79
            !LEGAL_VALUE iupac93
            !LEGAL_VALUE acdname
            !BRIEF Style of output names
        !END

        !PARAMETER -capitalize 3
           !ALIAS -capitalise
           !TYPE bool
           !DEFAULT false
           !BRIEF Capitalize output names.
        !END

        !PARAMETER -tag 4
           !TYPE string
           !REQUIRED false
           !BRIEF Set name as SD data with tag
        !END

        !PARAMETER -delim 5
           !TYPE string
           !REQUIRED false
           !BRIEF Append name to title using 'delim'
        !END

        !PARAMETER -charset 7
            !ALIAS -encoding
            !TYPE string
            !DEFAULT default
            !REQUIRED false
            !LEGAL_VALUE default
            !LEGAL_VALUE ascii
            !LEGAL_VALUE utf8
            !LEGAL_VALUE html
            !LEGAL_VALUE sjis
            !LEGAL_VALUE eucjp
            !LEGAL_VALUE konsole
            !BRIEF Choose charset/encoding for output names.
        !END

    !END

!END
"""


def main(argv=[__name__]):
    itf = oechem.OEInterface(InterfaceData, argv)
    Mol2Nam(itf)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
