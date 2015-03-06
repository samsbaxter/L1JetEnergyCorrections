"""
This script takes as input the output file from RunMatcher, and loops over
matched genjet/L1 jet pairs, making resolution plots.

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


def plot_resolution(inputfile, outputfile, ptBins_in, absetamin, absetamax):
    """Do various resolution plots for given eta bin, for all pT bins"""

    print "Doing eta bin: %g - %g" % (absetamin, absetamax)

    # Input tree
    tree_raw = inputfile.Get("valid")

    # Output folders
    output_f = outputfile.mkdir('eta_%g_%g' % (absetamin, absetamax))
    # output_f_hists = output_f.mkdir("Histograms")

    # Eta cut string
    eta_cut = " TMath::Abs(eta)<%g && TMath::Abs(eta) > %g " % (absetamax, absetamin)
    # pt cut string for 2D plots
    pt_cut_all = "pt < %g && pt > %g" % (ptBins_in[-1], ptBins_in[0])

    # To store widths of gaussians & their errors
    widths_l1 = []
    widths_l1_err = []
    widths_ref = []
    widths_ref_err = []

    # First make 2D plots of resolution Vs Et,
    # then we can project them for individual Et bins
    # This is *much* faster than just making all the plots individually
    res_min = -5
    res_max = 2
    nbins_res = 140
    pt_bin_min = ptBins_in[0]
    pt_bin_max = ptBins_in[-1]
    nbins_et = 4 * (pt_bin_max - pt_bin_min)

    # 2D plot of L1-Gen/L1 VS L1
    var = "resL1" if check_var_stored(tree_raw, "resL1") else "(pt-(pt*rsp))/pt"  # for old pair files
    tree_raw.Draw("%s:pt>>res_l1_2d(%d, %g, %g, %d, %g, %g)" % (var, nbins_et, pt_bin_min, pt_bin_max, nbins_res, res_min, res_max), eta_cut + "&&" + pt_cut_all)
    res_l1_2d = ROOT.gROOT.FindObject("res_l1_2d")
    res_l1_2d.SetTitle("%g < |#eta| < %g;E_{T}^{L1} [GeV];(E_{T}^{L1} - E_{T}^{Gen})/E_{T}^{L1}" % (absetamin, absetamax))
    output_f.WriteTObject(res_l1_2d)

    # 2D plot of L1-Gen/L1 VS Gen
    var = "resRef" if check_var_stored(tree_raw, "resRef") else "(pt-(pt*rsp))/(pt*rsp)"
    res_min = -2
    nbins_res = 80
    tree_raw.Draw("%s:pt>>res_ref_2d(%d, %g, %g, %d, %g, %g)" % (var, nbins_et, pt_bin_min, pt_bin_max, nbins_res, res_min, res_max), eta_cut + "&&" + pt_cut_all)
    res_ref_2d = ROOT.gROOT.FindObject("res_ref_2d")
    res_ref_2d.SetTitle("%g < |#eta| < %g;E_{T}^{L1} [GeV];(E_{T}^{L1} - E_{T}^{Gen})/E_{T}^{Gen}" % (absetamin, absetamax))
    output_f.WriteTObject(res_ref_2d)

    # Graphs to hold resolution for all pt bins
    # res_graph_l1 = ROOT.TGraphErrors(len(widths), array("d", pt_centres), array("d", widths), array("d", pt_err), array("d", widths_err))

    # Now go thorugh pt bins, and plot resolution for each, fit with gaussian,
    # and add width to graph
    for i, ptmin in enumerate(ptBins_in[:-1]):
        ptmax = ptBins_in[i+1]
        pt_cut = "pt < %g && pt > %g" % (ptmax, ptmin)
        print "    Doing pt bin: %g - %g" % (ptmin, ptmax)

        # Plot difference in L1 pT and Gen pT
        nbins = 100
        var = "ptDiff" if check_var_stored(tree_raw, "ptDiff") else "pt-(pt*rsp)"
        tree_raw.Draw("%s>>diffPt(%d)" % (var, nbins), eta_cut + " && " + pt_cut)
        h_diffPt = ROOT.gROOT.FindObject("diffPt")
        h_diffPt.SetName("diffPt_%g_%g" % (ptmin, ptmax))
        h_diffPt.SetTitle("%g < |#eta| < %g;E_{T}^{L1} - E_{T}^{Gen} [GeV];N" % (absetamin, absetamax))
        output_f.WriteTObject(h_diffPt)

        # Get bin indices corresponding to physical pt values
        bin_low = res_l1_2d.GetXaxis().FindBin(ptmin)
        bin_high = res_l1_2d.GetXaxis().FindBin(ptmax)-1

        # Plot resolution wrt L1 pT & fit
        h_res_l1 = res_l1_2d.ProjectionY("res_l1_%g_%g" % (ptmin, ptmax), bin_low, bin_high)
        h_res_l1.SetTitle("%g < |#eta| < %g;(E_{T}^{L1} - E_{T}^{Gen})/E_{T}^{L1};N" % (absetamin, absetamax))
        if h_res_l1.GetEntries() > 0:
            fit_l1 = int(h_res_l1.Fit("gaus", "Q", "R", h_res_l1.GetMean() - 1. * h_res_l1.GetRMS(), h_res_l1.GetMean() + 1. * h_res_l1.GetRMS()))
            if fit_l1 == 0:
                widths_l1.append(h_res_l1.GetFunction("gaus").GetParameter(2))
                widths_l1_err.append(h_res_l1.GetFunction("gaus").GetParError(2))
            else:
                # fallback - use raw width if no good fit
                print "Poor fit to l1 res - using raw values"
                widths_l1.append(h_res_l1.GetRMS())
                widths_l1_err.append(h_res_l1.GetRMSError())
        else:
            # If there's nothing in the resolution plot, store 0s
            # Not sure if this is smart or not
            print "0 entries in l1 res plot"
            widths_l1.append(0)
            widths_l1_err.append(0)
        output_f.WriteTObject(h_res_l1)

        # Plot resolution wrt Ref pT & fit
        h_res_ref = res_ref_2d.ProjectionY("res_ref_%g_%g" % (ptmin, ptmax), bin_low, bin_high)
        h_res_ref.SetTitle("%g < |#eta| < %g;(E_{T}^{L1} - E_{T}^{Gen})/E_{T}^{Gen};N" % (absetamin, absetamax))
        if h_res_ref.GetEntries() > 0:
            fit_ref = int(h_res_ref.Fit("gaus", "Q", "R", h_res_ref.GetMean() - 1. * h_res_ref.GetRMS(), h_res_ref.GetMean() + 1. * h_res_ref.GetRMS()))
            if fit_ref == 0:
                widths_ref.append(h_res_ref.GetFunction("gaus").GetParameter(2))
                widths_ref_err.append(h_res_ref.GetFunction("gaus").GetParError(2))
            else:
                print "Poor fit to gen res - using raw values"
                widths_ref.append(h_res_ref.GetRMS())
                widths_ref_err.append(h_res_ref.GetRMSError())
        else:
            print "0 entries in gen res plot"
            widths_ref.append(0)
            widths_ref_err.append(0)
        output_f.WriteTObject(h_res_ref)

    # Plot all points on graph Vs Et
    plot_widths(ptBins_in, widths_l1, widths_l1_err, "resL1_%g_%g" % (absetamin, absetamax), "%g < |#eta^{L1}| < %g;E_{T}^{L1} [GeV];E_{T}^{L1} - E_{T}^{Gen}/E_{T}^{L1}" % (absetamin, absetamax))
    plot_widths(ptBins_in, widths_ref, widths_ref_err, "resGen_%g_%g" % (absetamin, absetamax), "%g < |#eta^{L1}| < %g;E_{T}^{L1} [GeV];E_{T}^{L1} - E_{T}^{Gen}/E_{T}^{Gen}" % (absetamin, absetamax))


def plot_widths(pt_bins_in, widths, widths_err, name, title=""):
    """Plot graph of widths Vs Et"""

    # make x points and error bars
    pt_centres = []
    pt_err = []
    for i, pt in enumerate(pt_bins_in[:-1]):
        print "centre", 0.5 * (pt + pt_bins_in[i+1])
        pt_centres.append(0.5 * (pt + pt_bins_in[i+1]))
        pt_err.append(pt_centres[i]-pt)

    if len(widths) != len(pt_centres):
        print len(widths), len(pt_centres)
        raise Exception("incorrect pt bins or widths")

    res_graph = ROOT.TGraphErrors(len(widths), array("d", pt_centres), array("d", widths), array("d", pt_err), array("d", widths_err))
    res_graph.SetNameTitle(name, title)
    res_graph.Write("",ROOT.TObject.kOverwrite)


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
    eta_bins = binning.eta_bins[:2]

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
