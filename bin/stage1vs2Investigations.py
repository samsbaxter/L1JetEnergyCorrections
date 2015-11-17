#!/usr/bin/env python

"""
Quick n dirty script to compare the indiviudal histograms that go into
making the calibration curves for stage 1 and stage 2
"""


import ROOT
import os
import binning
import common_utils as cu
from collections import namedtuple


ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(1)
ROOT.TH1.SetDefaultSumw2()
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPalette(55)


def norm_hist(h):
    h.Scale(1./h.Integral())


def make_plots(filenames, oDir, hist_names, title):

    c = ROOT.TCanvas("", "", 800, 600)
    c.SetTicks(1, 1)

    files = [cu.open_root_file(f.filename) for f in filenames]

    for hname in hist_names:
        # print hname
        hists = [cu.get_from_file(f, hname).Clone() for f in files]

        leg = ROOT.TLegend(0.6, 0.6, 0.85, 0.85)

        for i, h in enumerate(hists):
            norm_hist(h)
            h.Rebin(2)
            h.SetTitle('%s: %s' % (title, hname))
            h.SetLineColor(filenames[i].color)
            if i == 0:
                h.Draw("HISTE")
            else:
                h.Draw("HISTE SAME")
            leg.AddEntry(h, filenames[i].label, "L")

        leg.Draw()

        outname = os.path.join(oDir, hname+'.pdf')
        cu.check_dir_exists_create(os.path.dirname(outname))
        c.SaveAs(os.path.join(oDir, hname+'.pdf'))


if __name__ == "__main__":

    # hists to plot
    hist_names = ['eta_0_0.348/Histograms/Rsp_genpt_%g_%g' % (pt_min, pt_max)
                  for pt_min, pt_max in
                  zip(binning.pt_bins_stage2[1:20], binning.pt_bins_stage2[2:21])]
    # no 10-14 bin for stage 1

    # handy container
    File = namedtuple('File', 'filename color label')

    # STAGE 1 PLOTS
    filenames_s1 = [
        File('/users/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/Stage1_QCDFlatSpring15BX25HCALFix_stage1NoLut_rctv4_jetSeed0_newPUSmc/output/output_QCDFlatSpring15BX25FlatNoPUHCALFix_Stage1_MCRUN2_74_V9_jetSeed0_noStage1Lut_newPUSmc_rctv4_preGt_ak4_ref14to1000_l10to500_dr0p7.root',
             ROOT.kRed, '0PU'),
        File('/users/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/Stage1_QCDFlatSpring15BX25HCALFix_stage1NoLut_rctv4_jetSeed0_newPUSmc/output/output_QCDFlatSpring15BX25PU10to30HCALFix_Stage1_MCRUN2_74_V9_jetSeed0_noStage1Lut_newPUSmc_rctv4_preGt_ak4_ref14to1000_l10to500_dr0p7_PU0to10.root',
             ROOT.kBlue, 'PU: 0 - 10'),
        File('/users/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/Stage1_QCDFlatSpring15BX25HCALFix_stage1NoLut_rctv4_jetSeed0_newPUSmc/output/output_QCDFlatSpring15BX25PU10to30HCALFix_Stage1_MCRUN2_74_V9_jetSeed0_noStage1Lut_newPUSmc_rctv4_preGt_ak4_ref14to1000_l10to500_dr0p7_PU15to25.root',
             ROOT.kBlack, 'PU: 15 - 25'),
        File('/users/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/Stage1_QCDFlatSpring15BX25HCALFix_stage1NoLut_rctv4_jetSeed0_newPUSmc/output/output_QCDFlatSpring15BX25PU10to30HCALFix_Stage1_MCRUN2_74_V9_jetSeed0_noStage1Lut_newPUSmc_rctv4_preGt_ak4_ref14to1000_l10to500_dr0p7_PU30to40.root',
             ROOT.kGreen+2, 'PU: 30-40')
    ]

    oDir_s1 = '/users/ra12451/L1JEC/CMSSW_7_5_0_pre5/src/L1Trigger/L1JetEnergyCorrections/Stage1VsStage2/Stage1'

    make_plots(filenames_s1, oDir_s1, hist_names, "Stage 1")

    # STAGE 2 PLOTS
    filenames_s2 = [
        File('/users/ra12451/L1JEC/CMSSW_7_5_0_pre5/src/L1Trigger/L1JetEnergyCorrections/Stage2_QCDFlatSpring15BX25HCALFix_layer2NoLut_jetSeed0/output/output_QCDFlatSpring15BX25FlatNoPUHCALFix_Stage2_MCRUN2_74_V9_jetSeed0_MP_ak4_ref10to5000_l10to5000_dr0p4_betterBinning.root',
             ROOT.kRed, '0PU'),
        File('/users/ra12451/L1JEC/CMSSW_7_5_0_pre5/src/L1Trigger/L1JetEnergyCorrections/Stage2_QCDFlatSpring15BX25HCALFix_layer2NoLut_jetSeed0/output/output_QCDFlatSpring15BX25PU10to30HCALFix_Stage2_MCRUN2_74_V9_jetSeed0_MP_ak4_ref10to5000_l10to5000_dr0p4_PU0to10_betterBinning.root',
             ROOT.kBlue, 'PU: 0 - 10'),
        File('/users/ra12451/L1JEC/CMSSW_7_5_0_pre5/src/L1Trigger/L1JetEnergyCorrections/Stage2_QCDFlatSpring15BX25HCALFix_layer2NoLut_jetSeed0/output/output_QCDFlatSpring15BX25PU10to30HCALFix_Stage2_MCRUN2_74_V9_jetSeed0_MP_ak4_ref10to5000_l10to5000_dr0p4_PU15to25_betterBinning.root',
             ROOT.kBlack, 'PU: 15 - 25'),
        File('/users/ra12451/L1JEC/CMSSW_7_5_0_pre5/src/L1Trigger/L1JetEnergyCorrections/Stage2_QCDFlatSpring15BX25HCALFix_layer2NoLut_jetSeed0/output/output_QCDFlatSpring15BX25PU10to30HCALFix_Stage2_MCRUN2_74_V9_jetSeed0_MP_ak4_ref10to5000_l10to5000_dr0p4_PU30to40_betterBinning.root',
             ROOT.kGreen+2, 'PU: 30-40')
    ]

    oDir_s2 = '/users/ra12451/L1JEC/CMSSW_7_5_0_pre5/src/L1Trigger/L1JetEnergyCorrections/Stage1VsStage2/Stage2'

    make_plots(filenames_s2, oDir_s2, hist_names, "Stage 2")
