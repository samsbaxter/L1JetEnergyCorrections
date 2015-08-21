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


def print_GCT_lut_file(fit_params, eta_bins, filename):
    """
    Take fit parameters and print to file, for use in CMSSW config file with GCT emulator.

    Eta bins are in order from the center to forwards i.e. 0-0.348, 0.348-0.695, etc

    IMPORTANT: high precision is required, particularly if you are using the PF
    correction function and [3] is large - then precision of [4] in particular
    is crucial. A change from 3 d.p. to 6 d.p. changes the correction factor
    from -1.27682 to 2.152 !!!
    """
    # check
    if (1 + len(fit_params)) != len(eta_bins):
        print "ERROR: no. of eta bins in fit_params not same as no. of eta bins in setup"
        return

    with open(filename, "w") as lut_file:
        lut_file.write("# put this in your py config file\n")
        lut_file.write("PFCoefficients = cms.PSet(\n")

        # non tau bit first
        for i, bin in enumerate(fit_params):
            line = "    nonTauJetCalib%i = cms.vdouble(" % i
            line += ','.join([str("%.8f" % x) for x in fit_params[i]])
            line += "),\n"
            lut_file.write(line)

        # tau bit - only central region
        for i, bin in enumerate(fit_params):
            if eta_bins[i + 1] <= 3.0:
                line = "    tauJetCalib%i = cms.vdouble(" % i
                line += ','.join([str("%.8f" % x) for x in fit_params[i]])
                line += "),\n"
                lut_file.write(line)

        lut_file.write(")\n")


def print_Stage1_lut_file(fit_functions, eta_bins, filename):
    """
    Take fit parameters and print to file, for use in CMSSW config file with Stage 1 emulator.

    fit_params is a list, where each entry is a list of fit parameters for a given eta bin.
    The order MUST be in physical eta, so the first entry coveres 0 - 0.348.

    Note that the LUT has entries for both + and - eta. It refers to eta by region number (0 - 21),
    *not* physical eta. Thus the first bin for the LUT must be 4.5 - 5 NOT 0 - 0.348.
    Don't worry, this method handles that conversion.

    Please update the header if necessary - check with Len.

    Adapted by code originally by Maria Cepeda.

    IMPORTANT: high precision is required, particularly if you are using the PF
    correction function and [3] is large - then precision of [4] in particular
    is crucial. A change from 3 d.p. to 6 d.p. changes the correction factor
    from -1.27682 to 2.152 !!!
    """
        # check
    if (1 + len(fit_functions)) != len(eta_bins):
        print "ERROR: no. of eta bins in fit_functions not same as no. of eta bins in setup"
        return

    with open(filename, "w") as lut_file:
        with open(filename.replace(".txt", "_dump.txt"), "w") as dump_file:
            header = """#<header> V1 15 7 </header>
########################################
# jet calibration and ranking LUT
# MSB 5 bits are eta value, LSB 10 bits
# are jet pt (not 14!, make sure to cap)
########################################
# Second  attempt at preliminar CalibJet for FirmwareVersion3
# Symmetric in Eta and RANK=0 jets do not scale up
#########################################
"""
            lut_file.write(header)

            for eta in xrange(22):

                param_ind = (10 - eta) if eta < 11 else (eta - 11)
                print "Eta region:", eta, " = physical eta bin:", param_ind
                for pt in xrange(1025):

                    if pt >(1<<10)-1:
                        pt = ((1<<10) -1)
                        break

                    lut_address = (eta<<10) + pt
                    physPt = pt / 2. # convert HW pt to physical pt
                    pt_corr = physPt * fit_functions[param_ind].Eval(physPt)
                    if pt_corr < 0:
                        pt_corr = 0
                    RANKCALIB = int(pt_corr / 4);  # The 4 is to go to the 4 GeV binning at the GT
                    if (RANKCALIB > 63):
                        RANKCALIB = 63;
                    line = "%s %s\n" % (lut_address, RANKCALIB)
                    lut_file.write(line);
                    dump_line = "eta: %d phys pt: %f LUT address: %d corrPhysPt: %f RANKCALIB: %d\n" % (eta, physPt, lut_address, pt_corr, RANKCALIB)
                    dump_file.write(dump_line)

