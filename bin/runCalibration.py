#!/usr/bin/env python
"""
This script takes as input the output file from RunMatcher, and loops over
matched genjet/L1 jet pairs, plotting interesting things and producing a
correction function, as well as LUTs to put in CMSSW.

It can also re-fit the correction curve to an existing graph, saving time.
In this case, use the --redo_correction_fit option, and the input file is
the output from a previous running of this script.

Usage: see
python runCalibration.py -h

Originally by Nick Wardle, modified(hacked to shreds) by Robin Aggleton
"""

import ROOT
import sys
import array
import numpy as np
from itertools import izip
import os
import argparse
import binning
import common_utils as cu


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
    """Better initial starting params for Stage1"""
    fitfunc.SetParameter(0, 1)
    fitfunc.SetParameter(1, 5)
    fitfunc.SetParameter(2, 1)
    fitfunc.SetParameter(3, -25)
    fitfunc.SetParameter(4, 0.01)
    fitfunc.SetParameter(5, -20)


def gct_fit_defaults(fitfunc):
    """Better intiial starting params for GCT"""
    fitfunc.SetParameter(0, 1)
    fitfunc.SetParameter(1, 5)
    fitfunc.SetParameter(2, 1)
    fitfunc.SetParameter(3, -25)
    fitfunc.SetParameter(4, 0.01)
    fitfunc.SetParameter(5, -20)


def fix_fit_params(fitfunc):
    """Fix function so constant line"""
    fitfunc.FixParameter(1, 0)
    fitfunc.FixParameter(2, 0)
    fitfunc.FixParameter(3, 0)
    fitfunc.FixParameter(4, 0)
    fitfunc.FixParameter(5, 0)


def generate_eta_graph_name(absetamin, absetamax):
    """
    Function to generate graph name for given eta bin,
    so co-ordinated between functions/modules.
    """
    return "l1corr_eta_%g_%g" % (absetamin, absetamax)


