#!/usr/bin/env python
"""
This script uses the correction functions from the ROOT file
output by runCalibration.py and:

- makes a LUT with them
- prints them in py/cpp format so the user can play with it
- makes various plots to check they are sensible

See options with python correction_LUT_plot.py -h

Robin Aggleton
"""

import ROOT
import sys
import numpy as np
from itertools import izip
import os
import argparse
import binning
import common_utils as cu
from runCalibration import generate_eta_graph_name
from correction_LUT_GCT import print_GCT_lut_file
from correction_LUT_stage1 import print_Stage1_lut_file, make_fancy_fits


ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(1)
ROOT.gStyle.SetOptFit(1111)


def print_function(function, lang="cpp"):
    """Print TF1 to screen so can replicate in ROOT or numpy

    Can choose language (py, cpp, numpy)
    """

    rangemin = ROOT.Double()  # eurghhhhh - fixes pass by reference
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
        print "et = np.arange(%g, %g, 0.1)" % (0, 250)
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


def plot_correction_map(corr_fn, filename="correction_map.pdf"):
    """Make plot of pt before Vs after to show mapping"""

    # jet pTs, pre calibration
    min_pre = 0
    max_pre = 52
    jet_pt_pre = np.arange(min_pre, max_pre, 0.5)

    # Post calibration
    jet_pt_post = np.array([pt * corr_fn.Eval(pt) for pt in jet_pt_pre])

    # Make coloured blocks to show the L1 pT bins
    blocks = []  # for persistence otherwise garbabe collected
    gct_bins = np.arange(4, 16 + (18 * 4), 4)
    for i, pt in enumerate(gct_bins):
        if (pt + 4) < jet_pt_post[0] or pt > jet_pt_post[-1]:
            continue
        b = ROOT.TBox(min_pre, pt, max_pre, pt + 4)
        col = 30 if i % 2 else 38
        b.SetFillColor(col)
        b.SetLineStyle(0)
        blocks.append(b)

    # Plot
    c = ROOT.TCanvas("c", "", 800, 800)
    c.SetTicks(1, 1)
    c.SetGrid(1, 1)
    gr = ROOT.TGraph(len(jet_pt_pre), jet_pt_pre, jet_pt_post)
    gr.SetMarkerColor(ROOT.kRed)
    gr.SetTitle("Input jets at 0.5 GeV intervals;p_{T}^{pre};p_{T}^{post}")
    gr.SetMarkerStyle(2)
    gr.Draw("AP")
    for bl in blocks:
        bl.Draw()
    gr.Draw("P")

    # Some helpful lines
    def draw_lines(pt):
        lx = ROOT.TLine(pt, gr.GetYaxis().GetXmin(), pt, pt * corr_fn.Eval(pt))
        lx.SetLineStyle(2)
        lx.Draw()
        ly = ROOT.TLine(0, pt * corr_fn.Eval(pt), pt, pt * corr_fn.Eval(pt))
        ly.SetLineStyle(2)
        ly.Draw()
    draw_lines(5)
    draw_lines(30)
    c.SaveAs(filename)


def plot_graph_function(eta_index, graph, function, filename):
    """Plot both graph and function on the same canvas. Useful for fancy fits.

    Parameters
    ----------
    eta_index: int
        Which eta bin this plot refers to

    graph: TGraphErrors
        Graph to be plotted

    function: MultiFunc
        Function to be drawn

    filename: str
        Path & filename for plot
    """
    c = ROOT.TCanvas("c%d" % eta_index, "SCREW ROOT", 800, 600)
    c.SetTicks(1, 1)
    graph.Draw("ALP")
    y_ax = graph.GetYaxis()
    y_ax.SetRangeUser(0.9 * y_ax.GetXmin(), 1.1 * y_ax.GetXmax())
    graph.SetTitle("%g < #eta^{L1} < %g" % (binning.eta_bins[eta_index], binning.eta_bins[eta_index + 1]))
    # Print the functions in a text box
    text = ROOT.TPaveText(0.2, 0.7, 0.88, 0.88, "NDC NB")
    # TPaveText ignores \n, sigh...
    for line in str(function).split("\n"):
        text.AddText(line)
    text.SetFillColor(ROOT.kWhite)
    text.SetFillStyle(0)
    text.SetLineStyle(0)
    text.Draw()
    function.Draw("SAME")
    graph.GetXaxis().SetLimits(0, 250)
    if eta_index == 10:
        y_ax.SetRangeUser(1.2, 2.4)
    c.SaveAs(filename)


