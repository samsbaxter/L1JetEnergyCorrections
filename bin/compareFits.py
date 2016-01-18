#!/bin/usr/env python
"""
Little script to plot several graphs and/or fit functions on the same canvas.
Can take any graph, from any file.

TODO: expand to hists?

Example usage:

>>> A = Contribution("a.root", "li1corr_eta_0_0.348")
>>> B = Contribution("b.root", "li1corr_eta_0_0.348")
>>> p = Plot([A, B], "graphfunction", xlim=[0, 50])
>>> p.plot()
>>> p.save("AB.pdf")

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

    s2_new = '/users/ra12451/L1JEC/CMSSW_7_6_0_pre7/src/L1Trigger/L1JetEnergyCorrections/Stage2_QCDFlatSpring15BX25HCALFix_26Nov_76X_mcRun2_asymptotic_v5_jetSeed1p5_noJec_v2/output/'
    # f_0PU_new = os.path.join(s2_new, 'output_QCDFlatSpring15BX25FlatNoPUHCALFix_MP_ak4_ref10to5000_l10to5000_dr0p4.root')
    f_PU0to10_new = os.path.join(s2_new, 'output_QCDFlatSpring15BX25PU10to30HCALFix_MP_ak4_ref10to5000_l10to5000_dr0p4_PU0to10.root')
    f_PU15to25_new = os.path.join(s2_new, 'output_QCDFlatSpring15BX25PU10to30HCALFix_MP_ak4_ref10to5000_l10to5000_dr0p4_PU15to25.root')
    f_PU30to40_new = os.path.join(s2_new, 'output_QCDFlatSpring15BX25PU10to30HCALFix_MP_ak4_ref10to5000_l10to5000_dr0p4_PU30to40.root')

    # Loop over eta bins
    for i, (eta_min, eta_max) in enumerate(zip(binning.eta_bins_central[:-1], binning.eta_bins_central[1:])):
        # --------------------------------------------------------------------
        # New Stage 2 curves
        # Compare diff PU scenarios for new MC
        # --------------------------------------------------------------------

        graphs = [
            # Contribution(file_name=f_0PU_new, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
            #              label="0PU", line_color=colors[0], marker_color=colors[0]),
            Contribution(file_name=f_PU0to10_new, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 0 - 10", line_color=colors[1], marker_color=colors[1]),
            Contribution(file_name=f_PU15to25_new, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 15 - 25", line_color=colors[2], marker_color=colors[2]),
            Contribution(file_name=f_PU30to40_new, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 30 - 40", line_color=colors[3], marker_color=colors[3])
        ]
        ylim = None
        if eta_min > 2:
            ylim = [0, 3.5]
        p = Plot(contributions=graphs, what="graph", xtitle="<p_{T}^{L1}>", ytitle="Correction value (= 1/response)",
                 title="Spring15 MC, no JEC, Stage 2, %g < |#eta| < %g" % (eta_min, eta_max), ylim=ylim)
        p.plot()
        oDir = s2_new
        p.save(os.path.join(oDir, "compare_PU_eta_%g_%g.pdf" % (eta_min, eta_max)))

        # zoom in on low pT
        graphs = [
            # Contribution(file_name=f_0PU_new, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
            #              label="0PU", line_color=colors[0], marker_color=colors[0]),
            Contribution(file_name=f_PU0to10_new, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 0 - 10", line_color=colors[1], marker_color=colors[1]),
            Contribution(file_name=f_PU15to25_new, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 15 - 25", line_color=colors[2], marker_color=colors[2]),
            Contribution(file_name=f_PU30to40_new, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 30 - 40", line_color=colors[3], marker_color=colors[3])
        ]
        xlim = [0, 250]
        ylim = None
        if eta_min > 2:
            ylim = [0, 3.5]
        p = Plot(contributions=graphs, what="graph", xtitle="<p_{T}^{L1}>", ytitle="Correction value (= 1/response)",
                 title="Spring15 MC, no JEC, Stage 2, %g < |#eta| < %g" % (eta_min, eta_max), xlim=xlim, ylim=ylim)
        p.plot()
        oDir = s2_new
        p.save(os.path.join(oDir, "compare_PU_eta_%g_%g_pTzoomed.pdf" % (eta_min, eta_max)))

        xlim = None


if __name__ == "__main__":
    compare()
