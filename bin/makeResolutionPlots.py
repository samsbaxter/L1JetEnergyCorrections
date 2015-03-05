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


def plot_resolution(inputfile, outputfile, ptBins_in, absetamin, absetamax, widths_l1, widths_ref):
    """
    Do various resolution plots for given eta bin, for all pT bins

    Stores widths of fitted gaussians in widths_l1 and widths_ref args.
    """

    print "Doing eta bin: %g - %g" % (absetamin, absetamax)

    # Input tree
    tree_raw = inputfile.Get("valid")

    # Output folders
    output_f = outputfile.mkdir('eta_%g_%g' % (absetamin, absetamax))
    output_f_hists = output_f.mkdir("Histograms")

    # Eta cut string
    eta_cut = " TMath::Abs(eta)<%g && TMath::Abs(eta) > %g " % (absetamax, absetamin)

    ptBins = ptBins_in
    for i, ptmin in enumerate(ptBins[0:-1]):
        ptmax = ptBins[i+1]
        pt_cut = "pt < %g && pt > %g" % (ptmax, ptmin)
        print "    Doing pt bin: %g - %g" % (ptmin, ptmax)

        nbins = 100

        # Plot difference in L1 pT and Gen pT
        if check_var_stored(tree_raw, "ptDiff"):
            tree_raw.Draw("ptDiff>>diffPt(%d)" % nbins, eta_cut + " && " + pt_cut)
        else:
            tree_raw.Draw("pt-(pt*rsp)>>diffPt(%d)" % nbins, eta_cut + " && " + pt_cut)
        h_diffPt = ROOT.gROOT.FindObject("diffPt")
        h_diffPt.SetName("diffPt_%g_%g" % (ptmin, ptmax))
        h_diffPt.SetTitle("%g < |#eta| < %g;E_{T}^{L1} - E_{T}^{Gen} [GeV];N" % (absetamin, absetamax))
        output_f_hists.WriteTObject(h_diffPt)

        # Plot resolution wrt L1 pT & fit
        res_min = -3
        res_max = 2
        var = "resL1"
        if not check_var_stored(tree_raw, var):
            var = "(pt-(pt*rsp))/pt"
        tree_raw.Draw("%s>>res_l1(%d, %g, %g)" % (var, nbins, res_min, res_max), eta_cut + " && " + pt_cut)
        h_res_l1 = ROOT.gROOT.FindObject("res_l1")
        h_res_l1.SetName("res_l1_%g_%g" % (ptmin, ptmax))
        h_res_l1.SetTitle("%g < |#eta| < %g;(E_{T}^{L1} - E_{T}^{Gen})/E_{T}^{L1};N" % (absetamin, absetamax))
        if h_res_l1.GetEntries() > 0:
            fit_l1 = int(h_res_l1.Fit("gaus", "Q", "R", h_res_l1.GetMean() - 1. * h_res_l1.GetRMS(), h_res_l1.GetMean() + 1. * h_res_l1.GetRMS()))
            if fit_l1 == 0:
                widths_l1.append(h_res_l1.GetFunction("gaus").GetParameter(2))
            else:
                append(-1)
        output_f_hists.WriteTObject(h_res_l1)

        # Plot resolution wrt Ref pT & fit
        var = "resRef"
        if not check_var_stored(tree_raw, var):
            var = "(pt-(pt*rsp))/(pt*rsp)"
        tree_raw.Draw("%s>>res_ref(%d, %g, %g)" % (var, nbins, res_min, res_max), eta_cut + " && " + pt_cut)
        h_res_ref = ROOT.gROOT.FindObject("res_ref")
        h_res_ref.SetName("res_ref_%g_%g" % (ptmin, ptmax))
        h_res_ref.SetTitle("%g < |#eta| < %g;(E_{T}^{L1} - E_{T}^{Gen})/E_{T}^{Gen};N" % (absetamin, absetamax))
        if h_res_ref.GetEntries() > 0:
            fit_ref = int(h_res_ref.Fit("gaus", "Q", "R", h_res_ref.GetMean() - 1. * h_res_ref.GetRMS(), h_res_ref.GetMean() + 1. * h_res_ref.GetRMS()))
            if fit_ref == 0:
                widths_ref.append(h_res_ref.GetFunction("gaus").GetParameter(2))
            else:
                widths_ref.append(-1)
        output_f_hists.WriteTObject(h_res_ref)


