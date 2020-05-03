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
# Depicts the BFactor of a ligand and its environment
#############################################################################

import sys
from openeye import oechem
from openeye import oedepict
from openeye import oegrapheme


def main(argv=[__name__]):

    itf = oechem.OEInterface()
    oechem.OEConfigure(itf, InterfaceData)
    oedepict.OEConfigureImageWidth(itf, 600.0)
    oedepict.OEConfigureImageHeight(itf, 600.0)
    oedepict.OEConfigure2DMolDisplayOptions(itf, oedepict.OE2DMolDisplaySetup_AromaticStyle)
    oechem.OEConfigureSplitMolComplexOptions(itf, oechem.OESplitMolComplexSetup_LigName)

    if not oechem.OEParseCommandLine(itf, argv):
        return 1

    iname = itf.GetString("-complex")
    oname = itf.GetString("-out")

    ifs = oechem.oemolistream()
    if not ifs.open(iname):
        oechem.OEThrow.Fatal("Cannot open input file!")

    ext = oechem.OEGetFileExtension(oname)
    if not oedepict.OEIsRegisteredImageFile(ext):
        oechem.OEThrow.Fatal("Unknown image type!")

    ofs = oechem.oeofstream()
    if not ofs.open(oname):
        oechem.OEThrow.Fatal("Cannot open output file!")

    complexmol = oechem.OEGraphMol()
    if not oechem.OEReadMolecule(ifs, complexmol):
        oechem.OEThrow.Fatal("Unable to read molecule from %s" % iname)

    if not oechem.OEHasResidues(complexmol):
        oechem.OEPerceiveResidues(complexmol, oechem.OEPreserveResInfo_All)

    # Separate ligand and protein

    sopts = oechem.OESplitMolComplexOptions()
    oechem.OESetupSplitMolComplexOptions(sopts, itf)

    ligand = oechem.OEGraphMol()
    protein = oechem.OEGraphMol()
    water = oechem.OEGraphMol()
    other = oechem.OEGraphMol()

    oechem.OESplitMolComplex(ligand, protein, water, other, complexmol, sopts)

    if ligand.NumAtoms() == 0:
        oechem.OEThrow.Fatal("Cannot separate complex!")

    # Calculate average BFactor of the whole complex

    avgbfactor = GetAverageBFactor(complexmol)

    # Calculate minimum and maximum BFactor of the ligand and its environment

    minbfactor, maxbfactor = GetMinAndMaxBFactor(ligand, protein)

    # Attach to each ligand atom the average BFactor of the nearby protein atoms

    stag = "avg residue BFfactor"
    itag = oechem.OEGetTag(stag)
    SetAverageBFactorOfNearbyProteinAtoms(ligand, protein, itag)

    oechem.OEThrow.Info("Average BFactor of the complex = %+.3f" % avgbfactor)
    oechem.OEThrow.Info("Minimum BFactor of the ligand and its environment = %+.3f" % minbfactor)
    oechem.OEThrow.Info("Maximum BFactor of the ligand and its environment = %+.3f" % maxbfactor)

    # Create image

    imagewidth, imageheight = oedepict.OEGetImageWidth(itf), oedepict.OEGetImageHeight(itf)
    image = oedepict.OEImage(imagewidth, imageheight)

    mframe = oedepict.OEImageFrame(image, imagewidth,
                                   imageheight * 0.90, oedepict.OE2DPoint(0.0, 0.0))
    lframe = oedepict.OEImageFrame(image, imagewidth, imageheight * 0.10,
                                   oedepict.OE2DPoint(0.0, imageheight * 0.90))

    opts = oedepict.OE2DMolDisplayOptions(mframe.GetWidth(), mframe.GetHeight(),
                                          oedepict.OEScale_AutoScale)
    oedepict.OESetup2DMolDisplayOptions(opts, itf)
    opts.SetAtomColorStyle(oedepict.OEAtomColorStyle_WhiteMonochrome)

    # Create BFactor color gradient

    colorg = oechem.OELinearColorGradient()
    colorg.AddStop(oechem.OEColorStop(0.0, oechem.OEDarkBlue))
    colorg.AddStop(oechem.OEColorStop(10.0, oechem.OELightBlue))
    colorg.AddStop(oechem.OEColorStop(25.0, oechem.OEYellowTint))
    colorg.AddStop(oechem.OEColorStop(50.0, oechem.OERed))
    colorg.AddStop(oechem.OEColorStop(100.0, oechem.OEDarkRose))

    # Prepare ligand for depiction

    oegrapheme.OEPrepareDepictionFrom3D(ligand)
    arcfxn = BFactorArcFxn(colorg, itag)
    for atom in ligand.GetAtoms():
        oegrapheme.OESetSurfaceArcFxn(ligand, atom, arcfxn)
    opts.SetScale(oegrapheme.OEGetMoleculeSurfaceScale(ligand, opts))

    # Render ligand and visualize BFactor

    disp = oedepict.OE2DMolDisplay(ligand, opts)
    colorbfactor = ColorLigandAtomByBFactor(colorg)
    oegrapheme.OEAddGlyph(disp, colorbfactor, oechem.OEIsTrueAtom())
    oegrapheme.OEDraw2DSurface(disp)
    oedepict.OERenderMolecule(mframe, disp)

    # Draw color gradient

    opts = oegrapheme.OEColorGradientDisplayOptions()
    opts.SetColorStopPrecision(1)
    opts.AddMarkedValue(avgbfactor)
    opts.SetBoxRange(minbfactor, maxbfactor)

    oegrapheme.OEDrawColorGradient(lframe, colorg, opts)

    oedepict.OEWriteImage(oname, image)

    return 0

