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
from common_utils import *


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
            print "%s.SetParameter(%d, %.8f)" % (name, i, param)
    elif lang.lower() == "numpy":
        print "import numpy as np"
        print "import matplotlib.pyplot as plt"
        print "et = np.arange(%g, %g, 0.1)" % (etmin, etmax)
        for i, param in enumerate(params):
            print "p%d = %.8f" % (i, param)
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

    IMPORTANT: high precision is required, particularly if you are using the PF
    correction function and [3] is large - then precision of [4] in particular
    is crucial. A change from 3 d.p. to 6 d.p. changes the correction factor
    from -1.27682 to 2.152 !!!
    """
    # check
    if (1 + len(fit_params)) != len(eta_bins):
        print "ERROR: no. of eta bins in fit_params not same as no. of eta bins in setup"
        return

    with open(filename, "w") as file:
        file.write("# put this in your py config file\n")
        file.write("PFCoefficients = cms.PSet(\n")

        # non tau bit first
        for i, bin in enumerate(fit_params):
            line = "    nonTauJetCalib%i = cms.vdouble(" % i
            line += ','.join([str("%.8f" % x) for x in fit_params[i]])
            line += "),\n"
            file.write(line)

        # tau bit - only central region
        for i, bin in enumerate(fit_params):
            if eta_bins[i + 1] <= 3.0:
                line = "    tauJetCalib%i = cms.vdouble(" % i
                line += ','.join([str("%.8f" % x) for x in fit_params[i]])
                line += "),\n"
                file.write(line)

        file.write(")\n")


def plot_correction_map(corr_fn, filename="correction_map.pdf"):
    """Make plot of pt before Vs after to show mapping"""

    # jet pTs, pre calibration
    min_pre = 4
    max_pre = 52
    jet_pt_pre = np.arange(min_pre, max_pre, 0.5)

    # Post calibration
    jet_pt_post = np.array([pt * corr_fn.Eval(pt) for pt in jet_pt_pre])

    # Make coloured blocks to show the GCT bins
    blocks = []  # for persistence otherwise garbabe collected
    gct_bins = np.arange(4, 16 + (18*4), 4)
    for i, pt in enumerate(gct_bins):
        if pt+4 < jet_pt_post[0] or pt > jet_pt_post[-1]:
            continue
        b = ROOT.TBox(min_pre, pt, max_pre, pt+4)
        col = 30 if i % 2 else 38
        b.SetFillColor(col)
        b.SetLineStyle(0)
        blocks.append(b)

    # Plot
    c = ROOT.TCanvas("c","", 800, 800)
    c.SetTicks(1, 1)
    c.SetGrid(1, 1)
    gr = ROOT.TGraph(len(jet_pt_pre), jet_pt_pre, jet_pt_post)
    gr.SetMarkerColor(ROOT.kRed)
    gr.SetTitle("Input jets at 0.5 GeV intervals;p_{T}^{pre};p_{T}^{post}")
    gr.SetMarkerStyle(2)
    gr.Draw("AP")
    [b.Draw() for b in blocks]
    gr.Draw("P")
    # Some helpful lines
    # For pT_in = 30
    l30x = ROOT.TLine(30, gr.GetYaxis().GetXmin(), 30, 30*corr_fn.Eval(30))
    l30x.SetLineStyle(2)
    l30x.Draw()
    l30y = ROOT.TLine(0, 30*corr_fn.Eval(30), 30, 30*corr_fn.Eval(30))
    l30y.SetLineStyle(2)
    l30y.Draw()
    # For pT_in = 30
    l5x = ROOT.TLine(5, gr.GetYaxis().GetXmin(), 5, 5*corr_fn.Eval(5))
    l5x.SetLineStyle(2)
    l5x.Draw()
    l5y = ROOT.TLine(0, 5*corr_fn.Eval(5), 5, 5*corr_fn.Eval(5))
    l5y.SetLineStyle(2)
    l5y.Draw()
    c.SaveAs(filename)

    corr_fn.Eval(5)
    # Make hists of pre & post occupancy
    h_pre = ROOT.TH1D("h_pre", ";p_{T};N", len(gct_bins)-1, gct_bins[0], gct_bins[-1])
    h_post = ROOT.TH1D("h_post", ";p_{T};N", len(gct_bins)-1, gct_bins[0], gct_bins[-1])

    for pt in jet_pt_pre:
        h_pre.Fill(pt)

    for pt in jet_pt_post:
        h_post.Fill(pt)

    h_post.SetLineColor(ROOT.kRed)
    h_pre.Draw("HIST")
    h_post.Draw("SAMEHIST")

    leg = ROOT.TLegend(0.7, 0.7, 0.8, 0.8)
    leg.SetFillColor(ROOT.kWhite)
    leg.AddEntry(h_pre, "Pre", "L")
    leg.AddEntry(h_post, "Post", "L")
    leg.Draw()
    c.SaveAs(filename.replace('correction_map', 'occupancy_map'))


def main(in_args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="input ROOT filename")
    parser.add_argument("lut", help="output LUT filename", default="my_lut.py")
    parser.add_argument("--cpp", help="print ROOT C++ code to screen", action='store_true')
    parser.add_argument("--python", help="print PyROOT code to screen", action='store_true')
    parser.add_argument("--numpy", help="print numpy code to screen", action='store_true')
    args = parser.parse_args(args=in_args)

    in_file = open_root_file(args.input)
    out_dir = os.path.dirname(args.lut)

    # Canvas for plotting all fits
    canv = ROOT.TCanvas("canv", "", 3800, 1200)
    ncols = ((len(binning.eta_bins)-1) / 2) + 1
    canv.Divide(ncols, 2)

    line = ROOT.TLine(5, 0, 5, 3)
    line.SetLineStyle(3)
    line.SetLineWidth(1)

    line2 = ROOT.TLine(1, 2, 20, 2)
    line2.SetLineStyle(3)
    all_fit_params = []

    etaBins = binning.eta_bins_central # CHANGE ME TO INCLUDE FWD
    for i, (etamin, etamax) in enumerate(izip(etaBins[:-1], etaBins[1:])):
        print "Eta bin:", etamin, "-", etamax

        # get the fitted TF1
        fit_func = get_from_file(in_file, "fitfcneta_%g_%g" % (etamin, etamax))
        if not fit_func:
            raise Exception("Couldn't get fit function fitfcneta_%g_%g" % (etamin, etamax))

        fit_params = [fit_func.GetParameter(par) for par in range(fit_func.GetNumberFreeParameters())]
        all_fit_params.append(fit_params)
        print "Fit parameters:", fit_params
        corr_10 = fit_func.Eval(10)
        print "Fit fn evaluated at 10 GeV:", corr_10

        # Print function to screen
        if args.cpp:
            print_function(fit_func, "cpp")
        if args.python:
            print_function(fit_func, "py")
        if args.numpy:
            print_function(fit_func, "numpy")

        # Print function to canvas
        canv.cd(i+1)
        fit_func.SetRange(etmin, etmax)
        fit_func.SetLineWidth(1)
        fit_func.Draw()
        line.SetY1(-15)
        line.SetY2(15)
        line.Draw()
        l2 = line2.Clone()
        l2.SetY1(corr_10)
        l2.SetY2(corr_10)
        l2.Draw("SAME")

        # Plot function mapping
        plot_correction_map(fit_func, out_dir+"/correction_map_%g_%g.pdf" % (etamin, etamax))

    canv.SaveAs(out_dir+"/all_fits.pdf")
    print_lut_file(all_fit_params, etaBins, args.lut)

if __name__ == "__main__":
    main()