def make_correction_curves(inputfile, outputfile, ptBins_in, absetamin, absetamax,
                           fitfcn, do_genjet_plots, do_correction_fit,
                           pu_min, pu_max):
    """
    Do all the relevant hists and fitting, for one eta bin.

    Briefly: make plots of L1 jet pT, and response (= l1/gen) for each genjet pt bin.
    Then find the mean L1 jet pT for the pt bin.
    Then fit a Gaussian to each response histogram, and get the mean.
    Plot 1/fitted mean Vs mean L1 pT.
    Then fit with given function, and return parameters.
    All of these plots are stored in the TFile, outputfile.

    Returns parameters of succeful fit.

    inputfile: TFile. Must contain TTree named "valid", full of pair quantities.

    outputfile: TFile. To store output histograms.

    ptBins_in: list. Edges of pt bins used to divide up correction curve.

    absetamin: float. Lower edge of eta bin, must be >= 0.

    absetamax: float. Upper edge of eta bin, must be > 0.

    fitfcn: TF1. Function to fit for correction curve.

    do_genjet_plots: bool. Whether to make plots for reference jets. Not used
        in calcualtion of correction curve, but handy for debugging.

    do_correction_fit: bool. Whether to actually fit the correction curve.

    pu_min: float. Cut on minimum number of PU vertices.

    pu_max: float. Cut on maximum number of PU vertices.

    """

    print "Doing eta bin: %g - %g" % (absetamin, absetamax)
    print "Doing PU range: %g - %g" %(pu_min, pu_max)
    print "Running over pT bins:", ptBins_in

    # Input tree
    tree_raw = cu.get_from_file(inputfile, "valid")

    # Output folders
    output_f = outputfile.mkdir('eta_%g_%g' % (absetamin, absetamax))
    output_f_hists = output_f.mkdir("Histograms")

    # Eta cut string
    eta_cut = ROOT.TCut("TMath::Abs(eta)<%g && TMath::Abs(eta) > %g" % (absetamax, absetamin))

    # PU cut string
    if hasattr(tree_raw, "numPUVertices"):
        pu_cut = ROOT.TCut("numPUVertices > %g && numPUVertices < %g" % (pu_min, pu_max))
    else:
        pu_cut = ROOT.TCut("")

    # Total cut
    total_cut = ROOT.TCut(eta_cut)
    total_cut += pu_cut  # need to use += and not && cos TCut all fubar
    print total_cut

    # Draw response (pT^L1/pT^Gen) for all pt bins
    tree_raw.Draw("rsp>>hrsp_eta_%g_%g(50,0,2)" %(absetamin, absetamax), total_cut)
    hrsp_eta = ROOT.gROOT.FindObject("hrsp_eta_%g_%g" % (absetamin, absetamax))
    hrsp_eta.SetTitle(";response (p_{T}^{L1}/p_{T}^{Gen});")
    output_f_hists.WriteTObject(hrsp_eta)

    nb = 500
    pt_min, pt_max = 0, 500

    # Draw rsp (pT^L1/pT^Gen) Vs GenJet pT
    tree_raw.Draw("rsp:ptRef>>h2d_rsp_gen(%d,%g,%g,150,0,5)" % (nb, pt_min, pt_max), total_cut)
    h2d_rsp_gen = ROOT.gROOT.FindObject("h2d_rsp_gen")
    h2d_rsp_gen.SetTitle(";p_{T}^{Gen} [GeV];response (p_{T}^{L1}/p_{T}^{Gen})")
    output_f_hists.WriteTObject(h2d_rsp_gen)

    # Draw rsp (pT^L1/pT^Gen) Vs L1 pT
    tree_raw.Draw("rsp:pt>>h2d_rsp_l1(%d,%g,%g,150,0,5)" % (nb, pt_min, pt_max), total_cut)
    h2d_rsp_l1 = ROOT.gROOT.FindObject("h2d_rsp_l1")
    h2d_rsp_l1.SetTitle(";p_{T}^{L1} [GeV];response (p_{T}^{L1}/p_{T}^{Gen})")
    output_f_hists.WriteTObject(h2d_rsp_l1)

    # draw pT^L1 Vs pT^Gen
    tree_raw.Draw("pt:ptRef>>h2d_gen_l1(%d,%g,%g,%d,%g,%g)" % (nb, pt_min, pt_max, nb, pt_min, pt_max), total_cut)
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
        pt_cut = ROOT.TCut("ptRef < %g && ptRef > %g " % (xhigh, xlow))
        total_cut = ROOT.TCut(eta_cut)
        total_cut += pu_cut
        total_cut += pt_cut
        print total_cut

        # Plots of pT L1 for given pT Gen bin
        tree_raw.Draw("pt>>hpt(1000, 0, 500)", total_cut)
        hpt = ROOT.gROOT.FindObject("hpt")
        hpt.SetName("L1_pt_genpt_%g_%g" % (xlow, xhigh))

        if hrsp.GetEntries() <= 0 or hpt.GetEntries() <= 0:
            print "Skipping as 0 entries"
            continue

        output_f_hists.WriteTObject(hpt)

        # Plots of pT Gen for given pT Gen bin
        if do_genjet_plots:
            tree_raw.Draw("ptRef>>hpt_gen(200)", total_cut)
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
        # fit mean is not close to raw mean. in either case use raw mean
        if fitStatus != 0 or (absetamin > 2.9 and abs((mean/hrsp.GetMean()) - 1) > 0.2):

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
    graph_name = generate_eta_graph_name(absetamin, absetamax)
    gr.SetName(graph_name)
    gr.GetXaxis().SetTitle("<p_{T}^{L1}> [GeV]")
    gr.GetYaxis().SetTitle("1/<p_{T}^{L1}/p_{T}^{Gen}>")

    if do_genjet_plots:
        gr_gen.SetName('gencorr_eta_%g_%g' % (absetamin, absetamax))
        gr_gen.GetXaxis().SetTitle("<p_{T}^{Gen}> [GeV]")
        gr_gen.GetYaxis().SetTitle("1/<p_{T}^{L1}/p_{T}^{Gen}>")

    # Fit correction function to response vs pT graph, add params list
    fit_params = []

    if do_correction_fit:
        sub_graph, this_fit = setup_fit(gr, fitfcn, absetamin, absetamax, outputfile)
        fit_graph, fit_params = fit_correction(sub_graph, this_fit)
        outputfile.WriteTObject(this_fit)  # function by itself
        outputfile.WriteTObject(fit_graph)  # has the function stored in it as well

    # Save these to file
    outputfile.WriteTObject(gr)
    if do_genjet_plots:
        outputfile.WriteTObject(gr_gen)

    return fit_params


