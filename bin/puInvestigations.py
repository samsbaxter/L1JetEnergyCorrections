"""
Little script to showoff plots that may showup PU regions Vs signal regions
"""

import argparse
import ROOT
from common_utils import *
import os
import sys
import binning


ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(1)
ROOT.TH1.SetDefaultSumw2()
# ROOT.gStyle.SetOptTitle(0);
ROOT.gStyle.SetOptStat(0);
ROOT.gStyle.SetPalette(55)


def make_plots(input_filename, out_dir, refPtMin=0, internJet=False, append=""):
    f = open_root_file(input_filename)
    tree = get_from_file(f, "valid")

    c = ROOT.TCanvas("c", "", 800, 600)
    c.SetLogz()

    colours = [ROOT.kBlack, ROOT.kRed, ROOT.kBlue, ROOT.kGreen+2]

    # Plot deltaR for various pT, eta bins
    for (eta_min, eta_max) in ([0, 0.348], [2.172,3], [3.5,4]):
        eta_cut = "TMath::Abs(eta)>%g && TMath::Abs(eta)< %g" % (eta_min, eta_max)

        for ptVar in ["ptRef"]:
            mg = ROOT.THStack("mg_%s_eta_%g_%g" % (ptVar, eta_min, eta_max),
                              "%g < |#eta^{L1}| < %g;#Delta R(L1, GenJet);" % (eta_min, eta_max))
            leg = ROOT.TLegend(0.6, 0.6, 0.88, 0.88)

            for i, (pt_min, pt_max) in enumerate(([14, 18], [26, 30], [42, 46], [70, 74])):

                pt_cut = "%s > %g && %s < %g" % (ptVar, pt_min, ptVar, pt_max)
                hname = "h_dr_%s_%g_%g_eta_%g_%g" % (ptVar, pt_min, pt_max, eta_min, eta_max)
                h_dr_pt = ROOT.TH1D(hname,
                                    "%g < %s < %g, %g < |#eta^{L1}| < %g;#Delta R(L1, GenJet);N" % (pt_min, ptVar, pt_max, eta_min, eta_max),
                                    35, 0, 0.7)
                total_cut = "%s && %s" % (eta_cut, pt_cut)
                print total_cut
                tree.Draw("dr>>%s" % (hname), total_cut)
                h_dr_pt.Scale(1./h_dr_pt.Integral())
                out_name = hname+".pdf"
                c.SaveAs(out_dir+"/"+out_name)

                h_dr_pt.SetLineColor(colours[i])
                mg.Add(h_dr_pt)
                leg.AddEntry(h_dr_pt, "%g < %s < %g" % (pt_min, ptVar, pt_max), "L")

            mg.Draw("NOSTACK HISTE")
            mg.GetHistogram().SetTitle("%s < |#eta^{L1}| < %g;#Delta R(L1, GenJet);" % (eta_min, eta_max))
            leg.Draw()
            out_name = mg.GetName()+".pdf"
            c.SaveAs(out_dir+"/"+out_name)

    f.Close()

    # Draw DeltaR Vs Delta pT
    # if internJet:
    #     h_dr_ptdiff = ROOT.TH2D("h_dr_ptdiff", "Intern jets, p_{T}^{Gen} > %g GeV;p_{T}^{L1} - p_{T}^{Gen};#DeltaR" % refPtMin, 375, -1000, 500, 35, 0, 0.7)
    # else:
    #     h_dr_ptdiff = ROOT.TH2D("h_dr_ptdiff", "Stage1 jets, p_{T}^{Gen} > %g GeV;p_{T}^{L1} - p_{T}^{Gen};#DeltaR" % refPtMin, 189, -504, 252, 35, 0, 0.7)
    # tree.Draw("dr:ptDiff>>h_dr_ptdiff", eta_cut, "COLZ")
    # out_name = "ptDiff_deltaR_"
    # out_name += "Stage1intern_" if internJet else "Stage1Jets_"
    # out_name += "refMin%g" % refPtMin
    # out_name += append
    # out_name += ".pdf"
    # c.SaveAs(out_dir+"/"+out_name)

    # Draw pt (l1) Vs Delta pT
    # if internJet:
    #     h_pt_ptdiff = ROOT.TH2D("h_pt_ptdiff", "Intern jets, p_{T}^{Gen} > %g GeV;p_{T}^{L1} - p_{T}^{Gen};p_{T}^{L1}" % refPtMin, 375, -1000, 500, 125, 0, 500)
    # else:
    #     h_pt_ptdiff = ROOT.TH2D("h_pt_ptdiff", "Stage1 jets, p_{T}^{Gen} > %g GeV;p_{T}^{L1} - p_{T}^{Gen};p_{T}^{L1}" % refPtMin, 189, -504, 252, 63, 0, 252)
    # tree.Draw("pt:ptDiff>>h_pt_ptdiff", eta_cut, "COLZ")
    # out_name = "ptDiff_pt_"
    # out_name += "Stage1intern_" if internJet else "Stage1Jets_"
    # out_name += "refMin%g" % refPtMin
    # out_name += append
    # out_name += ".pdf"
    # c.SaveAs(out_dir+"/"+out_name)

    # Draw pt (gen) Vs Delta pT
    # if internJet:
    #     h_ptRef_ptdiff = ROOT.TH2D("h_ptRef_ptdiff", "Intern jets, p_{T}^{Gen} > %g GeV;p_{T}^{L1} - p_{T}^{Gen};p_{T}^{Gen}" % refPtMin, 375, -1000, 500, 125, 0, 500)
    # else:
    #     h_ptRef_ptdiff = ROOT.TH2D("h_ptRef_ptdiff", "Stage1 jets, p_{T}^{Gen} > %g GeV;p_{T}^{L1} - p_{T}^{Gen};p_{T}^{Gen}" % refPtMin, 189, -504, 252, 125, 0, 500)
    # tree.Draw("ptRef:ptDiff>>h_ptRef_ptdiff", eta_cut, "COLZ")
    # out_name = "ptDiff_ptRef_"
    # out_name += "Stage1intern_" if internJet else "Stage1Jets_"
    # out_name += "refMin%g" % refPtMin
    # out_name += append
    # out_name += ".pdf"
    # c.SaveAs(out_dir+"/"+out_name)

    # Draw deltaEta vs deltaPhi
    # c.SetLogz(0)
    # h_deta_dphi = ROOT.TH2D("h_deta_dphi", "", 70, -0.7, 0.7, 70, -0.7, 0.7)
    # if internJet:
    #     h_deta_dphi.SetTitle("Intern jets, p_{T}^{Gen} > %g GeV;#Delta#phi;#Delta#eta" % refPtMin)
    # else:
    #     h_deta_dphi.SetTitle("Stage1 jets, p_{T}^{Gen} > %g GeV;#Delta#phi;#Delta#eta" % refPtMin)
    # tree.Draw("deta:dphi>>h_deta_dphi", eta_cut,"COLZ")
    # out_name = "dEta_dPhi_"
    # out_name += "Stage1intern_" if internJet else "Stage1Jets_"
    # out_name += "refMin%g" % refPtMin
    # out_name += append
    # out_name += ".pdf"
    # c.SaveAs(out_dir+"/"+out_name)


def main(in_args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", help="input ROOT file with matched pairs from RunMatcher")
    parser.add_argument("--oDir", help="Directory to save plots. Default is $PWD.", default=".")
    args = parser.parse_args(args=in_args)
    print args
    make_plots(input_filename=args.pairs, out_dir=args.oDir)


if __name__ == "__main__":
    main()