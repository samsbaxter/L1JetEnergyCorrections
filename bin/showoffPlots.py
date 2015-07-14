#!/usr/bin/env python
"""
This script produces plots for showing off in notes/presentations, etc.

Deisgned to be quick! So just pull the histograms, apply some aesthetics, save.

It takes in ROOT files made by:
- RunMatcher
- makeResolutionPlots.py
- checkCalibration.py
- runCalibration.py

Robin Aggleton
"""


import ROOT
import sys
import numpy as np
import binning
import argparse
from subprocess import call
from subprocess import check_output
from sys import platform as _platform
from itertools import izip
from common_utils import *
from array import array


ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.TH1.SetDefaultSumw2(True)
ROOT.gStyle.SetOptFit(1) # only show fit params and errors
# ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(True)

ptBins = binning.pt_bins

# Some common strings
rsp_str = "E_{T}^{L1}/E_{T}^{Ref}"
eta_str = "#eta"
eta_ref_str = "|#eta^{Ref}|"
eta_l1_str = "|#eta^{L1}|"
dr_str = "#DeltaR(L1 jet - Ref jet)"
pt_str = "E_{T}[GeV]"
pt_L1_str = "E_{T}^{L1} [GeV]"
pt_Ref_str = "E_{T}^{Ref} [GeV]"
res_l1_str = "#sigma(E_{T}^{L1} - E_{T}^{Ref})/<E_{T}^{L1}>"
pt_diff_str = "E_{T}^{L1} - E_{T}^{Ref} [GeV]"

# compare_1_str = "Old calibration"
# compare_1_str = "2012 RCT calibration, 2012 GCT calibration (GCT jets)"
# compare_2_str = "New RCT calibration, 2012 GCT calibration (GCT jets)"
# compare_3_str = "New RCT calibration, new GCT calibration (GCT jets)"

plot_labels = [
    #"New RCT calibration, 2012 GCT calibration (GCT jets), Phys14",
    #"New RCT calibration, 2012 GCT calibration (GCT jets), Spring15"
     "2012 RCT calibration, 2012 GCT calibratiion, Spring15",
     "New RCT calibration, 2012 GCT calibration, Spring15",
     "New RCT calibration, new GCT calibration, Spring15"
    ]
plot_colors = [ROOT.kBlack, ROOT.kRed, ROOT.kBlue, 8]
plot_markers = [20, 21, 22, 23]

# compare_1_str = "2012 RCT calibration (GCT internal jets)"
# compare_2_str = "New RCT calibration (GCT internal jets)"

# compare_1_str = "New RCT + 2012 GCT"
# compare_2_str = "New RCT + new RCT"

plot_title = "QCD 50ns"
plot_title = "TTbar 50ns, GCT jets"


def generate_canvas(title=""):
    """Generate a standard TCanvas for all plots"""
    c = ROOT.TCanvas("c", title, 1200, 800)
    c.SetTicks(1, 1)
    return c

#############################################
# PLOTS USING OUTPUT FROM RunMatcher
#############################################

def plot_dR(tree, oDir, cut="1", eta_min=0, eta_max=5, oFormat="pdf"):
    """Plot deltaR(L1 - RefJet)"""
    c = generate_canvas()
    tree.Draw("dr>>h_dr(40,0,0.8)", cut + "&& TMath::Abs(eta)>%g && TMath::Abs(eta)<%g" % (eta_min, eta_max), "HISTE")
    h_dr = ROOT.gROOT.FindObject("h_dr")
    h_dr.SetTitle(cut + "&& TMath::Abs(eta)>%g && TMath::Abs(eta)<%g;%s;N" % (eta_min, eta_max, dr_str))
    c.SaveAs("%s/dr_%g_%g.%s" % (oDir, eta_min, eta_max, oFormat))


def plot_pt_l1(tree, oDir, cut="1", eta_min=0, eta_max=5, oFormat="pdf"):
    """Plot pT(L1)"""
    c = generate_canvas()
    tree.Draw("pt>>h_pt(63,0,252)", cut + "&& TMath::Abs(eta)>%g && TMath::Abs(eta)<%g" % (eta_min, eta_max), "HISTE")
    h_pt = ROOT.gROOT.FindObject("h_pt")
    h_pt.SetTitle(cut + "&& TMath::Abs(eta)>%g && TMath::Abs(eta)<%g;%s;N" % (eta_min, eta_max, pt_L1_str))
    c.SaveAs("%s/pt_l1_%g_%g.%s" % (oDir, eta_min, eta_max, oFormat))