def setup_fit(graph, function, absetamin, absetamax, outputfile):
    """Setup for fitting (auto-calculate sensible range).

    Returns a sub-graph of only sensible points (chop off turnover at low pT,
    and any high pT tail), along with a corresponding fit function
    whose range has been set to match the sub graph.
    """

    xarr, yarr = cu.get_xy(graph)
    exarr, eyarr = cu.get_exey(graph)

    fit_max = max(xarr)  # Maxmimum pt for upper range of fit
    fit_min = 20 if absetamin > 2.9 else 20

    # For lower bound of fit, use either fit_min or the pt
    # of the maximum corr value, whichever has the larger pT.
    # Check to make sure it's not the last point on the graph
    # (e.g. if no turnover), in which case just use the default fit_min
    # Then find the index of the closest corresponding value in xarr
    max_corr = max(yarr[:len(yarr) / 2])
    max_corr_ind = yarr.index(max_corr)
    max_corr_pt = xarr[max_corr_ind]
    fit_min = max(fit_min, max_corr_pt) if (max_corr_pt != xarr[-1]) and (max_corr_pt != xarr[-1]) else fit_min
    min_ind = next(i for i, x in enumerate(xarr) if x >= fit_min)

    # For HF, the upper end flicks up, ruining the fit. Remove these points.
    # Start from halfway along the graph to ignore the initial turnover,
    # then look for a point where the next 2 points have consecutively
    # larger correction values. That's your fit maximum.
    max_ind = len(xarr)-1
    starting_ind = len(xarr) / 2
    for i, y in enumerate(yarr[starting_ind:-2]):
        if yarr[i + 2 + starting_ind] > yarr[i + 1 + starting_ind] > y:
            max_ind = i + starting_ind + 1
            break
    fit_max = xarr[max_ind]
    print "Correction fn fit range:", fit_min, fit_max

    # Generate a correction fucntion with suitable range
    this_fit = function.Clone(function.GetName() + 'eta_%g_%g' % (absetamin, absetamax))
    this_fit.SetRange(fit_min, fit_max)

    # Make a sub-graph with only the points used for fitting
    # Do not user graph.RemovePoint()! It doesn't work, and only removes every other point
    # Instead make a graph with the bit of array we want
    fit_graph = ROOT.TGraphErrors(max_ind-min_ind,
                                  np.array(xarr[min_ind:max_ind]),
                                  np.array(yarr[min_ind:max_ind]),
                                  np.array(exarr[min_ind:max_ind]),
                                  np.array(eyarr[min_ind:max_ind]))
    fit_graph.SetName(graph.GetName()+"_fit")

    return fit_graph, this_fit


def fit_correction(graph, function, fit_min=-1, fit_max=-1):
    """
    Fit response curve with given correction function, within given bounds.
    If fit_min and fit_max are < 0, then just use the range of the function supplied.

    Note that sometime the fit fails - if so, we try raising the lower
    bound of the fit until it suceeds (sometimes it works at e.g. 45, but not 40).
    If that fails, then we lower the upper bound and try fitting whilst raising
    the lower bound again.

    Returns graph (with fitted function) and parameters of successful fit.
    """
    # Get the min and max of the fit function
    if fit_min < 0  and fit_max < 0:
        fit_min, fit_max = ROOT.Double(), ROOT.Double()
        function.GetRange(fit_min, fit_max)

    print "Fitting", fit_min, fit_max

    # Now do the fitting, incrementing the fit min if failure
    fit_result = -1

    orig_fit_min, orig_fit_max = fit_min, fit_max

    while fit_max > orig_fit_min + 10:
        fit_min = orig_fit_min
        while fit_min < fit_max:
            function.SetRange(fit_min, fit_max)
            mode = ""
            if str(function.GetExpFormula()).startswith("pol"):
                mode = "F"
            fit_result = int(graph.Fit(function.GetName(), "R"+mode, "", fit_min, fit_max))
            # sanity check - sometimes will have status = 0 even though rubbish
            if function.Eval(50) > 10 or function.Eval(50) < 0.01:
                fit_result = -1
            print "Fit result:", fit_result, "for fit min", fit_min, "to max", fit_max
            if fit_result == 0:
                break
            else:
                fit_min += 0.5
        if fit_result == 0:
            break

        fit_max -= 0.5

    params = []
    if fit_result != 0 or function.Eval(50) > 10 or function.Eval(50) < 0.01:
        print "Couldn't fit"
    else:
        for i in range(function.GetNumberFreeParameters()):
            params.append(function.GetParameter(i))

    return graph, params


