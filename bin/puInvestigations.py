"""
Little script to showoff plots that may showup PU regions Vs signal regions
"""

import ROOT
from common_utils import *
import os


ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(1)
ROOT.TH1.SetDefaultSumw2()
# ROOT.gStyle.SetOptTitle(0);
ROOT.gStyle.SetOptStat(0);
ROOT.gStyle.SetPalette(55)


def make_plots(input_filename, refPtMin, internJet=False, append=""):
    f = open_root_file(input_filename)
    tree = get_from_file(f, "valid")

    c = ROOT.TCanvas("c", "", 800, 600)
    c.SetLogz()

    out_dir = os.path.dirname(input_filename)

    eta_cut = "TMath::Abs(eta)<3"

    # Draw DeltaR Vs Delta pT
    if internJet:
        h_dr_ptdiff = ROOT.TH2D("h_dr_ptdiff", "Intern jets, p_{T}^{Gen} > %g GeV;p_{T}^{L1} - p_{T}^{Gen};#DeltaR" % refPtMin, 375, -1000, 500, 35, 0, 0.7)
    else:
        h_dr_ptdiff = ROOT.TH2D("h_dr_ptdiff", "GCT jets, p_{T}^{Gen} > %g GeV;p_{T}^{L1} - p_{T}^{Gen};#DeltaR" % refPtMin, 189, -504, 252, 35, 0, 0.7)
    tree.Draw("dr:ptDiff>>h_dr_ptdiff", eta_cut, "COLZ")
    out_name = "ptDiff_deltaR_"
    out_name += "GCTintern_" if internJet else "GCTJets_"
    out_name += "refMin%g" % refPtMin
    out_name += append
    out_name += ".pdf"
    c.SaveAs(out_dir+"/"+out_name)

    # Draw pt (l1) Vs Delta pT
    if internJet:
        h_pt_ptdiff = ROOT.TH2D("h_pt_ptdiff", "Intern jets, p_{T}^{Gen} > %g GeV;p_{T}^{L1} - p_{T}^{Gen};p_{T}^{L1}" % refPtMin, 375, -1000, 500, 125, 0, 500)
    else:
        h_pt_ptdiff = ROOT.TH2D("h_pt_ptdiff", "GCT jets, p_{T}^{Gen} > %g GeV;p_{T}^{L1} - p_{T}^{Gen};p_{T}^{L1}" % refPtMin, 189, -504, 252, 63, 0, 252)
    tree.Draw("pt:ptDiff>>h_pt_ptdiff", eta_cut, "COLZ")
    out_name = "ptDiff_pt_"
    out_name += "GCTintern_" if internJet else "GCTJets_"
    out_name += "refMin%g" % refPtMin
    out_name += append
    out_name += ".pdf"
    c.SaveAs(out_dir+"/"+out_name)

    # Draw pt (gen) Vs Delta pT
    if internJet:
        h_ptRef_ptdiff = ROOT.TH2D("h_ptRef_ptdiff", "Intern jets, p_{T}^{Gen} > %g GeV;p_{T}^{L1} - p_{T}^{Gen};p_{T}^{Gen}" % refPtMin, 375, -1000, 500, 125, 0, 500)
    else:
        h_ptRef_ptdiff = ROOT.TH2D("h_ptRef_ptdiff", "GCT jets, p_{T}^{Gen} > %g GeV;p_{T}^{L1} - p_{T}^{Gen};p_{T}^{Gen}" % refPtMin, 189, -504, 252, 125, 0, 500)
    tree.Draw("ptRef:ptDiff>>h_ptRef_ptdiff", eta_cut, "COLZ")
    out_name = "ptDiff_ptRef_"
    out_name += "GCTintern_" if internJet else "GCTJets_"
    out_name += "refMin%g" % refPtMin
    out_name += append
    out_name += ".pdf"
    c.SaveAs(out_dir+"/"+out_name)

    # Draw deltaEta vs deltaPhi
    c.SetLogz(0)
    h_deta_dphi = ROOT.TH2D("h_deta_dphi", "", 70, -0.7, 0.7, 70, -0.7, 0.7)
    if internJet:
        h_deta_dphi.SetTitle("Intern jets, p_{T}^{Gen} > %g GeV;#Delta#phi;#Delta#eta" % refPtMin)
    else:
        h_deta_dphi.SetTitle("GCT jets, p_{T}^{Gen} > %g GeV;#Delta#phi;#Delta#eta" % refPtMin)
    tree.Draw("deta:dphi>>h_deta_dphi", eta_cut,"COLZ")
    out_name = "dEta_dPhi_"
    out_name += "GCTintern_" if internJet else "GCTJets_"
    out_name += "refMin%g" % refPtMin
    out_name += append
    out_name += ".pdf"
    c.SaveAs(out_dir+"/"+out_name)