def plot_widths(pt_bins, widths, name, title=""):
    """Plot graph of widths Vs Et"""

    # make x points and error bars
    pt_centres = []
    pt_err = []

    for i, pt in enumerate(pt_bins[:-1]):
        pt_centres.append(0.5 * (pt + pt_bins[i+1]))
        pt_err.append(pt_centres[i]-pt)

    if len(widths) != len(pt_centres):
        raise Exception("incorrect pt bins or widths")

    # make y error bars
    width_err = []
    for w in widths:
        width_err.append(0)

    res_graph = ROOT.TGraphErrors(len(widths), array("d", pt_centres), array("d", widths), array("d", pt_err), array("d", width_err))
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
    pt_bins = binning.pt_bins[:3]
    pt_bins_wide = binning.pt_bins_wide # larger bins at higher pt
    eta_bins = binning.eta_bins[:3]

    print "Running over eta bins:", eta_bins
    print "Running over pT bins:", pt_bins

    # Do plots for individual eta bins
    if args.excl:
        print "Doing individual eta bins"
        for i,eta in enumerate(eta_bins[0:-1]):
            emin = eta
            emax = eta_bins[i+1]
            widths_l1 = []
            widths_ref = []
            # diff binning for forward region
            if emin >= 3.:
                plot_resolution(inputf, outputf, pt_bins_wide, emin, emax, widths_l1, widths_ref)
                plot_widths(pt_bins_wide, widths_l1, "resL1_%g_%g" % (emin, emax), "%g < |#eta^{L1}| < %g;E_{T}^{L1} [GeV];E_{T}^{L1} - E_{T}^{Gen}/E_{T}^{L1}" % (emin, emax))
                plot_widths(pt_bins_wide, widths_ref, "resGen_%g_%g" % (emin, emax), "%g < |#eta^{L1}| < %g;E_{T}^{L1} [GeV];E_{T}^{L1} - E_{T}^{Gen}/E_{T}^{Gen}" % (emin, emax))
            else:
                plot_resolution(inputf, outputf, pt_bins, emin, emax, widths_l1, widths_ref)
                plot_widths(pt_bins, widths_l1, "resL1_%g_%g" % (emin, emax), "%g < |#eta^{L1}| < %g;E_{T}^{L1} [GeV];E_{T}^{L1} - E_{T}^{Gen}/E_{T}^{L1}" % (emin, emax))
                plot_widths(pt_bins, widths_ref, "resGen_%g_%g" % (emin, emax), "%g < |#eta^{L1}| < %g;E_{T}^{L1} [GeV];E_{T}^{L1} - E_{T}^{Gen}/E_{T}^{Gen}" % (emin, emax))


    # Do plots for inclusive eta
    # Skip if doing exlcusive and only 2 bins, or if only 1 bin
    if args.incl and ((not args.excl and len(eta_bins) >= 2) or (args.excl and len(eta_bins)>2):
        print "Doing inclusive eta"
        widths_l1_all = []
        widths_ref_all = []
        plot_resolution(inputf, outputf, pt_bins, eta_bins[0], eta_bins[-1], widths_l1_all, widths_ref_all)
        plot_widths(pt_bins, widths_l1_all, "resL1_allEta", "%g < |#eta^{L1}| < %g;E_{T}^{L1} [GeV];E_{T}^{L1} - E_{T}^{Gen}/E_{T}^{L1}" % (eta_bins[0], eta_bins[-1]))
        plot_widths(pt_bins, widths_ref_all, "resRef_allEta", "%g < |#eta^{L1}| < %g;E_{T}^{L1} [GeV];E_{T}^{L1} - E_{T}^{Gen}/E_{T}^{Gen}" % (eta_bins[0], eta_bins[-1]))


if __name__ == "__main__":
    main()
