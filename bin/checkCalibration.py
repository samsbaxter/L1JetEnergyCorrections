#!/usr/bin/env python
"""
This script takes as input the output file from RunMatcher, and loops over
matched genjet/L1 jet pairs, producing some plots that show off how
calibrated (or uncalibrated) the jets are.

Usage: see
python checkCalibration.py -h

"""

import ROOT
import sys
import array
import numpy as np
from pprint import pprint
from itertools import izip
import os
import argparse
import binning

ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(1)
ROOT.gStyle.SetOptFit(1111)


def plot_checks(inputfile, outputfile, absetamin, absetamax, max_pt, save_pdf=False):
    """
    Do all the relevant response 1D and 2D hists, for one eta bin.

    Can optionally impose maximum pt cut on L1 jets (to avoid problems with saturation).

    Can optionally save the plots to pdf.
    """

    print "Doing eta bin: %g - %g, max L1 jet pt: %g" % (absetamin, absetamax, max_pt)

    # Input tree
    tree_raw = inputfile.Get("valid")

    # Output folders
    output_f = outputfile.mkdir('eta_%g_%g' % (absetamin, absetamax))
    output_f_hists = output_f.mkdir("Histograms")

    # Eta cut string
    eta_cutStr = " TMath::Abs(eta)<%g && TMath::Abs(eta) > %g " % (absetamax, absetamin)
    # Pt cut string
    pt_cutStr = "pt < %g" % max_pt

    cutStr = eta_cutStr + " && " + pt_cutStr

    # Draw response (pT^L1/pT^Gen) for all pt bins
    tree_raw.Draw("rsp>>hrsp_eta_%g_%g(50,0,5)" % (absetamin, absetamax) , cutStr)
    hrsp_eta = ROOT.gROOT.FindObject("hrsp_eta_%g_%g" % (absetamin, absetamax))
    hrsp_eta.SetTitle(";response (p_{T}^{L1}/p_{T}^{Gen});")
    output_f_hists.WriteTObject(hrsp_eta)

    nb_pt = 63
    pt_min, pt_max = 0, 252
    nb_rsp = 100
    rsp_min, rsp_max = 0, 5

    # Draw rsp (pT^L1/pT^Gen) Vs GenJet pT
    tree_raw.Draw("rsp:ptRef>>h2d_rsp_gen(%d,%g,%g,%d,%g,%g)" % (nb_pt, pt_min, pt_max, nb_rsp, rsp_min, rsp_max), cutStr)
    h2d_rsp_gen = ROOT.gROOT.FindObject("h2d_rsp_gen")
    h2d_rsp_gen.SetTitle(";p_{T}^{Gen} [GeV];response (p_{T}^{L1}/p_{T}^{Gen})")
    output_f_hists.WriteTObject(h2d_rsp_gen)

    # Draw rsp (pT^L1/pT^Gen) Vs L1 pT
    tree_raw.Draw("rsp:pt>>h2d_rsp_l1(%d,%g,%g,%d,%g,%g)" % (nb_pt, pt_min, pt_max, nb_rsp, rsp_min, rsp_max), cutStr)
    h2d_rsp_l1 = ROOT.gROOT.FindObject("h2d_rsp_l1")
    h2d_rsp_l1.SetTitle(";p_{T}^{L1} [GeV];response (p_{T}^{L1}/p_{T}^{Gen})")
    output_f_hists.WriteTObject(h2d_rsp_l1)

    # Draw pT^Gen Vs pT^L1
    tree_raw.Draw("pt:ptRef>>h2d_gen_l1(%d,%g,%g,%d,%g,%g)" % (nb_pt, pt_min, pt_max, nb_pt, pt_min, pt_max), cutStr)
    h2d_gen_l1 = ROOT.gROOT.FindObject("h2d_gen_l1")
    h2d_gen_l1.SetTitle(";p_{T}^{Gen} [GeV];p_{T}^{L1} [GeV]")
    output_f_hists.WriteTObject(h2d_gen_l1)

    # Save plots as pdf if desired
    if save_pdf:
        canv = ROOT.TCanvas("c_%g_%g" % (absetamin, absetamax), "", 600, 600)
        # One linefor y = x (diag) and one for y = 1 (straight)
        line_diag = ROOT.TLine(0, 0, pt_max, pt_max)
        line_straight = ROOT.TLine(0, 1, pt_max, 1)

        for l in [line_diag, line_straight]:
            l.SetLineWidth(2)
            l.SetLineStyle(2)

        h2d_rsp_gen.Draw("COLZ")
        line_straight.Draw("SAME")
        canv.SaveAs("rsp_gen_%g_%g.pdf" % (absetamin, absetamax))

        h2d_gen_l1.Draw("COLZ")
        line_diag.Draw("SAME")
        canv.SaveAs("gen_l1_%g_%g.pdf" % (absetamin, absetamax))

        h2d_rsp_l1.Draw("COLZ")
        line_straight.Draw("SAME")
        canv.SaveAs("rsp_l1_%g_%g.pdf" % (absetamin, absetamax))


