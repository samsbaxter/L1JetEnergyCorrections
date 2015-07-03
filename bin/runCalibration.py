#!/usr/bin/env python
"""
This script takes as input the output file from RunMatcher, and loops over
matched genjet/L1 jet pairs, plotting interesting things and producing a
correction function, as well as LUTs to put in CMSSW.

Usage: see
python runCalibration.py -h

Originally by Nick Wardle, modified by Robin Aggleton
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
from correction_LUT_plot import print_function
from common_utils import check_exp, get_xy, get_exey


ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(1)
ROOT.gStyle.SetOptFit(1111)


# definition of the response function to fit to get our correction function
# MAKE SURE IT'S THE SAME ONE THAT IS USED IN THE EMULATOR
central_fit = ROOT.TF1("fitfcn", "[0]+[1]/(pow(log10(x),2)+[2])+[3]*exp(-[4]*(log10(x)-[5])*(log10(x)-[5]))")
forward_fit = ROOT.TF1("fitfcn", "pol0")

# Some sensible defaults for the fit function
def stage1_fit_defaults(fitfunc):
    """Better for Stage1"""
    fitfunc.SetParameter(0, 0.5)
    fitfunc.SetParameter(1, 2)
    fitfunc.SetParameter(2, -0.5)
    fitfunc.SetParameter(3, 0.13)
    fitfunc.SetParameter(4, 0.0)
    fitfunc.SetParameter(5, -6.)


def gct_fit_defaults(fitfunc):
    """Better for GCT"""
    fitfunc.SetParameter(0, 1)
    fitfunc.SetParameter(1, 5)
    fitfunc.SetParameter(2, 1)
    fitfunc.SetParameter(3, -25)
    fitfunc.SetParameter(4, 0.01)
    fitfunc.SetParameter(5, -20)


def fix_fit_params(fitfunc):
    """Fix so constant line"""
    fitfunc.FixParameter(1, 0)
    fitfunc.FixParameter(2, 0)
    fitfunc.FixParameter(3, 0)
    fitfunc.FixParameter(4, 0)
    fitfunc.FixParameter(5, 0)


def makeResponseCurves(inputfile, outputfile, ptBins_in, absetamin, absetamax,
                        fitfcn, fit_params, do_genjet_plots, do_correction_fit):
    """
    Do all the relevant hists and fitting, for one eta bin.
    """

    print "Doing eta bin: %g - %g" % (absetamin, absetamax)
    print "Running over pT bins:", ptBins_in

    # Input tree
    tree_raw = inputfile.Get("valid")

    # Output folders
    output_f = outputfile.mkdir('eta_%g_%g' % (absetamin, absetamax))
    output_f_hists = output_f.mkdir("Histograms")

    # Eta cut string
    eta_cutStr = " TMath::Abs(eta)<%g && TMath::Abs(eta) > %g " % (absetamax, absetamin)

    # Draw response (pT^L1/pT^Gen) for all pt bins
    tree_raw.Draw("rsp>>hrsp_eta_%g_%g(50,0,2)" %(absetamin, absetamax) , eta_cutStr)
    hrsp_eta = ROOT.gROOT.FindObject("hrsp_eta_%g_%g" % (absetamin, absetamax))
    hrsp_eta.SetTitle(";response (p_{T}^{L1}/p_{T}^{Gen});")
    output_f_hists.WriteTObject(hrsp_eta)

    nb = 500
    pt_min, pt_max = 0, 500

    # Draw rsp (pT^L1/pT^Gen) Vs GenJet pT
    tree_raw.Draw("rsp:pt/rsp>>h2d_rsp_gen(%d,%g,%g,150,0,5)" % (nb, pt_min, pt_max), eta_cutStr)
    h2d_rsp_gen = ROOT.gROOT.FindObject("h2d_rsp_gen")
    h2d_rsp_gen.SetTitle(";p_{T}^{Gen} [GeV];response (p_{T}^{L1}/p_{T}^{Gen})")
    output_f_hists.WriteTObject(h2d_rsp_gen)

    # Draw rsp (pT^L1/pT^Gen) Vs L1 pT
    tree_raw.Draw("rsp:pt>>h2d_rsp_l1(%d,%g,%g,150,0,5)" % (nb, pt_min, pt_max), eta_cutStr)
    h2d_rsp_l1 = ROOT.gROOT.FindObject("h2d_rsp_l1")
    h2d_rsp_l1.SetTitle(";p_{T}^{L1} [GeV];response (p_{T}^{L1}/p_{T}^{Gen})")
    output_f_hists.WriteTObject(h2d_rsp_l1)

    # draw pT^L1 Vs pT^Gen
    tree_raw.Draw("pt:pt/rsp>>h2d_gen_l1(%d,%g,%g,%d,%g,%g)" % (nb, pt_min, pt_max, nb, pt_min, pt_max), eta_cutStr)
    h2d_gen_l1 = ROOT.gROOT.FindObject("h2d_gen_l1")
    h2d_gen_l1.SetTitle(";p_{T}^{Gen} [GeV];p_{T}^{L1} [GeV]")
    output_f_hists.WriteTObject(h2d_gen_l1)

    # Go through and find histogram bin edges that are closest to the input pt
    # bin edges, and store for future use
    ptBins = []
    bin_indices = []
    for i, ptR in enumerate(ptBins_in[0:-1]):
        bin1 = h2d_rsp_gen.GetXaxis().FindBin(ptR)
        bin2 = h2d_rsp_gen.GetXaxis().FindBin(ptBins_in[i + 1]) - 1
        xlow = h2d_rsp_gen.GetXaxis().GetBinLowEdge(bin1)
        xup = h2d_rsp_gen.GetXaxis().GetBinLowEdge(bin2 + 1)
        bin_indices.append([bin1, bin2])
        ptBins.append(xlow)
    ptBins.append(xup)  # only need this last one

    gr = ROOT.TGraphErrors() # 1/<rsp> VS ptL1
    gr_gen = ROOT.TGraphErrors()  # 1/<rsp> VS ptGen
    grc = 0

    # Iterate over pT^Gen bins, and for each:
    # - Project 2D hist so we have a plot of response for given pT^Gen range
    # - Fit a Gaussian (if possible) to this resp histogram to get <response>
    # - Plot the L1 pT for given pT^Gen range (remember, for matched pairs)
    # - Get average response, <pT^L1>, from 1D L1 pT hist
    # - Add a new graph point, x=<pT^L1> y=<response> for this pT^Gen bin
    for i, ptR in enumerate(ptBins[0:-1]):

        bin1 = bin_indices[i][0]
        bin2 = bin_indices[i][1]
        # h2d_calib.GetXaxis().FindBin(ptR)
        # h2d_calib.GetXaxis().FindBin(ptBins[i+1])-1
        # print "Binning mis-matches", ptR, ptBins[i+1],
        # h2d_calib.GetXaxis().GetBinLowEdge(bin1),h2d_calib.GetXaxis().GetBinLowEdge(bin2+1)

        ########################### CALIBRATION #############################
        xlow = ptR
        xhigh = ptBins[i + 1]

        # Plot of response for given pT Gen bin
        hrsp = h2d_rsp_gen.ProjectionY("prj_ResponseProj_PTBin%d" % (i), bin1, bin2)
        hrsp.SetName("Rsp_genpt_%g_%g" % (xlow, xhigh))

        # cut on ref jet pt
        pt_cutStr = "pt/rsp < %g && pt/rsp > %g " % (xhigh, xlow)
        total_cutStr = "%s && %s" % (eta_cutStr, pt_cutStr)

        # Plots of pT L1 for given pT Gen bin
        tree_raw.Draw("pt>>hpt(600, 0, 300)", total_cutStr)
        hpt = ROOT.gROOT.FindObject("hpt")
        hpt.SetName("L1_pt_genpt_%g_%g" % (xlow, xhigh))

        if hrsp.GetEntries() <= 0 or hpt.GetEntries() <= 0:
            print "Skipping as 0 entries"
            continue

        output_f_hists.WriteTObject(hpt)

        # Plots of pT Gen for given pT Gen bin
        if do_genjet_plots:
            tree_raw.Draw("pt/rsp>>hpt_gen(200)", total_cutStr)
            hpt_gen = ROOT.gROOT.FindObject("hpt_gen")
            hpt_gen.SetName("gen_pt_genpt_%g_%g" % (xlow, xhigh))
            output_f_hists.WriteTObject(hpt_gen)

        # Fit Gaussian to response curve,
        # but only if we have a sensible number of entries
        fitStatus = -1
        mean = -999
        err = -999
        if hrsp.GetEntries() >= 3:
            fitStatus = int(hrsp.Fit("gaus", "QER", "", hrsp.GetMean() - 1. * hrsp.GetRMS(), hrsp.GetMean() + 1. * hrsp.GetRMS()))
            if fitStatus == 0:
                mean = hrsp.GetFunction("gaus").GetParameter(1)
                err = hrsp.GetFunction("gaus").GetParError(1)
        output_f_hists.WriteTObject(hrsp)

        # check if we have a bad fit - either fit status != 0, or
        # fit mean is close to raw mean. in either case not use raw mean
        if fitStatus != 0 or abs((mean/hrsp.GetMean()) - 1) > 0.2:
            print "Poor Fit: fit mean:", mean, "raw mean:", hrsp.GetMean(), \
                "fit status:", fitStatus, \
                "bin :", [xlow, xhigh], [absetamin, absetamax]
            mean = hrsp.GetMean()
            err = hrsp.GetMeanError()

        print "pT Gen: ", ptR, "-", ptBins[i + 1], "<pT L1>:", hpt.GetMean(), \
               "<pT Gen>:", (hpt_gen.GetMean() if do_genjet_plots else "NA"), "<rsp>:", mean

        # add point to response graph vs pt
        # store if new max/min, but only max if pt > pt of previous point
        # max_pt = max(hpt.GetMean(), max_pt) if grc > 0 and hpt.GetMean() > gr.GetX()[grc-1] else max_pt
        # min_pt = min(hpt.GetMean(), min_pt)
        gr.SetPoint(grc, hpt.GetMean(), 1. / mean)
        gr.SetPointError(grc, hpt.GetMeanError(), err)
        if do_genjet_plots:
            gr_gen.SetPoint(grc, hpt_gen.GetMean(), 1. / mean)
            # gr_gen.SetPointError(grc, hpt.GetMeanError(), err)
        grc += 1

    # Label response VS pT graphs
    gr.SetName('l1corr_eta_%g_%g' % (absetamin, absetamax))
    gr.GetXaxis().SetTitle("<p_{T}^{L1}> [GeV]")
    gr.GetYaxis().SetTitle("1/<p_{T}^{L1}/p_{T}^{Gen}>")

    if do_genjet_plots:
        gr_gen.SetName('gencorr_eta_%g_%g' % (absetamin, absetamax))
        gr_gen.GetXaxis().SetTitle("<p_{T}^{Gen}> [GeV]")
        gr_gen.GetYaxis().SetTitle("1/<p_{T}^{L1}/p_{T}^{Gen}>")

    # Fit correction function to response vs pT graph, add to list
    if do_correction_fit:
        thisfit = fitfcn.Clone(fitfcn.GetName() + 'eta_%g_%g' % (absetamin, absetamax))
        fit_min = 30
        # some forward - specific settings
        if absetamin >= 3.:
            fit_min = 20
            # fix_fit_params(thisfit)

        xarr, yarr = get_xy(gr)
        max_pt = max(xarr)  # Maxmimum pt for upper range of fit
        # For lower bound of fit, use either fit_min or the pt
        # of the maximum corr value, whicher is larger.
        # Check to make sure it's not the last point on the graph
        # (e.g. if no turnover), in which case just use the default fit_min
        max_corr = max(yarr)
        max_corr_pt = yarr.index(max_corr)
        fit_min = max(fit_min, max_corr_pt) if (max_corr_pt != xarr[-1]) and (max_corr_pt != max_pt) else fit_min

        print "Correction fn fit range:", fit_min, max_pt
        fit_graph, tmp_params = fit_correction(gr, thisfit, fit_min, max_pt)
        print_function(thisfit, "cpp")
        print_function(thisfit, "py")
        fit_params.append(tmp_params)
        outputfile.WriteTObject(fit_graph)

    # Save these to file
    outputfile.WriteTObject(gr)
    if do_correction_fit:
        outputfile.WriteTObject(thisfit)
    if do_genjet_plots:
        outputfile.WriteTObject(gr_gen)


def fit_correction(graph, function, fit_min, fit_max):
    """
    Fit response curve with given correction function, within given bounds.

    Note that sometime the fit fails oddly - if so, we try raising the lower
    bound of the fit until it suceeds (sometimes it works at e.g. 45, but not 40)

    Returns parameters of successful fit.
    """
    print "Fitting", fit_min, fit_max

    # Sometimes have 2 points with very diff corr values within a given
    # pt range due to turnover
    # To make the fit better/easier, we make a Graph with the subset
    # of points we want to fit to
    xarr, yarr = get_xy(graph)
    min_ind = xarr.index(next(x for x in xarr if x >= fit_min and xarr[xarr.index(x)+1] > x))
    print "min_ind:", min_ind, "x,y of fit graph:", xarr[min_ind:], yarr[min_ind:]
    # Do not user graph.RemovePoint()! It doesn't work, and only removes every-other point
    # Instead make a graph with the bit of array we want
    exarr, eyarr = get_exey(graph)
    fit_graph = ROOT.TGraphErrors(len(xarr)-min_ind, np.array(xarr[min_ind:]), np.array(yarr[min_ind:]), np.array(exarr[min_ind:]), np.array(eyarr[min_ind:]))
    fit_graph.SetName(graph.GetName()+"_fit")

    # Now do the fitting, incrementing the fit min if failure
    fit_result = -1
    while (fit_result != 0 and fit_min < fit_max):
        function.SetRange(fit_min, fit_max)
        mode = ""
        if str(function.GetExpFormula()).startswith("pol"):
            mode = "F"
        fit_result = int(fit_graph.Fit(function.GetName(), "R"+mode, "", fit_min, fit_max))
        # sanity check - sometimes will have status = 0 even though rubbish
        if function.Eval(80) > 10 or function.Eval(80) < 0.01:
            fit_result = -1
        print "Fit result:", fit_result, "for fit min", fit_min
        fit_min += 0.5

    params = []
    if fit_result != 0 or function.Eval(80) > 10 or function.Eval(80) < 0.01:
        print "Couldn't fit"
    else:
        for i in range(function.GetNumberFreeParameters()):
            params.append(function.GetParameter(i))

    return fit_graph, params


########### MAIN ########################
def main(in_args=sys.argv[1:]):
    print in_args
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="input ROOT filename")
    parser.add_argument("output", help="output ROOT filename")
    parser.add_argument("--no_genjet_plots", action='store_false',
                        help="Don't do genjet plots for each pt/eta bin")
    parser.add_argument("--no_correction_fit", action='store_false',
                        help="Don't do fits to correction functions")
    parser.add_argument("--stage1", action='store_true',
                        help="Load stage 1 specifics e.g. fit defaults. If not flagged, defaults to GCT.")
    parser.add_argument("--central", action='store_true',
                        help="Do central eta bins only (eta <= 3)")
    parser.add_argument("--forward", action='store_true',
                        help="Do forward eta bins only (eta >= 3)")
    parser.add_argument("--etaInd", nargs="+",
                        help="list of eta bin INDICES to run over - " \
                        "if unspecified will do all. " \
                        "This overrides --central/--forward. " \
                        "Handy for batch mode. " \
                        "IMPORTANT: MUST PUT AT VERY END")
    args = parser.parse_args(args=in_args)

    if args.stage1:
        print "Running with Stage1 defaults"
    else:
        print "Running with GCT defaults"

    # Turn off gen plots if you don't want them - they slow things down,
    # and don't affect determination of correction fn
    do_genjet_plots = args.no_genjet_plots
    if not do_genjet_plots:
        print "Not producing genjet plots"

    # Turn off if you don't want to fit to the correction curve
    # e.g. if you're testing your calibrations, since it'll waste time
    do_correction_fit = args.no_correction_fit
    if not do_correction_fit:
        print "Not fitting correction curves"

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

    # Do plots & fitting to get calib consts
    fit_params = []
    for i,eta in enumerate(etaBins[:-1]):
        emin = eta
        emax = etaBins[i+1]

        # whether we're doing a central or forward bin (.1 is for rounding err)
        forward_bin = emax > 3.1

        # setup pt bins, wider ones for forward region
        ptBins = binning.pt_bins if not forward_bin else binning.pt_bins_wide
        # ptBins = binning.pt_bins

        # Load fit function & starting params - important as wrong starting params
        # can cause fit failures
        fitfunc = central_fit
        if args.stage1:
            stage1_fit_defaults(fitfunc)
        else:
            gct_fit_defaults(fitfunc)

        # if forward_bin:
            # fitfunc = forward_fit

        makeResponseCurves(inputf, output_f, ptBins, emin, emax, fitfunc, fit_params, do_genjet_plots, do_correction_fit)


if __name__ == "__main__":
    main()