if __name__ == "__main__":
    make_plots("/afs/cern.ch/work/r/raggleto/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/QCDPhys14_newRCTv2_calibrated/pairs_TTbarPhys14AVE30BX50_GCT_QCDPhys14_newRCTv2_calibrated_GCT_ak5_ref14to1000_l10to500.root", 14, False)
    make_plots("/afs/cern.ch/work/r/raggleto/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/QCDPhys14_newRCTv2_calibrated/pairs_TTbarPhys14AVE30BX50_GCT_QCDPhys14_newRCTv2_calibrated_GCT_ak5_ref14to1000_l10to500_dR0p4.root", 14, False, "_dR0p4")
    make_plots("/afs/cern.ch/work/r/raggleto/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/QCDPhys14_newRCTv2_calibrated/pairs_TTbarPhys14AVE30BX50_GCT_QCDPhys14_newRCTv2_calibrated_GCTintern_ak5_ref14to1000_l10to500_dR0p4.root", 14, True, "_dR0p4")
    make_plots("/afs/cern.ch/work/r/raggleto/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/QCDPhys14_newRCTv2_calibrated/pairs_TTbarPhys14AVE30BX50_GCT_QCDPhys14_newRCTv2_calibrated_GCT_ak5_ref0to500_l10to500.root", 0, False)
    make_plots("/afs/cern.ch/work/r/raggleto/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/QCDPhys14_newRCTv2_calibrated/pairs_TTbarPhys14AVE30BX50_GCT_QCDPhys14_newRCTv2_calibrated_GCTintern_ak5_ref14to1000_l10to500.root", 14, True)
    make_plots("/afs/cern.ch/work/r/raggleto/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/QCDPhys14_newRCTv2_calibrated/pairs_TTbarPhys14AVE30BX50_GCT_QCDPhys14_newRCTv2_calibrated_GCTintern_ak5_ref0to1000_l10to500.root", 0, True)
    make_plots("/afs/cern.ch/work/r/raggleto/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/NeutrinoGunBX50Phys14_newRCTv2_calibrated/pairs_NeutrinoGunBX50Phys14_newRCTv2_calibrated_GCT_ak5_ref14to1000_l10to500.root", 14, False)
    make_plots("/afs/cern.ch/work/r/raggleto/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/NeutrinoGunBX50Phys14_newRCTv2_calibrated/pairs_NeutrinoGunPhys14BX50_GCT_NeutrinoGunBX50Phys14_newRCTv2_calibrated_GCT_ak5_ref0to1000_l10to500.root", 0, False)
    make_plots("/afs/cern.ch/work/r/raggleto/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/NeutrinoGunBX50Phys14_newRCTv2_calibrated/pairs_NeutrinoGunPhys14BX50_GCT_NeutrinoGunBX50Phys14_newRCTv2_calibrated_GCTintern_ak5_ref0to1000_l10to500.root", 0, True)
    make_plots("/afs/cern.ch/work/r/raggleto/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/NeutrinoGunBX50Phys14_newRCTv2_calibrated/pairs_NeutrinoGunPhys14BX50_GCT_NeutrinoGunBX50Phys14_newRCTv2_calibrated_GCTintern_ak5_ref14to1000_l10to500.root", 14, True)