def plot_rsp_eta(inputfile, outputfile, eta_bins, max_pt):
    """Plot graph of response in bins of eta

    If the response hist for each bin exists already, then we use that.
    If not, we make the hist.
    """

    gr_rsp_eta = ROOT.TGraphErrors()

    # Input tree
    tree_raw = inputfile.Get("valid")

    # Output folders
    output_f = outputfile.GetDirectory('eta_%g_%g' % (eta_bins[0], eta_bins[-1]))
    output_f_hists = None
    if not output_f:
        output_f = outputfile.mkdir('eta_%g_%g' % (eta_bins[0], eta_bins[-1]))
        output_f_hists = output_f.mkdir("Histograms")
    else:
        output_f_hists = output_f.GetDirectory("Histograms")

    # Go through eta bins, get response hist, fit with Gaussian and add to
    # the overall graph
    for i,eta in enumerate(eta_bins[:-1]):
        absetamin = eta
        absetamax = eta_bins[i+1]    # Eta cut string

        # Figure out if we've made a response hist already:
        rsp_name = "hrsp_eta_%g_%g" % (absetamin, absetamax)
        h_rsp = outputfile.GetDirectory("eta_%g_%g/Histograms" % (absetamin, absetamax)).Get(rsp_name)
        if not h_rsp:
            # plot response for this eta bin
            cutStr = "pt>%g && TMath::Abs(eta)<%g && TMath::Abs(eta) > %g " % (max_pt, absetamax, absetamin)
            nb_rsp = 100
            rsp_min, rsp_max = 0, 5
            tree_raw.Draw("rsp>>%s(%d,%g,%g)" % (rsp_name, nb_rsp, rsp_min, rsp_max), cutStr)
            h_rsp = ROOT.gROOT.FindObject(rsp_name)
            h_rsp.SetTitle(";response (p_{T}^{L1}/p_{T}^{Gen});")

        # Fit with Gaussian
        fit_result = h_rsp.Fit("gaus", "QER", "", h_rsp.GetMean() - h_rsp.GetRMS(), h_rsp.GetMean() + h_rsp.GetRMS())
        mean = h_rsp.GetFunction("gaus").GetParameter(1)
        err = h_rsp.GetFunction("gaus").GetParError(1)

        check_fit = False
        if check_fit:
            if fit_result != 0:
                print "cannot fit with Gaussian - using raw mean instead"
                mean = h_rsp.GetMean()
                err = h_rsp.GetMeanError()

        output_f_hists.WriteTObject(h_rsp)

        # add to graph
        N = gr_rsp_eta.GetN()
        gr_rsp_eta.SetPoint(N, 0.5 * (absetamin + absetamax), mean)
        gr_rsp_eta.SetPointError(N, 0.5 * (absetamax - absetamin), err)

    gr_rsp_eta.SetTitle(";|#eta^{L1}|; <response> = <p_{T}^{L1}/p_{T}^{Gen}>")
    gr_rsp_eta.SetName("gr_rsp_eta_%g_%g" % (eta_bins[0], eta_bins[-1]))
    output_f.WriteTObject(gr_rsp_eta)


########### MAIN ########################
def main(in_args=sys.argv[1:]):
    print in_args
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="input ROOT filename")
    parser.add_argument("output", help="output ROOT filename")
    parser.add_argument("--central", action='store_true',
                        help="Do central eta bins only (eta <= 3)")
    parser.add_argument("--forward", action='store_true',
                        help="Do forward eta bins only (eta >= 3)")
    parser.add_argument("--pdf", action='store_true',
                        help="Print plots to PDF")
    parser.add_argument("--etaInd", nargs="+",
                        help="list of eta bin INDICES to run over - " \
                        "if unspecified will do all. " \
                        "This overrides --central/--forward. " \
                        "Handy for batch mode. " \
                        "IMPORTANT: MUST PUT AT VERY END")
    parser.add_argument("--maxPt", default=500, type=float,
                        help="Maximum pT for L1 Jets")
    args = parser.parse_args(args=in_args)

    # Open input & output files, check
    inputf = ROOT.TFile(args.input, "READ")
    output_f = ROOT.TFile(args.output, "RECREATE")
    print "IN:", args.input
    print "OUT:", args.output
    if not inputf or not output_f:
        raise Exception("Input or output files cannot be opened")

    etaBins = binning.eta_bins
    if args.etaInd:
        args.etaInd.append(int(args.etaInd[-1])+1) # need upper eta bin edge
        # check eta bins are ok
        etaBins = [etaBins[int(x)] for x in args.etaInd]
    elif args.central:
        etaBins = [eta for eta in etaBins if eta < 3.1]
    elif args.forward:
        etaBins = [eta for eta in etaBins if eta > 2.9]
    print "Running over eta bins:", etaBins

    # Do plots for each eta bin
    fit_params = []
    for i,eta in enumerate(etaBins[:-1]):
        emin = eta
        emax = etaBins[i+1]

        plot_checks(inputf, output_f, emin, emax, args.maxPt, args.pdf)

    # Do an inclusive plot for all eta bins
    if len(etaBins) > 2:
        plot_checks(inputf, output_f, etaBins[0], etaBins[-1], args.maxPt, args.pdf)

    # Do a response vs eta graph
    plot_rsp_eta(inputf, output_f, etaBins, args.maxPt, )


if __name__ == "__main__":
    main()