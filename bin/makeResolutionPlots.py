"""
This script takes as input the output file from RunMatcher, and loops over
matched reference jet/L1 jet pairs, making resolution plots.

Does 2 types of "resolution":
L1 resolution = L1 - Ref / L1
Ref resolution = L1 - Ref / Ref

Usage: see
python makeResolutionPlots -h

"""

import ROOT
import sys
from array import array
import numpy
from pprint import pprint
from itertools import izip
import os
import argparse
import binning


ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(1)
ROOT.gStyle.SetOptFit(1111)
ROOT.TH1.SetDefaultSumw2()
ROOT.gROOT.ProcessLine('.L tdrStyle.C')
ROOT.setTDRStyle()
ROOT.gStyle.SetOptTitle(0);
ROOT.gStyle.SetOptStat(1);
ROOT.gROOT.ForceStyle();


def check_var_stored(tree, var):
    """Check to see if TTree has branch with name var"""
    return tree.GetListOfBranches().FindObject(var)

def check_fit_peaks(fit_mean, hist):
    """Check fit ok by comparing peaks"""
    peak = hist.GetBinCenter(hist.GetMaximumBin())
    return abs(peak - fit_mean) < abs(peak)


def plot_resolution_bin_fit(res_2d, ptmin, ptmax, hist_title, hist_name, graph, output):
    """
    Does a resolution plot for one pt bin, and fits a Gaussian to it.

    res_2d is a 2D plot of resolution vs pt

    ptmin & ptmax are bin limits
    hist_title is title of resultant hist
    hist_name is name of resultant hist
    graph is TGraphErrors object to add point to, adds new point at (pt, width)
    output is where you want to write hist + fit to

    """
    # Get bin indices corresponding to physical pt values
    bin_low = res_2d.GetXaxis().FindBin(ptmin)
    bin_high = res_2d.GetXaxis().FindBin(ptmax)-1

    # For graph - get bin middle & width
    pt_mid = 0.5 * (ptmin + ptmax)
    pt_width = ptmin - ptmin

    h_res = res_2d.ProjectionY(hist_name, bin_low, bin_high)
    h_res.SetTitle(hist_title)

    if h_res.GetEntries() > 0:
        # fit_l1 = int(h_res.Fit("gaus", "Q", "R", h_res.GetMean() - 1. * h_res.GetRMS(), h_res.GetMean() + 1. * h_res.GetRMS()))
        fit_l1 = int(h_res.Fit("gaus", "Q"))
        fit_mean = h_res.GetFunction("gaus").GetParameter(1)

        # default values for the widht & its error - safe if the fit went wrong
        width = h_res.GetRMS()
        width_err = h_res.GetRMSError()

        # check fit converged, and is sensible
        if fit_l1 == 0: # and check_fit_peaks(fit_mean, h_res):
            width =  h_res.GetFunction("gaus").GetParameter(2)
            width_err = h_res.GetFunction("gaus").GetParError(2)
        else:
            print "Poor fit to l1 res - using raw values"
        count = graph.GetN()
        graph.SetPoint(count, pt_mid, width)
        graph.SetPointError(count, pt_width, width_err)
    else:
        print "0 entries in resolution plot"
    output.WriteTObject(h_res)