def plot_all_functions(functions, filename, eta_bins, et_min=0, et_max=30):
    """Draw all corrections functions on one big canvas"""
    canv = ROOT.TCanvas("canv", "", 3800, 1200)
    nrows = 2
    ncols = ((len(binning.eta_bins) - 1) / nrows) + 1
    canv.Divide(ncols, nrows)

    # vertical line to intersect graph at a certain pT
    vert_line = ROOT.TLine(5, 0, 5, 3)
    vert_line.SetLineStyle(3)
    vert_line.SetLineWidth(1)

    # horizontal line to intersect graph
    hori_line = ROOT.TLine(et_min, 2, et_max, 2)
    hori_line.SetLineStyle(3)

    for i, fit_func in enumerate(functions):
        canv.cd(i + 1)
        fit_func.SetRange(et_min, et_max)
        fit_func.SetLineWidth(1)
        fit_func.SetTitle("%g - %g" % (eta_bins[i], eta_bins[i + 1]))
        fit_func.Draw()
        corr_5 = fit_func.Eval(5)
        vert_line.SetY1(-15)
        vert_line.SetY2(15)
        ROOT.gPad.SetTicks(1, 1)
        ROOT.gPad.SetGrid(1, 1)
        vert_line.Draw()
        l2 = hori_line.Clone()
        l2.SetY1(corr_5)
        l2.SetY2(corr_5)
        l2.Draw("SAME")

    canv.SaveAs(filename)


def main(in_args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="input ROOT filename")
    parser.add_argument("lut", help="output LUT filename", default="my_lut.txt")
    parser.add_argument("--gct", help="Make LUT for GCT", action='store_true')
    parser.add_argument("--stage1", help="Make LUT for Stage 1", action='store_true')
    parser.add_argument("--fancy", help="Make fancy LUT. "
                        "This checks for low pT deviations and caps the correction value",
                        action='store_true')
    parser.add_argument("--plots", help="Make plots to check sensibility of correction functions.",
                        action='store_true')
    parser.add_argument("--cpp", help="print ROOT C++ code to screen", action='store_true')
    parser.add_argument("--python", help="print PyROOT code to screen", action='store_true')
    parser.add_argument("--numpy", help="print numpy code to screen", action='store_true')
    args = parser.parse_args(args=in_args)

    if not args.gct and not args.stage1:
        print "You didn't pick which format for the LUT - not making a LUT unless you choose!"

    in_file = cu.open_root_file(args.input)
    out_dir = os.path.join(os.path.dirname(args.input),
                           os.path.splitext(os.path.basename(args.lut))[0])

    cu.check_dir_exists_create(out_dir)

    all_fit_params = []
    all_fits = []
    all_graphs = []

    # Get all the fit functions from file and their corresponding graphs
    etaBins = binning.eta_bins_central
    for i, (eta_min, eta_max) in enumerate(izip(etaBins[:-1], etaBins[1:])):
        print "Eta bin:", eta_min, "-", eta_max

        # get the fitted TF1
        fit_func = cu.get_from_file(in_file, "fitfcneta_%g_%g" % (eta_min, eta_max))
        all_fits.append(fit_func)
        fit_params = [fit_func.GetParameter(par) for par in range(fit_func.GetNumberFreeParameters())]
        all_fit_params.append(fit_params)
        # print "Fit parameters:", fit_params

        # get the corresponding fit graph
        fit_graph = cu.get_from_file(in_file, generate_eta_graph_name(eta_min, eta_max))
        all_graphs.append(fit_graph)

        print "Fit fn evaluated at 5 GeV:", fit_func.Eval(5)

        # Print function to screen
        if args.cpp:
            print_function(fit_func, "cpp")
        if args.python:
            print_function(fit_func, "py")
        if args.numpy:
            print_function(fit_func, "numpy")

    # Check we have the correct number
    if len(all_fits) + 1 != len(etaBins) or len(all_fit_params) + 1 != len(etaBins):
        raise Exception("Incorrect number of fit functions/sets of parameters "
                        "for corresponding number of eta bins")

    # Plot all functions on one canvas
    plot_file = os.path.join(out_dir, "all_raw_fits.pdf")
    plot_all_functions(all_fits, plot_file, etaBins, et_min=0, et_max=30)
    fits = all_fits

    # Make LUTs
    if args.gct:
        print_GCT_lut_file(all_fit_params, etaBins, args.lut)

    elif args.stage1:
        fits = make_fancy_fits(all_fits, all_graphs) if args.fancy else all_fits
        print_Stage1_lut_file(fits, args.lut, args.plots)

        if args.plots:
            # plot the fancy fits
            for i, (total_fit, gr) in enumerate(izip(fits, all_graphs)):
                plot_file = os.path.join(out_dir, "fancyfit_%d.pdf" % i)
                plot_graph_function(i, gr, total_fit, plot_file)

    elif args.stage2:
        pass

    if args.plots:
        # Plot function mapping
        for i, (eta_min, eta_max, fit_func) in enumerate(izip(etaBins[:-1], etaBins[1:], fits)):
            plot_file = os.path.join(out_dir, "correction_map_%g_%g.pdf" % (eta_min, eta_max))
            plot_correction_map(fit_func, plot_file)


if __name__ == "__main__":
    main()
