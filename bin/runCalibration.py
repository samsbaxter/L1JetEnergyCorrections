import ROOT
import sys
import array
import numpy
from pprint import pprint
from itertools import izip
import os

# ORIGNALLY BY NICK WARDLE

ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(1)
ROOT.gStyle.SetOptFit(1111)

fitmin = 100.
fitmax = 250.

# definition of the response function to fit
# fitfcn = ROOT.TF1("fitfcn","[0] + [1]/(TMath::Power(TMath::Log10(x),2) + [2]) + [3]*TMath::Exp(-1.*[4]*TMath::Power(TMath::Log10(x)-[5],2))", 20, 250)
fitfcn = ROOT.TF1("fitfcn", "[0]+[1]/(pow(log10(x),2)+[2])+[3]*exp(-[4]*(log10(x)-[5])*(log10(x)-[5]))", fitmin, fitmax)
fitfcn.SetParameter(0, 0.5)
fitfcn.SetParameter(1, 27)
fitfcn.SetParameter(2, 8.78)
fitfcn.SetParameter(3, 0.05)
fitfcn.SetParameter(4, 0.0)
fitfcn.SetParameter(5, -11.)


def makeResponseCurves(inputfile, outputfile, ptBins_in, absetamin, absetamax, fit_params):
    """
    Do all the relevant hists and fitting, for one eta bin.
    """

    name = "ResponseProj"
    nptbins = len(ptBins_in) - 1
    coll = "Off"
    ext = 'PT'
    obj = 'P_{T}^{Gen}'
    unit = '(GeV)'

    nb = 500
    min, max = 0, 500

    output_f = outputfile.mkdir('eta_%g_%g' % (absetamin, absetamax))
    output_f_hists = output_f.mkdir("Histograms")

    lat = ROOT.TLatex()
    lat.SetNDC()
    lat.SetTextFont(42)
    lat.SetTextSize(0.04)

    leg = ROOT.TLegend(0.55, 0.7, 0.94, 0.94)
    leg.SetFillColor(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.04)

    leg2 = ROOT.TLegend(0.6, 0.75, 0.94, 0.94)
    leg2.SetFillColor(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.04)

    tree_raw = inputfile.Get("valid")

    # From the input file, we make the histograms
    cstr = " TMath::Abs(eta)<%g && TMath::Abs(eta) > %g " % (absetamax, absetamin)

    # Draw response (pT^L1/pT^Gen)
    tree_raw.Draw("1./rsp>>hrsp_eta_%g_%g(50,0,2)" %(absetamin, absetamax) , cstr)
    hrsp_eta = ROOT.gROOT.FindObject("hrsp_eta_%g_%g" % (absetamin, absetamax))
    hrsp_eta.SetTitle(";response (p_{T}^{L1}/p_{T}^{Gen});")
    output_f_hists.WriteTObject(hrsp_eta)

    # Draw rsp (pT^L1/pT^Gen) Vs GenJet pT
    # rsp here is ref jet pt / l1 jet pt
    tree_raw.Draw("1./rsp:rsp*pt>>h2d_rsp_gen(%d,%g,%g,200,0,6)" % (nb, min, max), cstr)
    h2d_rsp_gen = ROOT.gROOT.FindObject("h2d_rsp_gen")
    h2d_rsp_gen.SetTitle(";p_{T}^{Gen};response (p_{T}^{L1}/p_{T}^{Gen})")
    output_f_hists.WriteTObject(h2d_rsp_gen)

    # Draw rsp (pT^L1/pT^Gen) Vs L1 pT
    # rsp here is ref jet pt / l1 jet pt
    tree_raw.Draw("1./rsp:pt>>h2d_rsp_l1(%d,%g,%g,200,0,6)" % (nb, min, max), cstr)
    h2d_rsp_l1 = ROOT.gROOT.FindObject("h2d_rsp_l1")
    h2d_rsp_l1.SetTitle(";p_{T}^{L1};response (p_{T}^{L1}/p_{T}^{Gen})")
    output_f_hists.WriteTObject(h2d_rsp_l1)

    # draw pT^Gen Vs pT^L1
    tree_raw.Draw("pt:rsp*pt>>h2d_gen_l1(%d,%g,%g,%d,%g,%g)" % (nb, min, max, nb, min, max), cstr)
    h2d_gen_l1 = ROOT.gROOT.FindObject("h2d_gen_l1")
    h2d_gen_l1.SetTitle(";p_{T}^{Gen};p_{T}^{L1}")
    output_f_hists.WriteTObject(h2d_gen_l1)

    # Go through and find histogram bin edges that are cloest to the input pt
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
    max_pt = 0
    for i, ptR in enumerate(ptBins[0:-1]):
        # Iterate over pT^Gen bins, and for each:
        # - Project 2D hist so we have a plot of response for given pT^Gen range
        # - Fit a Gaussian (if possible) to this resp histogram to get <rsp>
        # - Plot the L1 pT for given pT^Gen range (remember, for matched pairs)
        # - Get average response from 1D L1 pT hist
        # - Add a new graph point, x=<pT^L1> y=<response> for this pT^Gen bin

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
        hc = h2d_rsp_gen.ProjectionY("prj_%s_%sBin%d" % (name, ext, i), bin1, bin2)
        hc.SetName("Rsp_genpt_%g_%g" % (xlow, xhigh))

        # Plots of pT L1 for given pT Gen bin
        tree_raw.Draw("pt>>hpt(200)", cstr + " && pt*rsp < %g && pt*rsp > %g " % (xhigh, xlow))
        hpt = ROOT.gROOT.FindObject("hpt")
        hpt.SetName("L1_pt_genpt_%g_%g" % (xlow, xhigh))
        output_f_hists.WriteTObject(hpt)

        # Plots of pT Gen for given pT Gen bin
        tree_raw.Draw("pt*rsp>>hpt_gen(200)", cstr + " && pt*rsp < %g && pt*rsp > %g " % (xhigh, xlow))
        hpt_gen = ROOT.gROOT.FindObject("hpt_gen")
        hpt_gen.SetName("gen_pt_genpt_%g_%g" % (xlow, xhigh))
        output_f_hists.WriteTObject(hpt_gen)

        # Fit Gaussian to response curve
        fitStatus = -1
        if hc.GetEntries() > 0:
            fitStatus = int(hc.Fit("gaus", "Q", "R", hc.GetMean() - 1. * hc.GetRMS(), hc.GetMean() + 1. * hc.GetRMS()))
        output_f_hists.WriteTObject(hc)

        if hpt.GetEntries() < 0 or hc.GetEntries() < 0:
            continue

        if fitStatus < 0:
            continue

        mean = hc.GetFunction("gaus").GetParameter(1)
        err = hc.GetFunction("gaus").GetParError(1)
        # check if fit mean is close to raw mean - if not use raw mean since
        # we have a bad fit
        if abs(mean - hc.GetMean()) > (hc.GetMean()*0.2):
            print "Fit mean differs to Raw mean:", mean, hc.GetMean(), bin1, bin2, absetamin, absetamax
            mean = hc.GetMean()
            err = hc.GetMeanError()
        if err < 0:
            raise Exception("Error < 0")

        print "pT Gen: ", ptR, "-", ptBins[i + 1], "<pT L1>:", hpt.GetMean(), \
               "<pT Gen>:", hpt_gen.GetMean(), "<rsp>:", mean

        max_pt = hpt.GetMean() if hpt.GetMean() > max_pt else max_pt
        gr.SetPoint(grc, hpt.GetMean(), 1. / mean)
        gr.SetPointError(grc, hpt.GetMeanError(), err)
        gr_gen.SetPoint(grc, hpt_gen.GetMean(), 1. / mean)
        # gr_gen.SetPointError(grc, hpt.GetMeanError(), err)
        grc += 1

    # Now fit to the response curve to get out correction fn
    thisfit = fitfcn.Clone()
    thisfit.SetName(fitfcn.GetName() + 'eta_%g_%g' % (absetamin, absetamax))
    print "Fitting", fitmin, max_pt
    gr.Fit(thisfit.GetName(), "", "R+", fitmin, max_pt)
    gr.SetName('l1corr_eta_%g_%g' % (absetamin, absetamax))
    gr.GetXaxis().SetTitle("<p_{T}^{L1}>")
    gr.GetYaxis().SetTitle("1/<p_{T}^{L1}/p_{T}^{Gen}>")

    gr_gen.SetName('gencorr_eta_%g_%g' % (absetamin, absetamax))
    gr_gen.GetXaxis().SetTitle("<p_{T}^{Gen}>")
    gr_gen.GetYaxis().SetTitle("1/<p_{T}^{L1}/p_{T}^{Gen}>")

    # Get out fit params
    tmp_params = []
    for i in range(thisfit.GetNumberFreeParameters()):
        tmp_params.append(thisfit.GetParameter(i))

    fit_params.append(tmp_params)

    outputfile.WriteTObject(gr)
    outputfile.WriteTObject(thisfit)
    outputfile.WriteTObject(gr_gen)


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
    inputf = ROOT.TFile(sys.argv[1])
    output_f = ROOT.TFile(sys.argv[2], "RECREATE")
    print sys.argv[1]
    print sys.argv[2]

    # Setup pt, eta bins for doing calibrations
    ptBins = list(numpy.arange(14, 254, 4))
    # ptBins = list(numpy.concatenate((numpy.array([14, 18, 22, 24]), numpy.arange(28, 252, 4)))) # slightly odd binning here - why?
    # ptBins = list(numpy.concatenate((numpy.arange(14, 218, 4), numpy.arange(218, 266, 12)))) # slightly odd binning here - why?
    etaBins = [0.0, 0.348, 0.695, 1.044, 1.392, 1.74, 2.172, 3.0, 3.5, 4.0, 4.5, 5.001][0:2]

    print "Running over eta bins:", etaBins

    # Do plots & fitting to get calib consts
    fit_params = []
    for i,eta in enumerate(etaBins[0:-1]):
        emin = eta
        emax = etaBins[i+1]
        makeResponseCurves(inputf, output_f, ptBins, emin, emax, fit_params)

    # Make LUT
    # print_lut_screen(fit_params, etaBins)
    # dname, fname = os.path.split(sys.argv[2])
    # lut_filename = "LUT_"+fname.replace(".root", ".py").replace("output_", "")
    # print_lut_file(fit_params, etaBins, dname+"/"+lut_filename)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Usage:"
        print "python runCalibration <inputfile> <outputfile>"
        exit(1)

    main()
