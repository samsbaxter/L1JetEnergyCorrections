#!/usr/bin/env python
"""
Script to investigate the 'banding' as seen post calibration,
both in GCT Internal jets, and in normal GCT jets.
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

ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.TH1.SetDefaultSumw2(True)
ROOT.gStyle.SetOptFit(0111) # onyl show fit params and errors
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(False)

def binBand(in_args):

    # TODO: better
    if len(in_args) != 1:
        print "I need a calibration file to get a function from!"
        return
    corr_filename = in_args[0]

    # File with calibration functions
    corr_file = open_root_file(corr_filename)

    # Get correction function for this eta bin
    etaMin, etaMax = binning.eta_bins[0], binning.eta_bins[1]
    corr_fn = get_from_file(corr_file, "fitfcneta_%g_%g" % (etaMin, etaMax))

    # Internal jet pTs, pre calibration
    min_pre = 8
    max_pre = 52
    intern_jet_pt_pre = np.arange(min_pre, max_pre, 0.5)

    # Post calibration
    intern_jet_pt_post = np.array([pt * corr_fn.Eval(pt) for pt in intern_jet_pt_pre])

    # Make coloured blocks to show the bins
    blocks = []
    gct_bins = np.arange(8, 16 + (18*4), 4)
    for i, pt in enumerate(gct_bins):
        if pt+4 < intern_jet_pt_post[0] or pt > intern_jet_pt_post[-1]:
            continue
        b = ROOT.TBox(min_pre, pt, max_pre, pt+4)
        col = 30 if i % 2 else 38
        b.SetFillColor(col)
        b.SetLineStyle(0)
        blocks.append(b)

    # Plot
    c1 = ROOT.TCanvas("c","", 800, 800)
    c1.SetTicks(1, 1)
    gr = ROOT.TGraph(len(intern_jet_pt_pre), intern_jet_pt_pre, intern_jet_pt_post)
    gr.SetMarkerColor(ROOT.kRed)
    gr.SetTitle("Input jets at 0.5 GeV intervals;p_{T}^{pre};p_{T}^{post}")
    gr.SetMarkerStyle(2)
    gr.Draw("AP")
    [b.Draw() for b in blocks]
    gr.Draw("P")
    c1.SaveAs("binBanding.pdf")

    # Make hists of pre & post occupancy
    h_pre = ROOT.TH1D("h_pre", ";p_{T};N", len(gct_bins)-1, gct_bins[0], gct_bins[-1])
    h_post = ROOT.TH1D("h_post", ";p_{T};N", len(gct_bins)-1, gct_bins[0], gct_bins[-1])

    for pt in intern_jet_pt_pre:
        h_pre.Fill(pt)

    for pt in intern_jet_pt_post:
        h_post.Fill(pt)

    h_post.SetLineColor(ROOT.kRed)
    h_pre.Draw("HIST")
    h_post.Draw("SAMEHIST")

    leg = ROOT.TLegend(0.7, 0.7, 0.8, 0.8)
    leg.SetFillColor(ROOT.kWhite)
    leg.AddEntry(h_pre, "Pre", "L")
    leg.AddEntry(h_post, "Post", "L")
    leg.Draw()
    c1.SaveAs("binBandingHist.pdf")


if __name__ == "__main__":
    binBand(sys.argv[1:])