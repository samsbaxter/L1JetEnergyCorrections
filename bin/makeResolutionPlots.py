"""
This script takes as input the output file from RunMatcher, and loops over
matched genjet/L1 jet pairs, making resolution plots.

Usage: see
python makeResolutionPlots -h

"""

import ROOT
import sys
import array
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
ROOT.gROOT.LoadMacro("tdrstyle.C");
ROOT.setTDRStyle();
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
        output_f_hists.WriteTObject(h_res_l1)

        c1 = ROOT.gROOT.FindObject("c1")
        c1.SaveAs("resL1.pdf")

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
        output_f_hists.WriteTObject(h_res_ref)

        c1 = ROOT.gROOT.FindObject("c1")
        c1.SaveAs("resGen.pdf")

########### MAIN ########################
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input ROOT filename")
    parser.add_argument("output", help="output ROOT filename")
    args = parser.parse_args()


    inputf = ROOT.TFile(args.input, "READ")
    outputf = ROOT.TFile(args.output, "RECREATE")
    print args.input
    print args.output

    if not inputf or not outputf:
        raise Exception("Couldn't open input or output files")

    # Setup pt, eta bins for doing calibrations
    ptBins = binning.pt_bins[:5]
    ptBinsWide = binning.pt_bins_wide # larger bins at higher pt
    etaBins = binning.eta_bins[:2]

    print "Running over eta bins:", etaBins
    print "Running over pT bins:", ptBins

    # Do plots for individual eta bins
    for i,eta in enumerate(etaBins[0:-1]):
        emin = eta
        emax = etaBins[i+1]
        if emin >= 3.:
            plot_resolution(inputf, outputf, ptBinsWide, emin, emax)
        else:
            plot_resolution(inputf, outputf, ptBins, emin, emax)

    # Do plots for inclusive eta
    if len(etaBins) > 2:
        plot_resolution(inputf, outputf, ptBins, etaBins[0], etaBins[-1])

if __name__ == "__main__":
    main()
