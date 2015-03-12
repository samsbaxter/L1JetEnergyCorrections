"""
This script takes as input the output file from RunMatcher, and loops over
matched genjet/L1 jet pairs, plotting interesting things and producing a
correction function, as well as LUTs to put in CMSSW.

Usage: see
python runCalibration -h

Originally by Nick Wardle, modified by Robin Aggleton
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

# Note that the actual limits used for fitting are defined further down
fitmin = 35. # 45 for central bins, 35 for fwd
fitmax = 250.

# definition of the response function to fit to get our correction function
# MAKE SURE IT'S THE SAME ONE THAT IS USED IN THE EMULATOR
fitfcn = ROOT.TF1("fitfcn", "[0]+[1]/(pow(log10(x),2)+[2])+[3]*exp(-[4]*(log10(x)-[5])*(log10(x)-[5]))", fitmin, fitmax)

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
    fitfunc.SetParameter(0, 0.5)
    fitfunc.SetParameter(1, 27)
    fitfunc.SetParameter(2, 8.78)
    fitfunc.SetParameter(3, 0.13)
    fitfunc.SetParameter(4, 0.0)
    fitfunc.SetParameter(5, -11.)


def fix_fit_params(fitfunc):
    """Fix so constant line"""
    fitfunc.FixParameter(1, 0)
    fitfunc.FixParameter(2, 0)
    fitfunc.FixParameter(3, 0)
    fitfunc.FixParameter(4, 0)
    fitfunc.FixParameter(5, 0)


def makeResponseCurves(inputfile, outputfile, ptBins_in, absetamin, absetamax,
                       fit_params, do_genjet_plots, do_correction_fit):
    """
    Do all the relevant hists and fitting, for one eta bin.
    """

    print "Doing eta bin: %g - %g" % (absetamin, absetamax)

    # Input tree
    tree_raw = inputfile.Get("valid")

    # Output folders
    output_f = outputfile.mkdir('eta_%g_%g' % (absetamin, absetamax))
    output_f_hists = output_f.mkdir("Histograms")

    # Eta cut string
    eta_cutStr = " TMath::Abs(eta)<%g && TMath::Abs(eta) > %g " % (absetamax, absetamin)

    # Draw response (pT^L1/pT^Gen) for all pt bins
    tree_raw.Draw("1./rsp>>hrsp_eta_%g_%g(50,0,2)" %(absetamin, absetamax) , eta_cutStr)
    hrsp_eta = ROOT.gROOT.FindObject("hrsp_eta_%g_%g" % (absetamin, absetamax))
    hrsp_eta.SetTitle(";response (p_{T}^{L1}/p_{T}^{Gen});")
    output_f_hists.WriteTObject(hrsp_eta)

    nb = 500
    pt_min, pt_max = 0, 500

    # Draw rsp (pT^L1/pT^Gen) Vs GenJet pT
    # rsp here is ref jet pt / l1 jet pt
    tree_raw.Draw("1./rsp:rsp*pt>>h2d_rsp_gen(%d,%g,%g,200,0,6)" % (nb, pt_min, pt_max), eta_cutStr)
    h2d_rsp_gen = ROOT.gROOT.FindObject("h2d_rsp_gen")
    h2d_rsp_gen.SetTitle(";p_{T}^{Gen} [GeV];response (p_{T}^{L1}/p_{T}^{Gen})")
    output_f_hists.WriteTObject(h2d_rsp_gen)

    # Draw rsp (pT^L1/pT^Gen) Vs L1 pT
    # rsp here is ref jet pt / l1 jet pt
    tree_raw.Draw("1./rsp:pt>>h2d_rsp_l1(%d,%g,%g,200,0,6)" % (nb, pt_min, pt_max), eta_cutStr)
    h2d_rsp_l1 = ROOT.gROOT.FindObject("h2d_rsp_l1")
    h2d_rsp_l1.SetTitle(";p_{T}^{L1} [GeV];response (p_{T}^{L1}/p_{T}^{Gen})")
    output_f_hists.WriteTObject(h2d_rsp_l1)

    # draw pT^Gen Vs pT^L1
    tree_raw.Draw("pt:rsp*pt>>h2d_gen_l1(%d,%g,%g,%d,%g,%g)" % (nb, pt_min, pt_max, nb, pt_min, pt_max), eta_cutStr)
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
    max_pt = 0 # maximum pt to perform fit or correction fn

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

        pt_cutStr = "pt*rsp < %g && pt*rsp > %g " % (xhigh, xlow)
        total_cutStr = "%s && %s" % (eta_cutStr, pt_cutStr)

        # Plots of pT L1 for given pT Gen bin
        tree_raw.Draw("pt>>hpt(200)", total_cutStr)
        hpt = ROOT.gROOT.FindObject("hpt")
        hpt.SetName("L1_pt_genpt_%g_%g" % (xlow, xhigh))

        if hrsp.GetEntries() <= 0 or hpt.GetEntries() <= 0:
            print "Skipping as 0 entries"
            continue

        output_f_hists.WriteTObject(hpt)

        # Plots of pT Gen for given pT Gen bin
        if do_genjet_plots:
            tree_raw.Draw("pt*rsp>>hpt_gen(200)", total_cutStr)
            hpt_gen = ROOT.gROOT.FindObject("hpt_gen")
            hpt_gen.SetName("gen_pt_genpt_%g_%g" % (xlow, xhigh))
            output_f_hists.WriteTObject(hpt_gen)

        # Fit Gaussian to response curve,
        # but only if we have a sensible number of entries
        fitStatus = -1
        mean = -999
        err = -999
        if hrsp.GetEntries() >= 3:
            fitStatus = int(hrsp.Fit("gaus", "QRI", "", hrsp.GetMean() - 1. * hrsp.GetRMS(), hrsp.GetMean() + 1. * hrsp.GetRMS()))
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
        max_pt = max(hpt.GetMean(), max_pt) if grc > 0 and hpt.GetMean() > gr.GetX()[grc-1] else max_pt
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
        min_pt = 30
        # some forward - specific settings
        if absetamin >= 3.:
            min_pt = 18
            thisfit = ROOT.TF1("fitfcneta_%g_%g" % (absetamin, absetamax), "pol1", min_pt, max_pt)
            # fix_fit_params(thisfit)
        print "Correction fn fit range:", min_pt, max_pt
        tmp_params = fit_correction(gr, thisfit, min_pt, max_pt)
        fit_params.append(tmp_params)

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
    fit_result = -1
    while (fit_result != 0 and fit_min < fit_max):
        fit_result = int(graph.Fit(function.GetName(), "R", "", fit_min, fit_max))
        print "Fit result:", fit_result, "for fit min", fit_min
        fit_min += 0.5

    params = []
    for i in range(function.GetNumberFreeParameters()):
        params.append(function.GetParameter(i))

    return params


def print_lut_screen(fit_params, eta_bins):
    """
    Take fit parameters and print to screen
    """
    # check
    if (1 + len(fit_params)) != len(eta_bins):
        print "ERROR: no. of eta bins in fit_params not same as no. of eta bins in setup"
        return

    # print to screen
    for i, eta in enumerate(eta_bins[0:-1]):
        print "Eta bin:", eta, "-", eta_bins[i + 1]
        for j, param in enumerate(fit_params[i]):
            print "\tParameter:", j, "=", param


def print_lut_file(fit_params, eta_bins, filename):
    """
    Take fit parameters and print to file, for use in CMSSW config file
    """
    # check
    if (1 + len(fit_params)) != len(eta_bins):
        print "ERROR: no. of eta bins in fit_params not same as no. of eta bins in setup"
        return

    with open(filename, "w") as file:
        file.write("# put this in your py config file\n")
        file.write("    PFCoefficients = cms.PSet(\n")

        # non tau bit first
        for i, bin in enumerate(fit_params):
            line = "        nonTauJetCalib%i = cms.vdouble(" % i
            line += ','.join([str("%.3f" % x) for x in fit_params[i]])
            line += "),\n"
            file.write(line)

        # tau bit - only central region
        for i, bin in enumerate(fit_params):
            if eta_bins[i + 1] <= 3.0:
                line = "        tauJetCalib%i = cms.vdouble(" % i
                line += ','.join([str("%.3f" % x) for x in fit_params[i]])
                line += "),\n"
                file.write(line)

        file.write("    )\n")


########### MAIN ########################
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input ROOT filename")
    parser.add_argument("output", help="output ROOT filename")
    parser.add_argument("--no_genjet_plots", action='store_false',
                        help="Don't do genjet plots for each pt/eta bin")
    parser.add_argument("--no_correction_fit", action='store_false',
                        help="Don't do fits to correction functions")
    parser.add_argument("--stage1", action='store_true',
                        help="Load stage 1 specifics e.g. fit defaults. If not flagged, defaults to GCT.")
    args = parser.parse_args()


    # Load fit fucntion starting params - important as wrong starting params
    # can cause fit failures
    if args.stage1:
        stage1_fit_defaults(fitfcn)
    else:
        gct_fit_defaults(fitfcn)

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
    print args.input
    print args.output
    if not inputf or not output_f:
        raise Exception("Input or output files cannot be opened")

    # Setup pt, eta bins for doing calibrations
    ptBins = binning.pt_bins
    etaBins = binning.eta_bins

    print "Running over eta bins:", etaBins
    print "Running over pT bins:", ptBins

    # Do plots & fitting to get calib consts
    fit_params = []
    for i,eta in enumerate(etaBins[:-1]):
        emin = eta
        emax = etaBins[i+1]
        if emin >= 3:
            ptBins = binning.pt_bins_wide # larger bins at higher pt
        makeResponseCurves(inputf, output_f, ptBins, emin, emax, fit_params, do_genjet_plots, do_correction_fit)


    # For testing:
    # makeResponseCurves(inputf, output_f, ptBins, 0.0, 0.348, fit_params)
    # makeResponseCurves(inputf, output_f, ptBins, 3.5, 4.0, fit_params)

    # Make LUT
    print_lut_screen(fit_params, etaBins)
    dname, fname = os.path.split(sys.argv[2])
    lut_filename = fname.replace(".root", ".py").replace("output_", "LUT_")
    print_lut_file(fit_params, etaBins, dname+"/"+lut_filename)


if __name__ == "__main__":
    main()
