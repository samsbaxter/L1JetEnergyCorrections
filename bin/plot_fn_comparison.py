"""
Plot same fn with diff params for comparison
"""

import ROOT
import numpy as np


ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(1)
ROOT.TH1.SetDefaultSumw2()
# ROOT.gStyle.SetOptTitle(0);
ROOT.gStyle.SetOptStat(0);
ROOT.gStyle.SetPalette(55)


def pf_func(et, p0, p1, p2, p3, p4, p5):
    return p0 + (p1/(np.power(np.log10(et), 2)+p2)) + p3 * np.exp(-1.*p4*np.power(np.log10(et)-p5, 2))


def plot_comparison(params1, title1, params2, title2, plotname="fn_compare.pdf"):
    fitfcn = ROOT.TF1("fitfcn", "[0]+[1]/(pow(log10(x),2)+[2])+[3]*exp(-[4]*(log10(x)-[5])*(log10(x)-[5]))", 0, 150)
    fcn1 = fitfcn.Clone("fcn1")
    for i, p in enumerate(params1):
        fcn1.SetParameter(i, p)
    fcn1.SetLineColor(ROOT.kBlack)

    fcn2 = fitfcn.Clone("fcn2")
    for i, p in enumerate(params2):
        fcn2.SetParameter(i, p)
    fcn2.SetLineColor(ROOT.kRed)

    max1 = fcn1.GetMaximum()
    max2 = fcn2.GetMaximum()

    c = ROOT.TCanvas("c", "", 600, 500)
    c.SetTicks(1,1)
    fcn1.Draw()
    fcn2.Draw("SAME")
    fcn1.GetYaxis().SetRangeUser(0, max(max1, max2)*1.1)
    fcn1.GetXaxis().SetTitle("p_{T} [GeV]")

    leg = ROOT.TLegend(0.65, 0.65, 0.88, 0.88)
    leg.AddEntry(fcn1, title1, "L")
    leg.AddEntry(fcn2, title2, "L")
    leg.Draw()

    c.SaveAs(plotname)


if __name__ == "__main__":
    old_0_0p348 = [1.14, 2.297, 5.959, 1.181, 0.7286, 0.3673]
    new_0_0p348 = [3.32079045, 30.10690152, 2.91713150, -206.73606994, 0.00701027, -20.22374281]
    plot_comparison(old_0_0p348, "2012", new_0_0p348, "New", "fn_compare_0_0p348_newRCTv2.pdf")