def plot_resolution(inputfile, outputfile, ptBins_in, absetamin, absetamax):
    """Do various resolution plots for given eta bin, for all pT bins"""

    print "Doing eta bin: %g - %g" % (absetamin, absetamax)

    # Input tree
    tree_raw = inputfile.Get("valid")

    # Output folders
    output_f = outputfile.mkdir('eta_%g_%g' % (absetamin, absetamax))
    output_f_hists = output_f.mkdir("Histograms")

    # Eta cut string
    eta_cut = " TMath::Abs(eta)<%g && TMath::Abs(eta) > %g " % (absetamax, absetamin)
    # pt cut string for 2D plots
    pt_cut_all = "pt < %g && pt > %g" % (ptBins_in[-1], ptBins_in[0])

    title = "%g < |#eta^{L1}| < %g" % (absetamin, absetamax)

    # First make 2D plots of resolution Vs Et,
    # then we can project them for individual Et bins
    # This is *much* faster than just making all the plots individually
    res_min = -5
    res_max = 2
    nbins_res = 140
    pt_bin_min = ptBins_in[0]
    pt_bin_max = ptBins_in[-1]
    nbins_et = 4 * (pt_bin_max - pt_bin_min)

    # 2D plot of L1-Ref/L1 VS L1
    var = "resL1" if check_var_stored(tree_raw, "resL1") else "(pt-(pt*rsp))/pt"  # for old pair files
    tree_raw.Draw("%s:pt>>res_l1_2d(%d, %g, %g, %d, %g, %g)" % (var, nbins_et, pt_bin_min, pt_bin_max, nbins_res, res_min, res_max), eta_cut + "&&" + pt_cut_all)
    res_l1_2d = ROOT.gROOT.FindObject("res_l1_2d")
    res_l1_2d.SetTitle("%s;E_{T}^{L1} [GeV];(E_{T}^{L1} - E_{T}^{Gen})/E_{T}^{L1}" % title)
    output_f_hists.WriteTObject(res_l1_2d)

    # 2D plot of L1-Ref/L1 VS L1
    var = "resRef" if check_var_stored(tree_raw, "resRef") else "(pt-(pt*rsp))/(pt*rsp)"
    res_min = -2
    nbins_res = 80
    tree_raw.Draw("%s:pt>>res_refVsl1_2d(%d, %g, %g, %d, %g, %g)" % (var, nbins_et, pt_bin_min, pt_bin_max, nbins_res, res_min, res_max), eta_cut + "&&" + pt_cut_all)
    res_refVsl1_2d = ROOT.gROOT.FindObject("res_refVsl1_2d")
    res_refVsl1_2d.SetTitle("%s;E_{T}^{L1} [GeV];(E_{T}^{L1} - E_{T}^{Gen})/E_{T}^{Gen}" % title)
    output_f_hists.WriteTObject(res_refVsl1_2d)

    # 2D plot of L1-Ref/L1 VS Ref
    var = "resRef" if check_var_stored(tree_raw, "resRef") else "(pt-(pt*rsp))/(pt*rsp)"
    res_min = -2
    nbins_res = 80
    tree_raw.Draw("%s:(pt*rsp)>>res_refVsref_2d(%d, %g, %g, %d, %g, %g)" % (var, nbins_et, pt_bin_min, pt_bin_max, nbins_res, res_min, res_max), eta_cut + "&&" + pt_cut_all)
    res_refVsref_2d = ROOT.gROOT.FindObject("res_refVsref_2d")
    res_refVsref_2d.SetTitle("%s;E_{T}^{Ref} [GeV];(E_{T}^{L1} - E_{T}^{Gen})/E_{T}^{Gen}" % title)
    output_f_hists.WriteTObject(res_refVsref_2d)

    # Graphs to hold resolution for all pt bins
    res_graph_l1 = ROOT.TGraphErrors()
    res_graph_l1.SetNameTitle("resL1_%g_%g" % (absetamin, absetamax), "%s;E_{T}^{L1} [GeV];E_{T}^{L1} - E_{T}^{Gen}/E_{T}^{L1}" % title)

    res_graph_refVsl1 = ROOT.TGraphErrors() # binned in l1 pt
    res_graph_refVsl1.SetNameTitle("resRefL1_%g_%g" % (absetamin, absetamax), "%s;E_{T}^{L1} [GeV];E_{T}^{L1} - E_{T}^{Gen}/E_{T}^{Gen}" % title)

    res_graph_refVsref = ROOT.TGraphErrors() # binned in ref pt
    res_graph_refVsref.SetNameTitle("resRefRef_%g_%g" % (absetamin, absetamax), "%s;E_{T}^{Ref} [GeV];E_{T}^{L1} - E_{T}^{Gen}/E_{T}^{Gen}" % title)

    # Now go through pt bins, and plot resolution for each, fit with gaussian,
    # and add width to graph
    for i, ptmin in enumerate(ptBins_in[:-1]):
        ptmax = ptBins_in[i+1]
        pt_cut = "pt < %g && pt > %g" % (ptmax, ptmin)
        pt_cut_ref = "(pt*rsp) < %g && (pt*rsp) > %g" % (ptmax, ptmin)
        print "    Doing pt bin: %g - %g" % (ptmin, ptmax)

        # Plot difference in L1 pT and Ref pT
        nbins = 100
        var = "ptDiff" if check_var_stored(tree_raw, "ptDiff") else "pt-(pt*rsp)"
        tree_raw.Draw("%s>>diffPt(%d)" % (var, nbins), eta_cut + " && " + pt_cut)
        h_diffPt = ROOT.gROOT.FindObject("diffPt")
        h_diffPt.SetName("diffPt_%g_%g" % (ptmin, ptmax))
        h_diffPt.SetTitle("%s;E_{T}^{L1} - E_{T}^{Gen} [GeV];N" % title)
        output_f_hists.WriteTObject(h_diffPt)

        # Plot resolution wrt L1 pT & fit
        plot_resolution_bin_fit(res_l1_2d, ptmin, ptmax,
            "%s;(E_{T}^{L1} - E_{T}^{Gen})/E_{T}^{L1};N" % title,
            "res_l1_%g_%g" % (ptmin, ptmax), res_graph_l1, output_f_hists)

        # Plot ref resolution wrt L1 pT & fit
        plot_resolution_bin_fit(res_refVsl1_2d, ptmin, ptmax,
            "%s;(E_{T}^{L1} - E_{T}^{Gen})/E_{T}^{Gen};N" % title,
            "res_ref_l1_%g_%g" % (ptmin, ptmax), res_graph_refVsl1, output_f_hists)

        # Plot ref resolution Vs ref pt
        plot_resolution_bin_fit(res_refVsref_2d, ptmin, ptmax,
            "%s;(E_{T}^{L1} - E_{T}^{Gen})/E_{T}^{Gen};N" % title,
            "res_ref_ref_%g_%g" % (ptmin, ptmax), res_graph_refVsref, output_f_hists)

    output_f.WriteTObject(res_graph_l1)
    output_f.WriteTObject(res_graph_refVsl1)
    output_f.WriteTObject(res_graph_refVsref)


