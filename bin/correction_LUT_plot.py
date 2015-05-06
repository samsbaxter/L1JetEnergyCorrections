#!/usr/bin/env python
"""
This script pulls the correction functions from the ROOT file 
output by runCalibration.py, and then:

- makes a LUT with them
- prints them in py/cpp format so the user can play with it
- plots them over suitable pt range, to check they are sensible

Robin Aggleton
"""

import ROOT
import sys
import array
import numpy as np
from itertools import izip
import os
import argparse
import binning


ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(1)
ROOT.gStyle.SetOptFit(1111)


etmin, etmax = 0.1, 30

def print_function(function, lang="cpp"):
    """Print TF1 to screen so can replicate in ROOT

    Can choose language (py, cpp)
    """

    rangemin = ROOT.Double() # eurghhhhh - fixes pass by reference
    rangemax = ROOT.Double()
    function.GetRange(rangemin, rangemax)
    params = [function.GetParameter(i) for i in range(function.GetNumberFreeParameters())]
    name = function.GetName().replace(".", "p")

    print ""

    if lang.lower() == "py" or lang.lower() == "cpp":
        if lang.lower() == 'py':
            print "import ROOT"
            print '%s = ROOT.TF1("%s", "%s", %g, %g);' % (name, name, function.GetExpFormula(), rangemin, rangemax)
        elif lang.lower() == 'cpp':
            print 'TF1 %s("%s", "%s", %g, %g);' % (name, name, function.GetExpFormula(), rangemin, rangemax)
        for i, param in enumerate(params):
            print "%s.SetParameter(%d, %g)" % (name, i, param)
    elif lang.lower() == "numpy":
        print "import numpy as np"
        print "import matplotlib.pyplot as plt"
        print "et = np.arange(%g, %g, 0.1)" % (etmin, etmax)
        for i, param in enumerate(params):
            print "p%d = %f" % (i, param)
        print "def pf_func(et, p0, p1, p2, p3, p4, p5):"
        print "    return p0 + (p1/(np.power(np.log10(et), 2)+p2)) + p3 * np.exp(-1.*p4*np.power(np.log10(et)-p5, 2))"
        print ""
        print ""
        print "plt.plot(et, pf_func(et, p0, p1, p2, p3, p4, p5), lw=2, color='red')"
        print "plt.xlabel(r'$E_T$');plt.ylabel('Correction Factor')"
        print "plt.show()"
        # print "plt.savefig('plot.pdf')"

    print ""


def print_lut_file(fit_params, eta_bins, filename):
    """
    Take fit parameters and print to file, for use in CMSSW config file
    """
    # check
    if (1 + len(fit_params)) != len(eta_bins):
        print "ERROR: no. of eta bins in fit_params not same as no. of eta bins in setup"
        return

    with open(filename, "w") as file:
        file.write("# put this in your py config file\n")
        file.write("    PFCoefficients = cms.PSet(\n")

        # non tau bit first
        for i, bin in enumerate(fit_params):
            line = "        nonTauJetCalib%i = cms.vdouble(" % i
            line += ','.join([str("%.3f" % x) for x in fit_params[i]])
            line += "),\n"
            file.write(line)

        # tau bit - only central region
        for i, bin in enumerate(fit_params):
            if eta_bins[i + 1] <= 3.0:
                line = "        tauJetCalib%i = cms.vdouble(" % i
                line += ','.join([str("%.3f" % x) for x in fit_params[i]])
                line += "),\n"
                file.write(line)

        file.write("    )\n")


def main(in_args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="input ROOT filename")
    parser.add_argument("lut", help="output LUT filename", default="my_lut.py")
    args = parser.parse_args(args=in_args)

    in_file = ROOT.TFile(args.input)

    # Canvas for plotting all fits
    canv = ROOT.TCanvas("c", "", 3800, 1200)
    ncols = ((len(binning.eta_bins)-1) / 2) + 1
    canv.Divide(ncols, 2)

    line = ROOT.TLine(5, 0, 5, 3)
    line.SetLineStyle(3)
    line.SetLineWidth(1)

    line2 = ROOT.TLine(1, 2, 20, 2)
    line2.SetLineStyle(3)
    all_fit_params = []

    for i, etamin in enumerate(binning.eta_bins[:-1]):
        etamax = binning.eta_bins[i+1]

        # get the fitted TF1
        fit_func = in_file.Get("fitfcneta_%g_%g" % (etamin, etamax))
        if not fit_func:
            raise Exception("Couldn't get fit function fitfcneta_%g_%g" % (etamin, etamax))

        fit_params = [fit_func.GetParameter(par) for par in range(fit_func.GetNumberFreeParameters())]
        all_fit_params.append(fit_params)

        # Print function to screen
        print_function(fit_func, "cpp")
        print_function(fit_func, "py")
        print_function(fit_func, "numpy")

        # Print function to canvas
        canv.cd(i+1)
        fit_func.SetRange(etmin, etmax)
        fit_func.SetLineWidth(1)
        fit_func.Draw()
        line.SetY1(-15)
        line.SetY2(15)
        line.Draw()
        corr_10 = fit_func.Eval(10)
        l2 = line2.Clone()
        l2.SetY1(corr_10)
        l2.SetY2(corr_10)
        print corr_10
        l2.Draw("SAME")

    canv.SaveAs("all_fits.pdf")
    print_lut_file(all_fit_params, binning.eta_bins, args.lut)

if __name__ == "__main__":
    main()
