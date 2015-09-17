"""
Little script to showoff plots that may showup PU regions Vs signal regions
"""

import argparse
import ROOT
import os
import sys
from itertools import izip, product, chain
import L1Trigger.L1JetEnergyCorrections.analysis.common_utils as cu
import L1Trigger.L1JetEnergyCorrections.analysis.binning as binning


ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(1)
ROOT.TH1.SetDefaultSumw2()
# ROOT.gStyle.SetOptTitle(0);
ROOT.gStyle.SetOptStat(0);
ROOT.gStyle.SetPalette(55)


def plot_deltaR(input_file, out_dir, refPtMin=0, internJet=False, append=""):
    """Plot deltaR distributions for various pT, eta bins"""

    tree = cu.get_from_file(input_file, "valid")

    canv = ROOT.TCanvas("canv", "", 800, 600)
    canv.SetLogz()

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
                canv.SaveAs(out_dir+"/"+out_name)

                h_dr_pt.SetLineColor(colours[i])
                mg.Add(h_dr_pt)
                leg.AddEntry(h_dr_pt, "%g < %s < %g" % (pt_min, ptVar, pt_max), "L")

            mg.Draw("NOSTACK HISTE")
            mg.GetHistogram().SetTitle("%s < |#eta^{L1}| < %g;#Delta R(L1, GenJet);" % (eta_min, eta_max))
            leg.Draw()
            out_name = mg.GetName()+".pdf"
            canv.SaveAs(out_dir+"/"+out_name)


    # DeltaR vs response for given pT bin

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
    # canv.SaveAs(out_dir+"/"+out_name)

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
    # canv.SaveAs(out_dir+"/"+out_name)

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
    # canv.SaveAs(out_dir+"/"+out_name)

    # Draw deltaEta vs deltaPhi
    # canv.SetLogz(0)
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
    # canv.SaveAs(out_dir+"/"+out_name)


def plot_response_nvtx(input_file, out_dir, nvtx_var="numPUVertices",
              eta_min=0, eta_max=5, pt_min=0, pt_max=250, pt_var="pt", append=""):
    """Plot response as a function of number of vertices

    nvtx_var is the variable that describes number of vertices, is normally
    either numPUVertices or trueNumInteractions.

    eta_min/max, pt_min/max are for cuts on TMath::Abs(eta) and pt.
    pt_var is the variable name for the pt cut, so you can change the variable to cut on
    """
    tree = cu.get_from_file(input_file, "valid")

    canv = ROOT.TCanvas("canv", "", 800, 600)
    canv.SetTicks(1, 1)

    # check nvtx_var in tree
    if not hasattr(tree, nvtx_var):
        raise RuntimeError("%s is not a valid branch name" % nvtx_var)

    # cuts
    eta_cut = "%f < TMath::Abs(eta) && TMath::Abs(eta) < %f" % (eta_min, eta_max)
    pt_cut = "%f < %s && %s < %f" % (pt_min, pt_var, pt_var, pt_max)
    cuts = [eta_cut, pt_cut]
    total_cut = " && ".join(cuts)
    print total_cut

    # simple 2D plot of response vs nVtx
    hname = "h_nvtx_rsp_eta_%g_%g_pt_%g_%g" % (eta_min, eta_max, pt_min, pt_max)
    h_nvtx_rsp = ROOT.TH2D(hname,
                        "%g < |#eta| < %g, %g < %s < %g;%s;response ( = L1/Ref)" % (eta_min, eta_max, pt_min, pt_var, pt_max, nvtx_var),
                        40, 0, 40, 60, 0, 3)
    tree.Draw("rsp:%s>>%s" % (nvtx_var, hname), total_cut, "COLZ")

    # now permutate over log/norm
    for norm, log in product([True, False], [True, False]):
        canv.Clear()
        append_new = append
        if log:
            canv.SetLogz(1)
            append_new += "_log"
        else:
            canv.SetLogz(0)

        if norm:
            append_new += "_norm"
            hnew = cu.norm_vertical_bins(h_nvtx_rsp)
            hnew.Draw("COLZ")
        else:
            h_nvtx_rsp.Draw("COLZ")

        canv.SaveAs(out_dir+"/%s%s.pdf" % (hname, append_new))


