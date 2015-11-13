#!/bin/usr/env python
"""
Little script to plot several graphs and/or fit functions on the same canvas.
Can take any graph, from any file.

TODO: expand to hists?

Example usage:

    A = Contribution("a.root", "li1corr_eta_0_0.348")
    B = Contribution("b.root", "li1corr_eta_0_0.348")
    p = Plot([A, B], "graphfunction", xlim=[0, 50])
    p.plot()
    p.save("AB.pdf")

"""


import os
import ROOT
import binning as binning
from comparator import Contribution, Plot


ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(1)
ROOT.TH1.SetDefaultSumw2()
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPalette(55)


def compare():
    """Make all da plots"""

    # a set of 11 varying colours
    colors = [ROOT.kRed, ROOT.kBlue, ROOT.kBlack, ROOT.kGreen+2, ROOT.kMagenta,
              ROOT.kOrange+7, ROOT.kAzure+1, ROOT.kRed+3, ROOT.kViolet+1,
              ROOT.kOrange, ROOT.kTeal-5]

    d = "/users/ra12451/L1JEC/CMSSW_7_5_0_pre5/src/L1Trigger/L1JetEnergyCorrections/"

    f_0PU = os.path.join(d, 'Stage2_QCDFlatSpring15BX25HCALFix_layer2NoLut_jetSeed0/output/output_QCDFlatSpring15BX25FlatNoPUHCALFix_Stage2_MCRUN2_74_V9_jetSeed0_MP_ak4_ref10to5000_l10to5000_dr0p4_betterBinning.root')
    f_PU0to10 = os.path.join(d, 'Stage2_QCDFlatSpring15BX25HCALFix_layer2NoLut_jetSeed0/output/output_QCDFlatSpring15BX25PU10to30HCALFix_Stage2_MCRUN2_74_V9_jetSeed0_MP_ak4_ref10to5000_l10to5000_dr0p4_PU0to10_betterBinning.root')
    f_PU15to25 = os.path.join(d, 'Stage2_QCDFlatSpring15BX25HCALFix_layer2NoLut_jetSeed0/output/output_QCDFlatSpring15BX25PU10to30HCALFix_Stage2_MCRUN2_74_V9_jetSeed0_MP_ak4_ref10to5000_l10to5000_dr0p4_PU15to25_betterBinning.root')
    f_PU30to40 = os.path.join(d, 'Stage2_QCDFlatSpring15BX25HCALFix_layer2NoLut_jetSeed0/output/output_QCDFlatSpring15BX25PU10to30HCALFix_Stage2_MCRUN2_74_V9_jetSeed0_MP_ak4_ref10to5000_l10to5000_dr0p4_PU30to40_betterBinning.root')

    # Loop over eta bins
    for i, (eta_min, eta_max) in enumerate(zip(binning.eta_bins[:-1], binning.eta_bins[1:])):

        # --------------------------------------------------------------------
        # Compare diff PU scenarios for new MC
        # --------------------------------------------------------------------
        # no JEC
        ylim = None
        if eta_min > 2.9:
            ylim = [0, 2.5]
        elif eta_min > 3.9:
            ylim = [1.2, 2]
        elif eta_min > 2.17:
            ylim = [1, 4]

        graphs = [
            Contribution(file_name=f_0PU, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="0PU", line_color=colors[0], marker_color=colors[0]),
            Contribution(file_name=f_PU0to10, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 0 - 10", line_color=colors[1], marker_color=colors[1]),
            Contribution(file_name=f_PU15to25, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 15 - 25", line_color=colors[2], marker_color=colors[2]),
            Contribution(file_name=f_PU30to40, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 30 - 40", line_color=colors[3], marker_color=colors[3])
        ]
        p = Plot(contributions=graphs, what="graph", xtitle="<p_{T}^{L1}>", ytitle="Correction value (= 1/response)",
                 title="Spring15 MC, no JEC, Stage 2, %g < |#eta| < %g" % (eta_min, eta_max),
                 ylim=ylim)
        p.plot()
        oDir = "../Stage2_QCDFlatSpring15BX25HCALFix_layer2NoLut_jetSeed0/output/"
        p.save(os.path.join(oDir, "compare_PU_eta_%g_%g.pdf" % (eta_min, eta_max)))


if __name__ == "__main__":
    compare()