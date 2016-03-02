#!/bin/usr/env python
"""
Little script to plot several graphs and/or fit functions on the same canvas.
Can take any graph, from any file.

TODO: expand to hists?
"""


import os
import ROOT
import binning
from binning import pairwise
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

    s2_new = '/users/ra12451/L1JEC/CMSSW_8_0_0_pre5/src/L1Trigger/L1JetEnergyCorrections/Stage2_HF_QCDFlatSpring15BX25HCALFix_12Feb_85a0ccf_noJEC_fixedPUS/output'
    f_0PU_new = os.path.join(s2_new, 'output_QCDFlatSpring15BX25FlatNoPUHCALFix_MP_ak4_ref10to5000_l10to5000_dr0p4.root')
    f_PU0to10_new = os.path.join(s2_new, 'output_QCDFlatSpring15BX25PU10to30HCALFix_MP_ak4_ref10to5000_l10to5000_dr0p4_PU0to10.root')
    f_PU15to25_new = os.path.join(s2_new, 'output_QCDFlatSpring15BX25PU10to30HCALFix_MP_ak4_ref10to5000_l10to5000_dr0p4_PU15to25.root')
    f_PU30to40_new = os.path.join(s2_new, 'output_QCDFlatSpring15BX25PU10to30HCALFix_MP_ak4_ref10to5000_l10to5000_dr0p4_PU30to40.root')

    # s2_old = '/users/ra12451/L1JEC/CMSSW_7_6_0_pre7/src/L1Trigger/L1JetEnergyCorrections/Stage2_QCDFlatSpring15BX25HCALFix_26Nov_76X_mcRun2_asymptotic_v5_jetSeed1p5_noJec_v2/output/'
    # f_0PU_old = os.path.join(s2_old, 'output_QCDFlatSpring15BX25FlatNoPUHCALFix_MP_ak4_ref10to5000_l10to5000_dr0p4_orig.root')
    # f_PU0to10_old = os.path.join(s2_old, 'output_QCDFlatSpring15BX25PU10to30HCALFix_MP_ak4_ref10to5000_l10to5000_dr0p4_PU0to10_orig.root')
    # f_PU15to25_old = os.path.join(s2_old, 'output_QCDFlatSpring15BX25PU10to30HCALFix_MP_ak4_ref10to5000_l10to5000_dr0p4_PU15to25_orig.root')
    # f_PU30to40_old = os.path.join(s2_old, 'output_QCDFlatSpring15BX25PU10to30HCALFix_MP_ak4_ref10to5000_l10to5000_dr0p4_PU30to40_orig.root')

    # s2_buggy = '/users/ra12451/L1JEC/CMSSW_8_0_0_pre5/src/L1Trigger/L1JetEnergyCorrections/Stage2_HF_QCDFlatSpring15BX25HCALFix_10Feb_2dd1043_noJEC_v2/output'
    # f_0PU_buggy = os.path.join(s2_buggy, 'output_QCDFlatSpring15BX25FlatNoPUHCALFix_MP_ak4_ref10to5000_l10to5000_dr0p4.root')
    # f_PU0to10_buggy = os.path.join(s2_buggy, 'output_QCDFlatSpring15BX25PU10to30HCALFix_MP_ak4_ref10to5000_l10to5000_dr0p4_PU0to10.root')
    # f_PU15to25_buggy = os.path.join(s2_buggy, 'output_QCDFlatSpring15BX25PU10to30HCALFix_MP_ak4_ref10to5000_l10to5000_dr0p4_PU15to25.root')
    # f_PU30to40_buggy = os.path.join(s2_buggy, 'output_QCDFlatSpring15BX25PU10to30HCALFix_MP_ak4_ref10to5000_l10to5000_dr0p4_PU30to40.root')

    # s2_maxPUS = '/users/ra12451/L1JEC/CMSSW_8_0_0_pre5/src/L1Trigger/L1JetEnergyCorrections/Stage2_HF_QCDFlatSpring15BX25HCALFix_13Feb_85a0ccf_noJEC_PUSmax/output'
    # f_PU0to10_maxPUS = os.path.join(s2_maxPUS, 'output_QCDFlatSpring15BX25PU10to30HCALFix_MP_ak4_ref10to5000_l10to5000_dr0p4_PU0to10.root')
    # f_PU15to25_maxPUS = os.path.join(s2_maxPUS, 'output_QCDFlatSpring15BX25PU10to30HCALFix_MP_ak4_ref10to5000_l10to5000_dr0p4_PU15to25.root')
    # f_PU30to40_maxPUS = os.path.join(s2_maxPUS, 'output_QCDFlatSpring15BX25PU10to30HCALFix_MP_ak4_ref10to5000_l10to5000_dr0p4_PU30to40.root')

    s2_data = '/users/ra12451/L1JEC/CMSSW_8_0_0_pre6/src/L1Trigger/L1JetEnergyCorrections/run260627_SingleMuReReco_HF_noL1JEC_3bf1b93_20Feb_Bristol_v3/output'
    f_PU0to5_data = os.path.join(s2_data, 'output_SingleMuReReco_ak4_ref10to5000_l10to5000_dr0p4_cleanTIGHTLEPVETO_PU0to5.root')
    f_PU8to12_data = os.path.join(s2_data, 'output_SingleMuReReco_ak4_ref10to5000_l10to5000_dr0p4_cleanTIGHTLEPVETO_PU8to12.root')
    f_PU15to25_data = os.path.join(s2_data, 'output_SingleMuReReco_ak4_ref10to5000_l10to5000_dr0p4_cleanTIGHTLEPVETO_PU15to25.root')
    f_allPU_data = os.path.join(s2_data, 'output_SingleMuReReco_ak4_ref10to5000_l10to5000_dr0p4_cleanTIGHTLEPVETO.root')

    s2_L1PF = '/users/ra12451/L1JEC/CMSSW_8_0_0_pre6/src/L1Trigger/L1JetEnergyCorrections/Stage2_HF_QCDSpring15_20Feb_3bf1b93_noL1JEC_PFJets_V7PFJEC/output'
    f_PU0to10_L1PF = os.path.join(s2_L1PF, 'output_QCDFlatSpring15BX25PU10to30HCALFix_MP_ak4_PF10to5000_l10to5000_dr0p4_noCleaning_PU0to10.root')
    f_PU15to25_L1PF = os.path.join(s2_L1PF, 'output_QCDFlatSpring15BX25PU10to30HCALFix_MP_ak4_PF10to5000_l10to5000_dr0p4_noCleaning_PU15to25.root')
    f_PU30to40_L1PF = os.path.join(s2_L1PF, 'output_QCDFlatSpring15BX25PU10to30HCALFix_MP_ak4_PF10to5000_l10to5000_dr0p4_noCleaning_PU30to40.root')

    zoom_pt = [0, 150]

    # --------------------------------------------------------------------
    # New Stage 2 curves
    # Plot different PU scenarios for given eta bin
    # --------------------------------------------------------------------
    for i, (eta_min, eta_max) in enumerate(pairwise(binning.eta_bins)):
        graphs = [
            Contribution(file_name=f_0PU_new, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="0PU", line_color=colors[0], marker_color=colors[0]),
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
        ylim = None
        if eta_min > 2:
            ylim = [0, 3.5]
        p = Plot(contributions=graphs, what="graph", xtitle="<p_{T}^{L1}>", ytitle="Correction value (= 1/response)",
                 title="Spring15 MC, no JEC, Stage 2, %g < |#eta| < %g" % (eta_min, eta_max), xlim=zoom_pt, ylim=ylim)
        p.plot()
        p.save(os.path.join(oDir, "compare_PU_eta_%g_%g_pTzoomed.pdf" % (eta_min, eta_max)))

        xlim = None

    """
    # --------------------------------------------------------------------
    # New vs Old curves
    # --------------------------------------------------------------------
    for i, (eta_min, eta_max) in enumerate(pairwise(binning.eta_bins_central)):

        new_graphs = [
            # Contribution(file_name=f_0PU_new, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
            #              label="0PU (800pre5)", line_color=colors[0], marker_color=colors[0]),
            Contribution(file_name=f_PU0to10_new, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 0 - 10 (800pre5)", line_color=colors[1], marker_color=colors[1]),
            Contribution(file_name=f_PU15to25_new, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 15 - 25 (800pre5)", line_color=colors[2], marker_color=colors[2]),
            Contribution(file_name=f_PU30to40_new, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 30 - 40 (800pre5)", line_color=colors[3], marker_color=colors[3])
        ]

        old_graphs = [
            # Contribution(file_name=f_0PU_old, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
            #              label="0PU (760pre7)", line_style=2, line_color=colors[0], marker_color=colors[0]),
            Contribution(file_name=f_PU0to10_old, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 0 - 10 (760pre7)", line_style=2, line_color=colors[1], marker_color=colors[1]),
            Contribution(file_name=f_PU15to25_old, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 15 - 25 (760pre7)", line_style=2, line_color=colors[2], marker_color=colors[2]),
            Contribution(file_name=f_PU30to40_old, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 30 - 40 (760pre7)", line_style=2, line_color=colors[3], marker_color=colors[3])
        ]
        ylim = None
        if eta_min > 2:
            ylim = [0, 3.5]

        oDir = s2_new
        for i, pu_label in enumerate(['PU0to10', 'PU15to25', 'PU30to40']):
            p = Plot(contributions=[new_graphs[i], old_graphs[i]], what="graph", xtitle="<p_{T}^{L1}>", ytitle="Correction value (= 1/response)",
                     title="Spring15 MC, no JEC, Stage 2, %g < |#eta| < %g" % (eta_min, eta_max), ylim=ylim)
            p.plot()
            p.save(os.path.join(oDir, "compare_800pre5_760pre7_eta_%g_%g_%s.pdf" % (eta_min, eta_max, pu_label)))
    """
    """
    # --------------------------------------------------------------------
    # Min PUS vs max PUS curves
    # --------------------------------------------------------------------
    for i, (eta_min, eta_max) in enumerate(pairwise(binning.eta_bins)):

        new_graphs = [
            Contribution(file_name=f_PU0to10_new, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 0 - 10 (min PUS)", line_color=colors[1], marker_color=colors[1]),
            Contribution(file_name=f_PU15to25_new, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 15 - 25 (min PUS)", line_color=colors[2], marker_color=colors[2]),
            Contribution(file_name=f_PU30to40_new, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 30 - 40 (min PUS)", line_color=colors[3], marker_color=colors[3])
        ]

        buggy_graphs = [
            Contribution(file_name=f_PU0to10_maxPUS, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 0 - 10 (max PUS)", line_style=2, line_color=colors[1], marker_color=colors[1]),
            Contribution(file_name=f_PU15to25_maxPUS, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 15 - 25 (max PUS)", line_style=2, line_color=colors[2], marker_color=colors[2]),
            Contribution(file_name=f_PU30to40_maxPUS, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 30 - 40 (max PUS)", line_style=2, line_color=colors[3], marker_color=colors[3])
        ]
        ylim = None
        if eta_min > 2:
            ylim = [0, 3.5]

        oDir = s2_maxPUS
        for i, pu_label in enumerate(['PU0to10', 'PU15to25', 'PU30to40']):
            p = Plot(contributions=[new_graphs[i], buggy_graphs[i]], what="graph", xtitle="<p_{T}^{L1}>", ytitle="Correction value (= 1/response)",
                     title="Spring15 MC, no JEC, Stage 2, %g < |#eta| < %g" % (eta_min, eta_max), ylim=ylim)
            p.plot()
            p.save(os.path.join(oDir, "compare_minPUS_maxPUS_eta_%g_%g_%s.pdf" % (eta_min, eta_max, pu_label)))

    """
    """

    for i, (eta_min, eta_max) in enumerate(pairwise(binning.eta_bins)):
        # --------------------------------------------------------------------
        # Plot diff PU scenarios for given eta bin, for max PUS ntuples
        # --------------------------------------------------------------------
        graphs = [
            Contribution(file_name=f_PU0to10_maxPUS, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 0 - 10", line_color=colors[1], marker_color=colors[1]),
            Contribution(file_name=f_PU15to25_maxPUS, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 15 - 25", line_color=colors[2], marker_color=colors[2]),
            Contribution(file_name=f_PU30to40_maxPUS, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 30 - 40", line_color=colors[3], marker_color=colors[3])
        ]

        ylim = None
        if eta_min > 2.9:
            ylim = [0, 3.5]
        p = Plot(contributions=graphs, what="graph", xtitle="<p_{T}^{L1}>", ytitle="Correction value (= 1/response)",
                 title="Spring15 MC, no JEC, Stage 2, max PUS, %g < |#eta| < %g" % (eta_min, eta_max), ylim=ylim)
        p.plot()
        oDir = s2_maxPUS
        p.save(os.path.join(oDir, "compare_PU_eta_%g_%g.pdf" % (eta_min, eta_max)))

        # zoom in on low pT
        ylim = None
        if eta_min > 2.9:
            ylim = [0, 3.5]
        p = Plot(contributions=graphs, what="graph", xtitle="<p_{T}^{L1}>", ytitle="Correction value (= 1/response)",
                 title="Spring15 MC, no JEC, Stage 2, max PUS, %g < |#eta| < %g" % (eta_min, eta_max), xlim=zoom_pt, ylim=ylim)
        p.plot()
        p.save(os.path.join(oDir, "compare_PU_eta_%g_%g_pTzoomed.pdf" % (eta_min, eta_max)))

        xlim = None
    """

    # --------------------------------------------------------------------
    # New Stage 2 curves for DATA
    # Plot different PU scenarios for given eta bin
    # --------------------------------------------------------------------
    for i, (eta_min, eta_max) in enumerate(pairwise(binning.eta_bins)):
        graphs = [
            Contribution(file_name=f_PU0to5_data, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 0 - 5", line_color=colors[1], marker_color=colors[1]),
            Contribution(file_name=f_PU8to12_data, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 8 - 12", line_color=colors[2], marker_color=colors[2]),
            Contribution(file_name=f_PU15to25_data, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 15 - 25", line_color=colors[3], marker_color=colors[3]),
            Contribution(file_name=f_allPU_data, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="All PU", line_color=colors[4], marker_color=colors[4])
        ]

        ylim = None
        if eta_min > 2:
            ylim = [0, 3.5]
        title = "Run 260627 (SingleMu, no JEC, TightLepVeto + elMult0 + muMult0), Stage 2, %g < |#eta| < %g" % (eta_min, eta_max)
        p = Plot(contributions=graphs, what="graph", xtitle="<p_{T}^{L1}>", ytitle="Correction value (= 1/response)",
                 title=title, ylim=ylim)
        p.plot()
        oDir = s2_data
        p.save(os.path.join(oDir, "compare_PU_eta_%g_%g.pdf" % (eta_min, eta_max)))

        # zoom in on low pT
        ylim = None
        if eta_min > 2:
            ylim = [0, 3.5]
        p = Plot(contributions=graphs, what="graph", xtitle="<p_{T}^{L1}>", ytitle="Correction value (= 1/response)",
                 title=title, xlim=zoom_pt, ylim=ylim)
        p.plot()
        p.save(os.path.join(oDir, "compare_PU_eta_%g_%g_pTzoomed.pdf" % (eta_min, eta_max)))

        xlim = None


    # --------------------------------------------------------------------
    # DATA vs MC (L1-Gen) curves (all PU for data, PU binned for MC)
    # --------------------------------------------------------------------
    for i, (eta_min, eta_max) in enumerate(pairwise(binning.eta_bins_central)):

        graphs = [
            Contribution(file_name=f_allPU_data, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="DATA: All PU (<nVtx> ~ 10)", line_color=colors[4], marker_color=colors[4]),
            Contribution(file_name=f_0PU_new, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="MC, 0PU", line_color=colors[0], marker_color=colors[0]),
            Contribution(file_name=f_PU0to10_new, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="MC, PU: 0 - 10", line_color=colors[1], marker_color=colors[1]),
            Contribution(file_name=f_PU15to25_new, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="MC, PU: 15 - 25", line_color=colors[2], marker_color=colors[2]),
            Contribution(file_name=f_PU30to40_new, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="MC, PU: 30 - 40", line_color=colors[3], marker_color=colors[3])
        ]

        ylim = None
        if eta_min > 2:
            ylim = [0, 3.5]
        title = "Run 260627 (SingleMu, no JEC, TightLepVeto + elMult0 + muMult0) VS Spring 15 QCD MC L1 vs GenJet, Stage 2, %g < |#eta| < %g" % (eta_min, eta_max)
        p = Plot(contributions=graphs, what="graph", xtitle="<p_{T}^{L1}>", ytitle="Correction value (= 1/response)",
                 title=title, ylim=ylim)
        p.plot()
        oDir = s2_data
        p.save(os.path.join(oDir, "compare_data_mcSpring15_l1gen_eta_%g_%g.pdf" % (eta_min, eta_max)))

        # zoom in on low pT
        ylim = None
        if eta_min > 2:
            ylim = [0, 3.5]
        p = Plot(contributions=graphs, what="graph", xtitle="<p_{T}^{L1}>", ytitle="Correction value (= 1/response)",
                 title=title, xlim=zoom_pt, ylim=ylim)
        p.plot()
        p.save(os.path.join(oDir, "compare_data_mcSpring15_l1gen_eta_%g_%g_pTzoomed.pdf" % (eta_min, eta_max)))

        xlim = None

    # --------------------------------------------------------------------
    # DATA vs MC (L1-PF) curves (all PU for data, PU binned for MC)
    # --------------------------------------------------------------------
    for i, (eta_min, eta_max) in enumerate(pairwise(binning.eta_bins_central)):

        graphs = [
            Contribution(file_name=f_allPU_data, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="DATA: All PU (<nVtx> ~ 10)", line_color=colors[4], marker_color=colors[4]),
            Contribution(file_name=f_PU0to10_L1PF, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="MC, PU: 0 - 10", line_color=colors[1], marker_color=colors[1]),
            Contribution(file_name=f_PU15to25_L1PF, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="MC, PU: 15 - 25", line_color=colors[2], marker_color=colors[2]),
            Contribution(file_name=f_PU30to40_L1PF, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="MC, PU: 30 - 40", line_color=colors[3], marker_color=colors[3])
        ]

        ylim = None
        if eta_min > 2:
            ylim = [0, 3.5]
        title = "Run 260627 (SingleMu, no JEC, TightLepVeto + elMult0 + muMult0) VS Spring 15 QCD MC L1 vs PF, Stage 2, L1 vs PF, %g < |#eta| < %g" % (eta_min, eta_max)
        p = Plot(contributions=graphs, what="graph", xtitle="<p_{T}^{L1}>", ytitle="Correction value (= 1/response)",
                 title=title, ylim=ylim)
        p.plot()
        oDir = s2_data
        p.save(os.path.join(oDir, "compare_data_mcSpring15_l1pf_eta_%g_%g.pdf" % (eta_min, eta_max)))

        # zoom in on low pT
        ylim = None
        if eta_min > 2:
            ylim = [0, 3.5]
        p = Plot(contributions=graphs, what="graph", xtitle="<p_{T}^{L1}>", ytitle="Correction value (= 1/response)",
                 title=title, xlim=zoom_pt, ylim=ylim)
        p.plot()
        p.save(os.path.join(oDir, "compare_data_mcSpring15_l1pf_eta_%g_%g_pTzoomed.pdf" % (eta_min, eta_max)))

        xlim = None

    # --------------------------------------------------------------------
    # L1-Gen vs L1-PF curves
    # --------------------------------------------------------------------
    for i, (eta_min, eta_max) in enumerate(pairwise(binning.eta_bins)):

        new_graphs = [
            Contribution(file_name=f_PU0to10_new, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 0 - 10 (L1-Gen)", line_color=colors[1], marker_color=colors[1]),
            Contribution(file_name=f_PU15to25_new, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 15 - 25 (L1-Gen)", line_color=colors[2], marker_color=colors[2]),
            Contribution(file_name=f_PU30to40_new, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 30 - 40 (L1-Gen)", line_color=colors[3], marker_color=colors[3])
        ]

        L1PF_graphs = [
            Contribution(file_name=f_PU0to10_L1PF, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 0 - 10 (L1-PF)", line_style=2, line_color=colors[1], marker_color=colors[1]),
            Contribution(file_name=f_PU15to25_L1PF, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 15 - 25 (L1-PF)", line_style=2, line_color=colors[2], marker_color=colors[2]),
            Contribution(file_name=f_PU30to40_L1PF, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 30 - 40 (L1-PF)", line_style=2, line_color=colors[3], marker_color=colors[3])
        ]
        ylim = None
        if eta_min > 2:
            ylim = [0, 3.5]

        oDir = s2_L1PF
        for i, pu_label in enumerate(['PU0to10', 'PU15to25', 'PU30to40']):
            p = Plot(contributions=[new_graphs[i], L1PF_graphs[i]], what="graph", xtitle="<p_{T}^{L1}>", ytitle="Correction value (= 1/response)",
                     title="Spring15 MC, no L1JEC, Stage 2, no PF JetID, %g < |#eta| < %g" % (eta_min, eta_max), ylim=ylim)
            p.plot()
            p.save(os.path.join(oDir, "compare_L1Gen_L1PF_eta_%g_%g_%s.pdf" % (eta_min, eta_max, pu_label)))

            p = Plot(contributions=[new_graphs[i], L1PF_graphs[i]], what="graph", xtitle="<p_{T}^{L1}>", ytitle="Correction value (= 1/response)",
                     title="Spring15 MC, no L1JEC, Stage 2, no PF JetID, %g < |#eta| < %g" % (eta_min, eta_max), xlim=zoom_pt, ylim=ylim)
            p.plot()
            p.save(os.path.join(oDir, "compare_L1Gen_L1PF_eta_%g_%g_%s_pTzoomed.pdf" % (eta_min, eta_max, pu_label)))

if __name__ == "__main__":
    compare()