def plot_eta_l1(tree, oDir, cut="1", oFormat="pdf"):
    """Plot eta(L1)"""
    c = generate_canvas()
    h_eta = ROOT.TH1D("h_eta", "%s;%s;N" % (cut, eta_l1_str), len(binning.eta_bins_all)-1, array('d', binning.eta_bins_all))
    tree.Draw("eta>>h_eta", cut, "HISTE")
    c.SaveAs("%s/eta_l1.%s" % (oDir, oFormat))


def plot_pt_ref(tree, oDir, cut="1", eta_min=0, eta_max=5, oFormat="pdf"):
    """Plot pT(Reference)"""
    c = generate_canvas()
    tree.Draw("ptRef>>h_pt(63,0,252)", cut + "&& TMath::Abs(eta)>%g && TMath::Abs(eta)<%g" % (eta_min, eta_max), "HISTE")
    h_pt = ROOT.gROOT.FindObject("h_pt")
    h_pt.SetTitle(cut + "&& TMath::Abs(eta)>%g && TMath::Abs(eta)<%g;%s;N" % (eta_min, eta_max, pt_Ref_str))
    c.SaveAs("%s/pt_ref_%g_%g.%s" % (oDir, eta_min, eta_max, oFormat))


def plot_eta_ref(tree, oDir, cut="1", oFormat="pdf"):
    """Plot eta(Reference)"""
    c = generate_canvas()
    h_eta = ROOT.TH1D("h_eta", "%s;%s;N" % (cut, eta_ref_str), len(binning.eta_bins_all)-1, array('d', binning.eta_bins_all))
    tree.Draw("etaRef>>h_eta", cut, "HISTE")
    c.SaveAs("%s/eta_ref.%s" % (oDir, oFormat))


def plot_pt_both(tree, oDir, cut="1", eta_min=0, eta_max=5, oFormat="pdf"):
    """Plot pt(Reference) and pt(L1) on same plot"""
    c = generate_canvas()
    total_cut = cut + " && TMath::Abs(eta) > %g && TMath::Abs(eta) < %g" % (eta_min, eta_max)
    h_pt_l1 = ROOT.TH1D("h_pt_l1", "%s;%s;N" % (total_cut, pt_str), 63, 0, 252)
    h_pt_ref = ROOT.TH1D("h_pt_ref", "%s;%s;N" % (total_cut, pt_str), 63, 0, 252)
    tree.Draw("pt>>h_pt_l1", cut + " && TMath::Abs(eta) > %g && TMath::Abs(eta) < %g" % (eta_min, eta_max), "HISTE")
    tree.Draw("ptRef>>h_pt_ref", cut + " && TMath::Abs(eta) > %g && TMath::Abs(eta) < %g" % (eta_min, eta_max), "HISTE")
    h_pt_ref.SetLineColor(ROOT.kRed)
    stack = ROOT.THStack("st", "")
    stack.Add(h_pt_l1)
    stack.Add(h_pt_ref)
    stack.Draw("NOSTACK HISTE")
    print total_cut
    stack.GetHistogram().SetTitle("%s;%s;N" % (total_cut, pt_str))
    c.SetTitle(total_cut)
    leg = ROOT.TLegend(0.7, 0.7, 0.88, 0.88)
    leg.AddEntry(0, "|#eta|: %g - %g" %(eta_min, eta_max), "")
    leg.AddEntry(h_pt_l1, "L1", "L")
    leg.AddEntry(h_pt_ref, "Ref", "L")
    leg.Draw()
    c.SaveAs("%s/pt_both_%g_%g.%s" % (oDir, eta_min, eta_max, oFormat))


def plot_eta_both(tree, oDir, cut="1", oFormat="pdf"):
    """Plot eta(Reference) and eta(L1) on same plot"""
    c = generate_canvas()
    h_eta_l1 = ROOT.TH1D("h_eta_l1", "%s;%s;N" % (cut, eta_str), len(binning.eta_bins_all)-1, array('d', binning.eta_bins_all))
    h_eta_ref = ROOT.TH1D("h_eta_ref", "%s;%s;N" % (cut, eta_str), len(binning.eta_bins_all)-1, array('d', binning.eta_bins_all))
    tree.Draw("eta>>h_eta_l1", cut, "HISTE")
    tree.Draw("etaRef>>h_eta_ref", cut, "HISTE")
    h_eta_ref.SetLineColor(ROOT.kRed)
    h_eta_l1.Draw("HISTE")
    h_eta_ref.Draw("HISTE SAME")
    leg = ROOT.TLegend(0.7, 0.7, 0.88, 0.88)
    leg.AddEntry(h_eta_l1, "L1", "L")
    leg.AddEntry(h_eta_ref, "Ref", "L")
    leg.Draw()
    c.SaveAs("%s/eta_both.%s" % (oDir, oFormat))


