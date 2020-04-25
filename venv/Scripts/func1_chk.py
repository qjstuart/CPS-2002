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

import sys
from openeye import oechem
from openeye import oeff


# //////////////////////////////////////////////////////////////////////////
# The following function displays how to use a checkpoint during function //
# optimization.  A simple quadradic equation is minimized for which the   //
# analytical gradient is provided but the second derivative is not.       //
# //////////////////////////////////////////////////////////////////////////


class Function(oeff.OEFunc1):
    def __init__(self):
        oeff.OEFunc1.__init__(self)
        pass

    def begin(self):
        pass

    def NumVar(self):
        return 1

    def __call__(self, x, g=None):
        if isinstance(x, oechem.OEDoubleArray):
            if g is not None:
                g[0] = 2.0*x[0]-7.0
                return x[0]*x[0]-7*x[0]+63
            else:
                return x[0]*x[0]-7*x[0]+63
        else:
            x1 = oechem.OEDoubleArray(x, self.NumVar(), False)
            if g is not None:
                g1 = oechem.OEDoubleArray(g, self.NumVar(), False)
                g1[0] = 2.0*x1[0]-7.0
                return x1[0]*x1[0]-7*x1[0]+63
            else:
                return x1[0]*x1[0]-7*x1[0]+63


class ChkPt(oeff.OECheckpoint0):
    def __init__(self):
        oeff.OECheckpoint0.__init__(self)
        pass

    def __call__(self, iteration, nvar, fval, var, state):
        # Intermediate information during optimization
        var1 = oechem.OEDoubleArray(var, 1, False)
        oechem.OEThrow.Info("iteration: %d x: %d value: %d state: %d"
                            % (iteration, var1[0], fval, state))

        # To demonstrate how to force quitting optimization from checkpoint
        # this returns false when iteration is 5
        if iteration >= 5:
            return False
        else:
            return True


def main(args):
    if len(args) != 2:
        oechem.OEThrow.Usage("%s <initial guess>" % args[0])

    x = oechem.OEDoubleArray(1)
    try:
        x[0] = float(args[1])
    except ValueError:
        oechem.OEThrow.Usage("%s <initial guess (expecting a number)>" % args[0])

    func = Function()

    # Calculate function value at given x
    value = func(x)
    oechem.OEThrow.Info("Function value at x = %d is %d" % (x[0], value))

    # Optimize function using BFGS Optimizer and checkpoint
    xOpt = oechem.OEDoubleArray(1)
    optimizer = oeff.OEBFGSOpt()
    value = optimizer(func, ChkPt(), x, xOpt)
    oechem.OEThrow.Info("Function has a minimia at x = %d and the minimum value is %d"
                        % (xOpt[0], value))

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