def redo_correction_fit(inputfile, outputfile, absetamin, absetamax, fitfcn):
    """Redo correction fit for a given eta bin.

    Get TGraphErrors for the bin, and perform calibration curve fitting
    procedure and save if successful.

    inputfile: TFile. The output file from running runCalibration.py previously.
    outputfile: TFile. The file you want to write the new graph & fit to.
    Can be the same as inputfile.
    absetamin: double
    absetamax: double
    fitfcn: TF1
    """
    # Get relevant graph
    gr = cu.get_from_file(inputfile, generate_eta_graph_name(absetamin, absetamax))

    # Setup fitting (calculate sensible range, make sub-graph), then do fit!
    sub_graph, this_fit = setup_fit(gr, fitfcn, absetamin, absetamax, outputfile)
    fit_graph, fit_params = fit_correction(sub_graph, this_fit)
    outputfile.WriteTObject(this_fit)  # function by itself
    outputfile.WriteTObject(fit_graph)  # has the function stored in it as well
    outputfile.WriteTObject(gr)  # the original graph


########### MAIN ########################
def main(in_args=sys.argv[1:]):
    print in_args
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="input ROOT filename")
    parser.add_argument("output", help="output ROOT filename")
    parser.add_argument("--no_genjet_plots", action='store_false',
                        help="Don't do genjet plots for each pt/eta bin")
    parser.add_argument("--no_correction_fit", action='store_false',
                        help="Don't do fits for correction functions")
    parser.add_argument("--redo_correction_fit", action='store_true',
                        help="Redo fits for correction functions")
    parser.add_argument("--gct", action='store_true',
                        help="Load legacy GCT specifics e.g. fit defaults.")
    parser.add_argument("--stage1", action='store_true',
                        help="Load stage 1 specifics e.g. fit defaults.")
    parser.add_argument("--central", action='store_true',
                        help="Do central eta bins only (eta <= 3)")
    parser.add_argument("--forward", action='store_true',
                        help="Do forward eta bins only (eta >= 3)")
    parser.add_argument("--PUmin", type=float, default=-100,
                        help="Minimum number of PU vertices (refers to *actual* " \
                             "number of PU vertices in the event, not the centre " \
                             "of of the Poisson distribution)")
    parser.add_argument("--PUmax", type=float, default=1200,
                        help="Maximum number of PU vertices (refers to *actual* " \
                             "number of PU vertices in the event, not the centre " \
                             "of of the Poisson distribution)")
    parser.add_argument("--etaInd", nargs="+",
                        help="list of eta bin INDICES to run over - " \
                        "if unspecified will do all. " \
                        "This overrides --central/--forward. " \
                        "Handy for batch mode. " \
                        "IMPORTANT: MUST PUT AT VERY END")
    args = parser.parse_args(args=in_args)

    if args.stage1:
        print "Running with Stage1 defaults"
    elif args.gct:
        print "Running with GCT defaults"
    else:
        raise RuntimeError("You need to specify defaults: --gct/--stage1")

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
    print "IN:", args.input
    print "OUT:", args.output
    input_file = cu.open_root_file(args.input, "READ")
    output_file = cu.open_root_file(args.output, "RECREATE")

    # Figure out which eta bins the user wants to run over
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
    for i, eta_min in enumerate(etaBins[:-1]):
        eta_max = etaBins[i+1]

        # whether we're doing a central or forward bin (.1 is for rounding err)
        forward_bin = eta_max > 3.1

        # setup pt bins, wider ones for forward region
        ptBins = binning.pt_bins if not forward_bin else binning.pt_bins_wide

        # Load fit function & starting params - important as wrong starting params
        # can cause fit failures
        fitfunc = central_fit
        if args.stage1:
            stage1_fit_defaults(fitfunc)
        elif args.gct:
            gct_fit_defaults(fitfunc)

        # if forward_bin:
            # fitfunc = forward_fit

        if args.redo_correction_fit:
            redo_correction_fit(input_file, output_file, eta_min, eta_max, fitfunc)
        else:
            make_correction_curves(input_file, output_file, ptBins, eta_min, eta_max,
                                   fitfunc, do_genjet_plots, do_correction_fit,
                                   args.PUmin, args.PUmax)


if __name__ == "__main__":
    main()