def plot_correction_map(corr_fn, filename="correction_map.pdf"):
    """Make plot of pt before Vs after to show mapping"""

    # jet pTs, pre calibration
    min_pre = 0
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
    # h_pre = ROOT.TH1D("h_pre", ";p_{T};N", len(gct_bins)-1, gct_bins[0], gct_bins[-1])
    # h_post = ROOT.TH1D("h_post", ";p_{T};N", len(gct_bins)-1, gct_bins[0], gct_bins[-1])

    # for pt in jet_pt_pre:
    #     h_pre.Fill(pt)

    # for pt in jet_pt_post:
    #     h_post.Fill(pt)

    # h_post.SetLineColor(ROOT.kRed)
    # h_pre.Draw("HIST")
    # h_post.Draw("SAMEHIST")

    # leg = ROOT.TLegend(0.7, 0.7, 0.8, 0.8)
    # leg.SetFillColor(ROOT.kWhite)
    # leg.AddEntry(h_pre, "Pre", "L")
    # leg.AddEntry(h_post, "Post", "L")
    # leg.Draw()
    # c.SaveAs(filename.replace('correction_map', 'occupancy_map'))


def main(in_args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="input ROOT filename")
    parser.add_argument("lut", help="output LUT filename", default="my_lut.txt")
    parser.add_argument("--gct", help="Make LUT for GCT", action='store_true')
    parser.add_argument("--stage1", help="Make LUT for Stage 1", action='store_true')
    parser.add_argument("--plots", help="Make plots to check sensibility of correction functions.",
                        action='store_true')
    parser.add_argument("--cpp", help="print ROOT C++ code to screen", action='store_true')
    parser.add_argument("--python", help="print PyROOT code to screen", action='store_true')
    parser.add_argument("--numpy", help="print numpy code to screen", action='store_true')
    args = parser.parse_args(args=in_args)

    if not args.gct and not args.stage1:
        print "You didn't pick which format for the LUT - not making a LUT unless you choose!"

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
    all_fits = []

    etaBins = binning.eta_bins
    for i, (etamin, etamax) in enumerate(izip(etaBins[:-1], etaBins[1:])):
        print "Eta bin:", etamin, "-", etamax

        # get the fitted TF1
        fit_func = get_from_file(in_file, "fitfcneta_%g_%g" % (etamin, etamax))
        if not fit_func:
            raise Exception("Couldn't get fit function fitfcneta_%g_%g" % (etamin, etamax))

        all_fits.append(fit_func)
        fit_params = [fit_func.GetParameter(par) for par in range(fit_func.GetNumberFreeParameters())]
        all_fit_params.append(fit_params)
        print "Fit parameters:", fit_params

        corr_5 = fit_func.Eval(5)
        print "Fit fn evaluated at 5 GeV:", corr_5

        # Print function to screen
        if args.cpp:
            print_function(fit_func, "cpp")
        if args.python:
            print_function(fit_func, "py")
        if args.numpy:
            print_function(fit_func, "numpy")

        if args.plots:
            # Print function to canvas
            canv.cd(i+1)
            fit_func.SetRange(etmin, etmax)
            fit_func.SetLineWidth(1)
            fit_func.Draw()
            line.SetY1(-15)
            line.SetY2(15)
            line.Draw()
            l2 = line2.Clone()
            l2.SetY1(corr_5)
            l2.SetY2(corr_5)
            l2.Draw("SAME")

            # Plot function mapping
            plot_correction_map(fit_func, out_dir+"/correction_map_%g_%g.pdf" % (etamin, etamax))

    if args.plots:
        canv.SaveAs(out_dir+"/all_fits.pdf")

    if args.gct:
        print_GCT_lut_file(all_fit_params, etaBins, args.lut)
    elif args.stage1:
        print_Stage1_lut_file(all_fits, etaBins, args.lut)


if __name__ == "__main__":
    main()