def plot_response_nvtx_binned(input_file, out_dir, no_pu_file, nvtx_var="numPUVertices",
                              eta_min=0, eta_max=5, pt_min=0, pt_max=250, pt_var="pt", append=""):
    """Make histogram of response for various bins of nVtx

    no_pu_file is optional TFile for 0PU sample.

    eta_min/max, pt_min/max are for cuts on TMath::Abs(eta) and pt.

    pt_var is the variable name for the pt cut, so you can change the variable to cut on.

    nvtx_var is the variable that describes number of vertices, is normally
    either numPUVertices or trueNumInteractions.

    """

    tree = cu.get_from_file(input_file, "valid")
    tree_no_pu = cu.get_from_file(no_pu_file, "valid") if no_pu_file else None

    canv = ROOT.TCanvas("canv", "", 800, 600)
    canv.SetTicks(1, 1)

    # check nvtx_var in tree
    if not hasattr(tree, nvtx_var):
        raise RuntimeError("%s is not a valid branch name" % nvtx_var)

    # cuts
    eta_cut = "%f < TMath::Abs(eta) && TMath::Abs(eta) < %f" % (eta_min, eta_max)
    pt_cut = "%f < %s && %s < %f" % (pt_min, pt_var, pt_var, pt_max)
    cuts = [eta_cut, pt_cut]

    stack = ROOT.THStack("st", "")
    nbins, rsp_min, rsp_max = 40, 0, 2
    lw = 2

    leg = ROOT.TLegend(0.56, 0.6, 0.87, 0.87)

    # make hist if 0PU sample available
    if no_pu_file:
        hname = "h_rsp_eta_%g_%g_%s_%g_%g_no_pu" % (eta_min, eta_max, pt_var, pt_min, pt_max)
        h = ROOT.TH1D(hname,
                      "%g < |#eta| < %g, %g < %s < %g;response (=L1/ref);p.d.f." % (eta_min, eta_max, pt_min, pt_var, pt_max),
                      nbins, rsp_min, rsp_max)
        total_cut = " && ".join(cuts)
        print total_cut
        tree_no_pu.Draw("rsp>>%s" % hname, total_cut)
        h.Scale(1. / h.Integral())
        h.SetLineColor(ROOT.kBlack)
        h.SetLineWidth(lw)
        h.SetMarkerColor(ROOT.kBlack)
        leg.AddEntry(h, "nVtx: 0 (0PU sample)", "L")
        stack.Add(h)

    # make hist for each nVtx bin
    nvtx_bins = ([0, 10], [15, 25], [30, 40])
    colours = [ROOT.kRed, ROOT.kGreen+2, ROOT.kBlue]
    for i, (nvtx_min, nvtx_max) in enumerate(nvtx_bins):
        hname = "h_rsp_eta_%g_%g_%s_%g_%g_nvtx_%g_%g" % (eta_min, eta_max, pt_var, pt_min, pt_max, nvtx_min, nvtx_max)
        h = ROOT.TH1D(hname,
                      "%g < |#eta| < %g, %g < %s < %g;response (=L1/ref);p.d.f." % (eta_min, eta_max, pt_min, pt_var, pt_max),
                      nbins, rsp_min, rsp_max)
        nvtx_cut = "%f < %s && %s < %f" % (nvtx_min, nvtx_var, nvtx_var, nvtx_max)
        total_cut = " && ".join(chain(cuts, [nvtx_cut]))
        print total_cut
        tree.Draw("rsp>>%s" % hname, total_cut)
        h.Scale(1. / h.Integral())
        h.SetLineColor(colours[i])
        h.SetLineWidth(lw)
        h.SetMarkerColor(colours[i])
        leg.AddEntry(h, "nVtx: %g - %g" % (nvtx_min, nvtx_max), "L")
        stack.Add(h)

    canv.Clear()
    stack.Draw("NOSTACK HISTE")
    stack.GetHistogram().SetTitle("%g < |#eta| < %g, %g < %s < %g;response (=L1/ref);p.d.f." % (eta_min, eta_max, pt_min, pt_var, pt_max))
    stack.GetHistogram().GetYaxis().SetTitleOffset(1.1)
    leg.Draw()
    canv.SaveAs(out_dir+"/h_rsp_eta_%g_%g_%s_%g_%g%s.pdf" % (eta_min, eta_max, pt_var, pt_min, pt_max, append))


def pu_investigate(in_args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", help="input ROOT file with matched pairs from RunMatcher")
    parser.add_argument("--oDir", help="Directory to save plots. Default is $PWD.", default=".")
    parser.add_argument("--noPU", help="Input ROOT file with 0 PU.", default=None)
    args = parser.parse_args(args=in_args)
    print args

    cu.check_dir_exists_create(args.oDir)

    input_file = cu.open_root_file(args.pairs)
    no_pu_file = cu.open_root_file(args.noPU) if args.noPU else None

    # plot_deltaR(input_file=args.pairs, out_dir=args.oDir)

    # central, forward, for select pt bins
    for pt_min, pt_max in ([0, 250], [0, 50], [75, 125]):
        plot_response_nvtx(input_file=input_file, out_dir=args.oDir,
                    nvtx_var="numPUVertices", eta_min=0, eta_max=3,
                    pt_min=pt_min, pt_max=pt_max, append="")
        plot_response_nvtx(input_file=input_file, out_dir=args.oDir,
                    nvtx_var="numPUVertices", eta_min=3, eta_max=5,
                    pt_min=pt_min, pt_max=pt_max, append="")

        plot_response_nvtx_binned(input_file=input_file, no_pu_file=no_pu_file,
                                out_dir=args.oDir,
                                nvtx_var="numPUVertices", eta_min=0, eta_max=3,
                                pt_min=pt_min, pt_max=pt_max, append="")
        plot_response_nvtx_binned(input_file=input_file, no_pu_file=no_pu_file,
                                out_dir=args.oDir,
                                nvtx_var="numPUVertices", eta_min=3, eta_max=5,
                                pt_min=pt_min, pt_max=pt_max, append="")

    # Individual eta bins
    # for eta_min, eta_max in zip(binning.eta_bins[:-1], binning.eta_bins[1:]):
    #     print eta_min, eta_max
    #     plot_response_nvtx(input_file=input_file, out_dir=args.oDir, nvtx_var="numPUVertices",
    #         eta_min=eta_min, eta_max=eta_max, pt_min=0, pt_max=250, append="")


    input_file.Close()


if __name__ == "__main__":
    pu_investigate()