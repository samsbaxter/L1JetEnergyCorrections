#!/usr/bin/env python
"""
Short script to quick make response histograms, binned by eta.
"""

import ROOT
import binning
import common_utils as cu


ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(1)
ROOT.gStyle.SetOptFit(1111)
ROOT.TH1.SetDefaultSumw2(True)


def make_plot_eta_binned(input_filename, output_filename, title=''):
    f = cu.open_root_file(input_filename)
    tree = cu.get_from_file(f, 'valid')

    hists = []

    eta_bins = binning.eta_bins
    # eta_bins = [0, 3, 5]
    for i, (eta_min, eta_max) in enumerate(binning.pairwise(eta_bins)):
        hname = "h_%g_%g" % (eta_min, eta_max)
        h = ROOT.TH1D(hname, title + ";response;p.d.f", 30, 0, 3)
        tree.Draw("rsp>>%s" % hname, "%g < TMath::Abs(eta) && TMath::Abs(eta) < %g" % (eta_min, eta_max))
        h.SetLineColor(binning.eta_bin_colors[i])
        h.SetLineWidth(2)
        h.Scale(1. / h.Integral())
        hists.append(h)

    canv = ROOT.TCanvas("c", "", 600, 600)
    canv.SetTicks(1, 1)
    hstack = ROOT.THStack("hst", title + ";response;p.d.f")
    leg = ROOT.TLegend(0.6, 0.6, 0.88, 0.88)
    for i, h in enumerate(hists):
        hstack.Add(h)
        leg.AddEntry(h, '%g < |#eta| < %g' % (eta_bins[i], eta_bins[i + 1]), 'L')

    hstack.Draw("NOSTACK HIST")
    leg.Draw()
    canv.SaveAs(output_filename)


if __name__ == "__main__":
    make_plot_eta_binned('../Stage2_HF_QCDFlatSpring15BX25HCALFix_10Feb_2dd1043_noJEC_v2/output/pairs_noJEC.root',
                         '../Stage2_HF_QCDFlatSpring15BX25HCALFix_10Feb_2dd1043_noJEC_v2/output/quick_check_noJEC.pdf',
                         'Spring15 MC, No JEC')
    make_plot_eta_binned('../Stage2_HF_QCDFlatSpring15BX25HCALFix_10Feb_2dd1043_noJEC_v2/output/pairs_JEC.root',
                         '../Stage2_HF_QCDFlatSpring15BX25HCALFix_10Feb_2dd1043_noJEC_v2/output/quick_check_JEC.pdf',
                         'Spring15 MC, JEC')
