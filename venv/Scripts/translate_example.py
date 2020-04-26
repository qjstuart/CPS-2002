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

# Translates between languages.  Internally LexichemTK uses American
# English so it will convert to/from that as an intermediate
# representation.
#
# By default the program inputs/outputs the internal LexichemTK
# character set representation.  Optionally one can convert the
# input or output to alternate encodings, eg: HTML or UTF8.
#
import sys
from openeye import oechem
from openeye import oeiupac


def Translate(itf):
    ifp = sys.stdin
    if itf.GetString("-in") != "-":
        ifp = open(itf.GetString("-in"))

    if itf.HasString("-out"):
        outname = itf.GetString("-out")
        if outname != "-":
            try:
                ofs = open(outname, 'w')
            except Exception:
                oechem.OEThrow.Fatal("Unable to open '%s' for writing" % outname)
        else:
            ofs = sys.stdout

    from_language = oeiupac.OEGetIUPACLanguage(itf.GetString("-from"))
    to_language = oeiupac.OEGetIUPACLanguage(itf.GetString("-to"))

    from_charset = oeiupac.OEGetIUPACCharSet(itf.GetString("-from_charset"))
    to_charset = oeiupac.OEGetIUPACCharSet(itf.GetString("-to_charset"))

    for name in ifp:
        name = name.strip()

        # Convert from Charset to internal representation
        if from_charset == oeiupac.OECharSet_HTML:
            name = oeiupac.OEFromHTML(name)
        elif from_charset == oeiupac.OECharSet_UTF8:
            name = oeiupac.OEFromUTF8(name)

        # Translation functions all operate on lowercase names
        name = oeiupac.OELowerCaseName(name)

        if from_language != oeiupac.OELanguage_AMERICAN:
            name = oeiupac.OEFromLanguage(name, from_language)

        # At this point the name is American English in the
        # LexichemTK default internal character representation

        # Convert to output language
        if to_language != oeiupac.OELanguage_AMERICAN:
            name = oeiupac.OEToLanguage(name, to_language)

        # Convert to output charset
        if to_charset == oeiupac.OECharSet_ASCII:
            name = oeiupac.OEToAscii(name)
        elif to_charset == oeiupac.OECharSet_UTF8:
            name = oeiupac.OEToUTF8(name)
        elif to_charset == oeiupac.OECharSet_HTML:
            name = oeiupac.OEToHTML(name)
        elif to_charset == oeiupac.OECharSet_SJIS:
            name = oeiupac.OEToSJIS(name)
        elif to_charset == oeiupac.OECharSet_EUCJP:
            name = oeiupac.OEToEUCJP(name)

        ofs.write(name + '\n')


############################################################
InterfaceData = """
# translate interface file
!CATEGORY translate

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
        !DEFAULT -
        !BRIEF Output filename
        !KEYLESS 2
      !END

      !PARAMETER -from 3
         !ALIAS -from_language
         !TYPE string
         !DEFAULT american
         !LEGAL_VALUE american
         !LEGAL_VALUE english
         !LEGAL_VALUE us

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
         !BRIEF Language for input names.
     !END

     !PARAMETER -to 4
         !ALIAS -to_language
         !TYPE string
         !DEFAULT american
         !LEGAL_VALUE american
         !LEGAL_VALUE english
         !LEGAL_VALUE us

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
         !BRIEF Language for input names.
     !END

     !PARAMETER -from_charset 5
         !TYPE string
         !DEFAULT default
         !REQUIRED false
         !LEGAL_VALUE default
         !LEGAL_VALUE ascii
         !LEGAL_VALUE utf8
         !LEGAL_VALUE html
         !LEGAL_VALUE sjis
         !LEGAL_VALUE eucjp
         !BRIEF Choose charset/encoding for input names.
     !END

     !PARAMETER -to_charset 6
         !ALIAS -encoding
         !ALIAS -charset
         !TYPE string
         !DEFAULT default
         !REQUIRED false
         !LEGAL_VALUE default
         !LEGAL_VALUE ascii
         !LEGAL_VALUE utf8
         !LEGAL_VALUE html
         !LEGAL_VALUE sjis
         !LEGAL_VALUE eucjp
         !BRIEF Choose charset/encoding for output names.
     !END


!END
"""


def main(argv=[__name__]):
    itf = oechem.OEInterface(InterfaceData, argv)
    Translate(itf)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