#############################################
# PLOTS USING OUTPUT FROM makeResolutionPlots
#############################################

def plot_pt_diff(res_file, eta_min, eta_max, pt_min, pt_max, oDir, oFormat="pdf"):
    """Plot the difference between L1 and ref jet pT, for given L1 pT, eta bin"""
    hname = "eta_%g_%g/Histograms/ptDiff_l1_%g_%g" % (eta_min, eta_max, pt_min, pt_max)
    h_diff = get_from_file(res_file, hname)
    c = generate_canvas()
    h_diff.Draw()
    h_diff.SetMaximum(h_diff.GetMaximum()*1.2)
    # h_diff.SetLineWidth(2)
    func = h_diff.GetListOfFunctions().At(0)
    func.SetLineWidth(1)
    h_diff.SetTitle("%g < |#eta^{L1}| < %g, %g < p_{T}^{L1} < %g;%s;N" % (eta_min, eta_max, pt_min, pt_max, pt_diff_str))
    c.SaveAs("%s/pt_diff_eta_%g_%g_%g_%g.%s" % (oDir, eta_min, eta_max, pt_min, pt_max, oFormat))


def plot_res_pt_bin(res_file, eta_min, eta_max, pt_min, pt_max, oDir, oFormat="pdf"):
    """Plot the L1 resolution for given L1 pT, eta bin"""
    hname = "eta_%g_%g/Histograms/res_l1_%g_%g" % (eta_min, eta_max, pt_min, pt_max)
    h_res = get_from_file(res_file, hname)
    c = generate_canvas()
    h_res.Draw()
    h_res.SetAxisRange(-2, 2, "X")
    h_res.SetTitle(";%s;N" % res_l1_str)
    c.SaveAs("%s/res_l1_eta_%g_%g_%g_%g.%s" % (oDir, eta_min, eta_max, pt_min, pt_max, oFormat))


def plot_res_all_pt(res_files, eta_min, eta_max, oDir, oFormat="pdf"):
    """Plot a graph of resolution as a function of L1 eta.

    Can optionally do comparison against another file,
    in which case res_file1 is treated as before calibration,
    whilst res_file2 is treated as after calibration.
    """
    grname = "eta_%g_%g/resL1_%g_%g_diff" % (eta_min, eta_max, eta_min, eta_max)

    graphs = [get_from_file(f, grname) for f in res_files if f]

    c = generate_canvas()

    leg = ROOT.TLegend(0.34, 0.56, 0.87, 0.87)

    mg = ROOT.TMultiGraph()
    for i, g in enumerate(graphs):
        g.SetLineColor(plot_colors[i] if i < len(plot_colors) else ROOT.kBlack)
        g.SetMarkerColor(plot_colors[i] if i < len(plot_colors) else ROOT.kBlack)
        g.SetMarkerStyle(plot_markers[i] if i < len(plot_markers) else ROOT.kBlack)
        mg.Add(g)
        leg.AddEntry(g, plot_labels[i] if i < len(plot_labels) else "", "LP")

    mg.Draw("ALP")
    mg.SetTitle("%s;%s;%s" % (plot_title, graphs[0].GetXaxis().GetTitle(), graphs[0].GetYaxis().GetTitle()))
    mg.GetXaxis().SetTitleSize(0.04)
    mg.GetXaxis().SetTitleOffset(0.9)
    mg.GetYaxis().SetTitle(res_l1_str)
    mg.GetYaxis().SetRangeUser(0, mg.GetYaxis().GetXmax())
    mg.Draw("ALP")
    leg.Draw()
    c.SaveAs("%s/res_l1_eta_%g_%g_diff_compare.%s" % (oDir, eta_min, eta_max, oFormat))