#############################################################################
#
#############################################################################


def GetAverageBFactor(mol):

    sumbfactor = 0.0
    for atom in mol.GetAtoms():
        res = oechem.OEAtomGetResidue(atom)
        sumbfactor += res.GetBFactor()
    avgbfactor = sumbfactor / mol.NumAtoms()

    return avgbfactor


def ConsiderResidueAtom(atom, res):
    if atom.GetAtomicNum() == oechem.OEElemNo_H:
        return False
    if res.GetName() == "HOH":
        return False
    return True


def GetMinAndMaxBFactor(ligand, protein, maxdistance=4.0):

    minbfactor = float("inf")
    maxbfactor = float("-inf")

    # Ligand atoms
    for latom in ligand.GetAtoms(oechem.OEIsHeavy()):
        res = oechem.OEAtomGetResidue(latom)
        minbfactor = min(minbfactor, res.GetBFactor())
        maxbfactor = max(maxbfactor, res.GetBFactor())

    # Protein atoms close to ligand atoms
    nn = oechem.OENearestNbrs(protein, maxdistance)
    for latom in ligand.GetAtoms(oechem.OEIsHeavy()):
        for neigh in nn.GetNbrs(latom):
            ratom = neigh.GetBgn()
            res = oechem.OEAtomGetResidue(ratom)
            if ConsiderResidueAtom(ratom, res):
                minbfactor = min(minbfactor, res.GetBFactor())
                maxbfactor = max(maxbfactor, res.GetBFactor())

    return minbfactor, maxbfactor


def SetAverageBFactorOfNearbyProteinAtoms(ligand, protein, itag, maxdistance=4.0):

    nn = oechem.OENearestNbrs(protein, maxdistance)
    for latom in ligand.GetAtoms(oechem.OEIsHeavy()):
        sumbfactor = 0.0
        neighs = []
        for neigh in nn.GetNbrs(latom):
            ratom = neigh.GetBgn()
            res = oechem.OEAtomGetResidue(ratom)
            if ConsiderResidueAtom(ratom, res):
                sumbfactor += res.GetBFactor()
                neighs.append(ratom)

        avgbfactor = 0.0
        if len(neighs) > 0:
            avgbfactor = sumbfactor / len(neighs)
        latom.SetDoubleData(itag, avgbfactor)

#############################################################################
#
#############################################################################


class BFactorArcFxn(oegrapheme.OESurfaceArcFxnBase):
    def __init__(self, colorg, itag):
        oegrapheme.OESurfaceArcFxnBase.__init__(self)
        self.colorg = colorg
        self.itag = itag

    def __call__(self, image, arc):
        adisp = arc.GetAtomDisplay()
        if adisp is None or not adisp.IsVisible():
            return False

        atom = adisp.GetAtom()
        if atom is None:
            return False

        avgresiduebfactor = atom.GetDoubleData(self.itag)
        if avgresiduebfactor == 0.0:
            return True
        color = self.colorg.GetColorAt(avgresiduebfactor)

        pen = oedepict.OEPen(color, color, oedepict.OEFill_Off, 5.0)

        center = arc.GetCenter()
        bAngle = arc.GetBgnAngle()
        eAngle = arc.GetEndAngle()
        radius = arc.GetRadius()

        oegrapheme.OEDrawDefaultSurfaceArc(image, center, bAngle, eAngle, radius, pen)

        return True

    def CreateCopy(self):
        return BFactorArcFxn(self.colorg, self.itag).__disown__()

#############################################################################
#
#############################################################################


class ColorLigandAtomByBFactor(oegrapheme.OEAtomGlyphBase):
    def __init__(self, colorg):
        oegrapheme.OEAtomGlyphBase.__init__(self)
        self.colorg = colorg

    def RenderGlyph(self, disp, atom):
        adisp = disp.GetAtomDisplay(atom)
        if adisp is None or not adisp.IsVisible():
            return False

        res = oechem.OEAtomGetResidue(atom)
        bfactor = res.GetBFactor()
        color = self.colorg.GetColorAt(bfactor)

        pen = oedepict.OEPen(color, color, oedepict.OEFill_On, 1.0)
        radius = disp.GetScale() / 3.0

        layer = disp.GetLayer(oedepict.OELayerPosition_Below)
        oegrapheme.OEDrawCircle(layer, oegrapheme.OECircleStyle_Default,
                                adisp.GetCoords(), radius, pen)
        return True

    def CreateCopy(self):
        return ColorLigandAtomByBFactor(self.colorg).__disown__()

#############################################################################
# INTERFACE
#############################################################################


InterfaceData = '''
!BRIEF [-complex] <input> [-out] <output pdf>

!CATEGORY "input/output options :"

  !PARAMETER -complex
    !ALIAS -c
    !TYPE string
    !KEYLESS 1
    !REQUIRED true
    !VISIBILITY simple
    !BRIEF Input filename of the protein complex
  !END

  !PARAMETER -out
    !ALIAS -o
    !TYPE string
    !REQUIRED true
    !KEYLESS 2
    !VISIBILITY simple
    !BRIEF Output filename
  !END

!END
'''

if __name__ == "__main__":
    sys.exit(main(sys.argv))