########### MAIN ########################
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input ROOT filename")
    parser.add_argument("output", help="output ROOT filename")
    parser.add_argument("--incl", action="store_true", help="Do inclusive eta plots")
    parser.add_argument("--excl", action="store_true", help="Do exclusive eta plots")
    args = parser.parse_args()

    inputf = ROOT.TFile(args.input, "READ")
    outputf = ROOT.TFile(args.output, "RECREATE")
    print "Reading from", args.input
    print "Writing to", args.output

    if not inputf or not outputf:
        raise Exception("Couldn't open input or output files")

    # Setup pt, eta bins for doing calibrations
    pt_bins = binning.pt_bins[:]
    pt_bins_wide = binning.pt_bins_wide[:] # larger bins at higher pt
    eta_bins = binning.eta_bins[:]

    print "Running over eta bins:", eta_bins
    print "Running over pT bins:", pt_bins

    # Do plots for individual eta bins
    if args.excl:
        print "Doing individual eta bins"
        for i,eta in enumerate(eta_bins[0:-1]):
            emin = eta
            emax = eta_bins[i+1]
            if emin >= 3.:  # diff binning for forward region
                plot_resolution(inputf, outputf, pt_bins_wide, emin, emax)
            else:
                plot_resolution(inputf, outputf, pt_bins, emin, emax)

    # Do plots for inclusive eta
    # Skip if doing exlcusive and only 2 bins, or if only 1 bin
    if args.incl and ((not args.excl and len(eta_bins) >= 2) or (args.excl and len(eta_bins)>2)):
        print "Doing inclusive eta"
        plot_resolution(inputf, outputf, pt_bins, eta_bins[0], eta_bins[-1])


if __name__ == "__main__":
    main()