def plot_eta_pt_rsp_2d(calib_file, etaBins, ptBins, oDir, oFormat='pdf'):
    """
    Plot a 2D map of response for each eta, pt bin. Display the <response> from
    Gaussian fit of response hist in that bin

    Uses the resolution output file, since this plot of rsp & fit for pT(L1) bin,
    and will be done for pre and post calib, whereas output from runCalibration
    will generally only be pre calib, and is binned by ref Jet pt
    """
    h_2d = ROOT.TH2D("h2d_eta_pt_rsp", ";p_{T}^{L1} [GeV];|#eta^{L1}|",
                     len(ptBins)-1, array('d', ptBins),
                     len(etaBins)-1, array('d', etaBins))
    for eta_ind, (eta_min, eta_max) in enumerate(zip(etaBins[:-1], etaBins[1:]), 1):
        for pt_ind, (pt_min, pt_max) in enumerate(zip(ptBins[:-1], ptBins[1:]), 1):
            h_rsp = get_from_file(calib_file, "eta_%g_%g/Histograms/res_l1_%g_%g" % (eta_min, eta_max, pt_min, pt_max))
            if h_rsp.GetEntries() > 0:
                # we actually use the fit to (L1-Gen)/L1, so we need to * -1 and invert
                res = h_rsp.GetListOfFunctions().At(0).GetParameter(1)
                rsp = 1./(1 - res)
                print rsp
                h_2d.SetBinContent(pt_ind, eta_ind, rsp)
            else:
                h_2d.SetBinContent(pt_ind, eta_ind, 0)
    c = generate_canvas()
    ROOT.gStyle.SetPaintTextFormat(".2f")
    ROOT.gStyle.SetPalette(56)
    h_2d.Draw("COLZTEXT")
    h_2d.GetZaxis().SetRangeUser(0,2)
    c.SaveAs("%s/h2d_eta_pt_rsp.%s" % (oDir, oFormat))

#############################################
# PLOTS USING OUTPUT FROM checkCalibration
#############################################

def plot_l1_Vs_ref(check_file, eta_min, eta_max, oDir, oFormat="pdf"):
    """Plot l1 pt against ref jet pt, for given L1 eta bin"""
    hname = "eta_%g_%g/Histograms/h2d_gen_l1" % (eta_min, eta_max)
    h2d_gen_l1 = get_from_file(check_file, hname)
    c = generate_canvas()
    h2d_gen_l1.Draw("COLZ")
    line = ROOT.TLine(0, 0, 250, 250)
    line.SetLineStyle(2)
    line.SetLineWidth(2)
    line.Draw()
    c.SaveAs("%s/h2d_gen_l1_%g_%g.%s" % (oDir, eta_min, eta_max, oFormat))


def plot_rsp_eta(check_files, eta_min, eta_max, oDir, oFormat="pdf"):
    """Plot a graph of response vs L1 eta.

    Can optionally do comparison against another file,
    in which case check_file1 is treated as before calibration,
    whilst check_file2 is treated as after calibration.
    """
    grname = "eta_%g_%g/gr_rsp_eta_%g_%g" % (eta_min, eta_max, eta_min, eta_max)

    graphs = [get_from_file(f, grname) for f in check_files if f]

    c = generate_canvas(plot_title)

    # leg = ROOT.TLegend(0.4, 0.7, 0.87, 0.87) # top right
    leg = ROOT.TLegend(0.34, 0.15, 0.87, 0.4) # bottom right

    mg = ROOT.TMultiGraph()

    for i, g in enumerate(graphs):
        g.GetYaxis().SetRangeUser(0, 2)
        g.GetXaxis().SetLimits(eta_min, eta_max)
        g.SetLineColor(plot_colors[i] if i < len(plot_colors) else ROOT.kBlack)
        g.SetMarkerColor(plot_colors[i] if i < len(plot_colors) else ROOT.kBlack)
        g.SetMarkerStyle(plot_markers[i] if i < len(plot_markers) else 20)
        mg.Add(g)
        leg.AddEntry(g, plot_labels[i] if i < len(plot_labels) else "", "LP")

    line_central = ROOT.TLine(eta_min, 1, eta_max, 1)
    line_plus = ROOT.TLine(eta_min, 1.1, eta_max, 1.1)
    line_minus = ROOT.TLine(eta_min, 0.9, eta_max, 0.9)
    line_central.SetLineWidth(2)
    line_central.SetLineStyle(2)
    for line in [line_plus, line_minus]:
        line.SetLineWidth(2)
        line.SetLineStyle(3)

    mg.Draw("ALP")
    mg.SetTitle("%s;%s;%s" % (plot_title, graphs[0].GetXaxis().GetTitle(), graphs[0].GetYaxis().GetTitle()))
    mg.GetYaxis().SetRangeUser(0,2)
    mg.GetXaxis().SetLimits(eta_min, eta_max)
    mg.GetXaxis().SetTitleSize(0.04)
    mg.GetXaxis().SetTitleOffset(0.9)
    # mg.GetYaxis().SetTitleSize(0.04)
    mg.Draw("ALP")
    mg.GetHistogram().SetTitle(plot_title)

    leg.Draw()
    [line.Draw() for line in [line_central, line_plus, line_minus]]
    c.SaveAs("%s/gr_rsp_eta_%g_%g_compare.%s" % (oDir, eta_min, eta_max, oFormat))

