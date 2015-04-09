"""
This script takes as input the output file from RunMatcher, and loops over
matched genjet/L1 jet pairs, producing some plots that show off how
calibrated (or uncalibrated) the jets are.

Usage: see
python checkCalibration -h

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


def plot_checks(inputfile, outputfile, absetamin, absetamax):
    """
    Do all the relevant hists, for one eta bin.
    """

    print "Doing eta bin: %g - %g" % (absetamin, absetamax)

    # Input tree
    tree_raw = inputfile.Get("valid")

    # Output folders
    output_f = outputfile.mkdir('eta_%g_%g' % (absetamin, absetamax))
    output_f_hists = output_f.mkdir("Histograms")

    # Eta cut string
    eta_cutStr = " TMath::Abs(eta)<%g && TMath::Abs(eta) > %g " % (absetamax, absetamin)

    canv = ROOT.TCanvas("c_%g_%g" % (absetamin, absetamax), "", 600, 600)

    # Draw response (pT^L1/pT^Gen) for all pt bins
    tree_raw.Draw("rsp>>hrsp_eta_%g_%g(50,0,5)" %(absetamin, absetamax) , eta_cutStr)
    hrsp_eta = ROOT.gROOT.FindObject("hrsp_eta_%g_%g" % (absetamin, absetamax))
    hrsp_eta.SetTitle(";response (p_{T}^{L1}/p_{T}^{Gen});")
    output_f_hists.WriteTObject(hrsp_eta)

    nb_pt = 50
    pt_min, pt_max = 0, 250
    nb_rsp = 100
    rsp_min, rsp_max = 0, 5

    # Straight lines - one for y = x (diag) and one for y = 1 (straight)
    line_diag = ROOT.TLine(0, 0, pt_max, pt_max)
    line_straight = ROOT.TLine(0, 1, pt_max, 1)

    for l in [line_diag, line_straight]:
        l.SetLineWidth(2)
        l.SetLineStyle(2)

    # Draw rsp (pT^L1/pT^Gen) Vs GenJet pT
    tree_raw.Draw("rsp:ptRef>>h2d_rsp_gen(%d,%g,%g,%d,%g,%g)" % (nb_pt, pt_min, pt_max, nb_rsp, rsp_min, rsp_max), eta_cutStr)
    h2d_rsp_gen = ROOT.gROOT.FindObject("h2d_rsp_gen")
    h2d_rsp_gen.SetTitle(";p_{T}^{Gen} [GeV];response (p_{T}^{L1}/p_{T}^{Gen})")
    output_f_hists.WriteTObject(h2d_rsp_gen)
    h2d_rsp_gen.Draw("COLZ")
    line_straight.Draw("SAME")
    canv.SaveAs("rsp_gen_%g_%g.pdf" % (absetamin, absetamax))

    # Draw rsp (pT^L1/pT^Gen) Vs L1 pT
    tree_raw.Draw("rsp:pt>>h2d_rsp_l1(%d,%g,%g,%d,%g,%g)" % (nb_pt, pt_min, pt_max, nb_rsp, rsp_min, rsp_max), eta_cutStr)
    h2d_rsp_l1 = ROOT.gROOT.FindObject("h2d_rsp_l1")
    h2d_rsp_l1.SetTitle(";p_{T}^{L1} [GeV];response (p_{T}^{L1}/p_{T}^{Gen})")
    output_f_hists.WriteTObject(h2d_rsp_l1)
    h2d_rsp_l1.Draw("COLZ")
    line_straight.Draw("SAME")
    canv.SaveAs("rsp_l1_%g_%g.pdf" % (absetamin, absetamax))

    # draw pT^Gen Vs pT^L1
    tree_raw.Draw("pt:ptRef>>h2d_gen_l1(%d,%g,%g,%d,%g,%g)" % (nb_pt, pt_min, pt_max, nb_pt, pt_min, pt_max), eta_cutStr)
    h2d_gen_l1 = ROOT.gROOT.FindObject("h2d_gen_l1")
    h2d_gen_l1.SetTitle(";p_{T}^{Gen} [GeV];p_{T}^{L1} [GeV]")
    output_f_hists.WriteTObject(h2d_gen_l1)
    h2d_gen_l1.Draw("COLZ")
    line_diag.Draw("SAME")
    canv.SaveAs("gen_l1_%g_%g.pdf" % (absetamin, absetamax))


def plot_rsp_eta(inputfile, outputfile, eta_bins):
    """Plot response in bins of eta"""

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

    for i,eta in enumerate(eta_bins[:-1]):
        emin = eta
        emax = eta_bins[i+1]    # Eta cut string
        eta_cutStr = " TMath::Abs(eta)<%g && TMath::Abs(eta) > %g " % (emax, emin)
        # plot response for this eta bin
        nb_rsp = 100
        rsp_min, rsp_max = 0, 5
        tree_raw.Draw("rsp>>h_rsp_%g_%g(%d,%g,%g)" % (emin, emax, nb_rsp, rsp_min, rsp_max), eta_cutStr)
        h_rsp = ROOT.gROOT.FindObject("h_rsp_%g_%g" % (emin, emax))
        h_rsp.SetTitle(";response (p_{T}^{L1}/p_{T}^{Gen});")
        output_f_hists.WriteTObject(h_rsp)

        # bit lazy - take mean for now
        mean = h_rsp.GetMean()
        err = h_rsp.GetMeanError()

        # add to graph
        N = gr_rsp_eta.GetN()
        gr_rsp_eta.SetPoint(N, 0.5 * (emin + emax), mean)
        gr_rsp_eta.SetPointError(N, 0.5 * (emax - emin), err)

    gr_rsp_eta.SetTitle(";|#eta^{L1}|; <response> = <p_{T}^{L1}/p_{T}^{Gen}>")
    gr_rsp_eta.SetName("gr_rsp_eta_%g_%g" % (eta_bins[0], eta_bins[-1]))
    output_f.WriteTObject(gr_rsp_eta)


########### MAIN ########################
def main(args=sys.argv[1:]):
    print args
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input ROOT filename")
    parser.add_argument("output", help="output ROOT filename")
    parser.add_argument("--central", action='store_true',
                        help="Do central eta bins only (eta <= 3)")
    parser.add_argument("--forward", action='store_true',
                        help="Do forward eta bins only (eta >= 3)")
    parser.add_argument("--etaInd", nargs="+",
                        help="list of eta bin INDICES to run over - " \
                        "if unspecified will do all " \
                        "(overrides --central/--forward)" \
                        "handy for batch mode" \
                        "MUST PUT AT VERY END")
    args = parser.parse_args(args=args)

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

        plot_checks(inputf, output_f, emin, emax)

    # Do an inclusive plot for all eta bins
    plot_checks(inputf, output_f, etaBins[0], etaBins[-1])

    # Do a respone vs eta graph
    plot_rsp_eta(inputf, output_f, etaBins)


if __name__ == "__main__":
    main()