#############################################
# PLOTS USING OUTPUT FROM runCalibration
#############################################

def plot_rsp_eta_pt_bin(calib_file, eta_min, eta_max, pt_min, pt_max, oDir, oFormat="pdf"):
    """Plot the response in one pt, eta bin"""
    hname = "eta_%g_%g/Histograms/Rsp_genpt_%g_%g" % (eta_min, eta_max, pt_min, pt_max)
    h_rsp = get_from_file(calib_file, hname)
    c = generate_canvas()
    h_rsp.Draw("HISTE")
    c.SaveAs("%s/h_rsp_%g_%g_%g_%g.%s" % (oDir, eta_min, eta_max, pt_min, pt_max, oFormat))


def plot_rsp_eta_bin(calib_file, eta_min, eta_max, oDir, oFormat="pdf"):
    """Plot the response in one eta bin"""
    hname = "eta_%g_%g/Histograms/hrsp_eta_%g_%g" % (eta_min, eta_max, eta_min, eta_max)
    h_rsp = ROOT.TH1F(get_from_file(calib_file, hname))
    func = h_rsp.GetListOfFunctions().At(0)
    c = generate_canvas()
    h_rsp.Draw("HISTE")
    if func:
        func.Draw("SAME")
    c.SaveAs("%s/h_rsp_%g_%g.%s" % (oDir, eta_min, eta_max, oFormat))


def plot_pt_bin(calib_file, eta_min, eta_max, pt_min, pt_max, oDir, oFormat="pdf"):
    """Plot the L1 pt in a given ref jet pt bin"""
    hname = "eta_%g_%g/Histograms/L1_pt_genpt_%g_%g" % (eta_min, eta_max, pt_min, pt_max)
    h_pt = get_from_file(calib_file, hname)
    c = generate_canvas()
    h_pt.Draw("HISTE")
    c.SaveAs("%s/L1_pt_%g_%g_%g_%g.%s" % (oDir, eta_min, eta_max, pt_min, pt_max, oFormat))


def main(in_args=sys.argv[1:]):
    print in_args
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", help="input ROOT file with matched pairs from RunMatcher")

    parser.add_argument("--res", help="input ROOT file with resolution plots from makeResolutionPlots.py")
    parser.add_argument("--res2", help="optional: 2nd input ROOT file with resolution plots from makeResolutionPlots.py. " \
                                        "If you specify this one, then the file specified by --res will be treated as pre-calibration, " \
                                        "whilst this one will be treated as post-calibration")
    parser.add_argument("--res3", help="optional: 3rd input file for resolution plots")

    parser.add_argument("--checkcal", help="input ROOT file with calibration check plots from checkCalibration.py")
    parser.add_argument("--checkcal2", help="optional: 2nd input ROOT file with resolution plots from checkCalibration.py. " \
                                        "If you specify this one, then the file specified by --checkcal will be treated as pre-calibration, " \
                                        "whilst this one will be treated as post-calibration")
    parser.add_argument("--checkcal3", help="yet another calibration check file")

    parser.add_argument("--calib", help="input ROOT file from output of runCalibration.py")

    parser.add_argument("--oDir", help="Directory to save plots", default=".")
    parser.add_argument("--format", help="Format for plots (PDF, png, etc)", default="pdf")
    parser.add_argument("--etaInd", help="list of eta bin index to run over")

    args = parser.parse_args(args=in_args)

    print args

    # Check if directory exists. If not, create it.
    check_dir_exists_create(args.oDir)

    # Choice eta & pt bin
    eta_min, eta_max = binning.eta_bins[0], binning.eta_bins_central[-1]
    pt_min, pt_max = ptBins[10], ptBins[11]

    if args.etaInd:
        eta_min, eta_max = binning.eta_bins[int(args.etaInd)], binning.eta_bins[int(args.etaInd)+1]

    # Do plots with output from RunMatcher
    if args.pairs:
        pairs_file = open_root_file(args.pairs)
        pairs_tree = get_from_file(pairs_file, "valid")

        # eta binned
        for emin, emax in zip(binning.eta_bins[:-1], binning.eta_bins[1:]):
            plot_dR(pairs_tree, eta_min=emin, eta_max=emax, cut="1", oDir=args.oDir)
            plot_pt_both(pairs_tree, eta_min=emin, eta_max=emax, cut="1", oDir=args.oDir)

        plot_dR(pairs_tree, eta_min=0, eta_max=5, cut="1", oDir=args.oDir)  # all eta
        plot_pt_both(pairs_tree, eta_min=0, eta_max=5, cut="1", oDir=args.oDir)  # all eta
        plot_eta_both(pairs_tree, oDir=args.oDir)  # all eta

        plot_dR(pairs_tree, eta_min=0, eta_max=3, cut="1", oDir=args.oDir)  # central
        plot_pt_both(pairs_tree, eta_min=0, eta_max=3, cut="1", oDir=args.oDir)  # central

        plot_dR(pairs_tree, eta_min=3, eta_max=5, cut="1", oDir=args.oDir)  # forward
        plot_pt_both(pairs_tree, eta_min=3, eta_max=5, cut="1", oDir=args.oDir)  # forward

        pairs_file.Close()

    # Do plots with output from makeResolutionPlots.py
    if args.res:
        res_file = open_root_file(args.res)
        if not args.res2:
            # if not doing comparison
#            pt_min = binning.pt_bins[10]
#            pt_max = binning.pt_bins[11]
            # for the first 4 bins - troublesome
            # for pt_min, pt_max in izip(binning.pt_bins[0:4], binning.pt_bins[1:5]):
#            plot_pt_diff(res_file, eta_min, eta_max, pt_min, pt_max, args.oDir, args.format)
#            plot_res_pt_bin(res_file, eta_min, eta_max, pt_min, pt_max, args.oDir, args.format)

            # exclusive eta graphs
#            for emin, emax in izip(binning.eta_bins_central[:-1], binning.eta_bins_central[1:]):
#                plot_res_all_pt([res_file], emin, emax, args.oDir, args.format)

            # inclusive eta graph
            plot_res_all_pt([res_file], eta_min, eta_max, args.oDir, args.format)

            # plot_eta_pt_rsp_2d(res_file, binning.eta_bins_central, binning.pt_bins, args.oDir, args.format)
        else:
            # if doing comparison
            res_files = [res_file]
            if args.res2:
                res_files.append(open_root_file(args.res2))
            if args.res3:
                res_files.append(open_root_file(args.res3))
            # plot_res_all_pt(res_file, res_file2, eta_min, eta_max, args.oDir, args.format)
#            for emin, emax in izip(binning.eta_bins[:-1], binning.eta_bins[1:]):
#                plot_res_all_pt(res_files, emin, emax, args.oDir, args.format)

            plot_res_all_pt(res_files, binning.eta_bins[0], binning.eta_bins_central[-1], args.oDir, args.format)

        res_file.Close()

    # Do plots with output from checkCalibration.py
    if args.checkcal:

        etaBins = binning.eta_bins_central
        check_file = open_root_file(args.checkcal)

        for emin, emax in izip(etaBins[:-1], etaBins[1:]):
            plot_l1_Vs_ref(check_file, emin, emax, args.oDir, args.format)
            plot_rsp_eta_bin(check_file, emin, emax, args.oDir, args.format)
        plot_l1_Vs_ref(check_file, etaBins[0], etaBins[-1], args.oDir, args.format)

        check_file2 = open_root_file(args.checkcal2) if args.checkcal2 else None
        check_file3 = open_root_file(args.checkcal3) if args.checkcal3 else None
        plot_rsp_eta([check_file, check_file2, check_file3], etaBins[0], etaBins[-1], args.oDir, args.format)

        check_file.Close()

    # Do plots with output from runCalibration.py
    if args.calib:
        calib_file = open_root_file(args.calib)

        plot_rsp_eta_pt_bin(calib_file, eta_min, eta_max, pt_min, pt_max, args.oDir, args.format)
        plot_rsp_eta_bin(calib_file, eta_min, eta_max, args.oDir, args.format)
        plot_pt_bin(calib_file, eta_min, eta_max, pt_min, pt_max, args.oDir, args.format)

        calib_file.Close()


if __name__ == "__main__":
    main()
