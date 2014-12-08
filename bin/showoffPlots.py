import ROOT
import sys
import numpy

"""
This script produces plots for showing off in notes/presentations, etc

Robin Aggleton
"""

ROOT.TH1.SetDefaultSumw2(True)

# etaBins = [ 0.0,0.348, 0.695, 1.044, 1.392, 1.74, 2.172, 3.0] #, 3.5, 4.0, 4.5, 5.001]
etaBins = [ 0.0,0.348, 0.695, 1.044, 1.392, 1.74, 2.172, 3.0, 3.5, 4.0, 4.5, 5.001]
ptBins_1 = [14,18,22,24]
ptBins_2 = numpy.arange(28,120,4)
ptBins = ptBins_1[:]
ptBins+=list(ptBins_2)

# Some common strings
# Yes globals bad, yada yada

rsp_str = "E_{T}^{L1}/E_{T}^{Gen}"
etaRef_str = "|#eta^{Gen}|"
etaL1_str = "|#eta^{L1}|"
dr_str = "#DeltaR(Gen jet - L1 jet)"


def getTree(inFile, treeName):
    """
    Get TTree from ROOT file
    """
    return inFile.Get(treeName)


def getDefCanvas():
    """
    Get default canvas c1, 'cos I'm lazy
    """
    return ROOT.gROOT.FindObject("c1")


def plotResponseGeneral(tree):
    """
    Plots response VS eta, response Vs dR, dR distr., response distr.
    Note that "response" is normally E_T(L1) /E_T(Gen), although in ROOT file is
    1/that...
    """
    c = ROOT.TCanvas()
    c.SetTicks()
    ROOT.gStyle.SetNumberContours(255);
    tree.Draw("1./rsp:TMath::Abs(deta-eta)>>rsp_eta(250,0,5,200,0,2","","COLZ")
    rsp_eta = ROOT.gROOT.FindObject("rsp_eta")
    rsp_eta.SetTitle(';|#eta^{Gen}|;E_{T}^{L1}/E_{T}^{Gen}')
    # Draw lines for eta bins
    lines = []
    for e in etaBins[1:]:
        l = ROOT.TLine(e, 0, e, 2)
        l.SetLineStyle(2)
        lines.append(l)
    [l.Draw("SAME") for l in lines]
    c.SaveAs("rsp_eta.pdf")

    tree.Draw("1./rsp:dr>>rsp_dr(100,0,0.9,100,0,2)","","COLZ")
    rsp_dr = ROOT.gROOT.FindObject("rsp_dr")
    rsp_dr.SetTitle(";%s;%s" % (dr_str,rsp_str))
    c.SaveAs("rsp_dr.pdf")

    dr = rsp_dr.ProjectionX("dr")
    dr.Sumw2()
    dr.Rebin(2)
    dr.Scale(1./dr.Integral())
    dr.SetTitle(";%s;A.U." % dr_str)
    dr.Draw("HISTE")
    c.SaveAs("dr.pdf")

    rsp = rsp_dr.ProjectionY("rsp")
    rsp.Sumw2()
    rsp.Scale(1./rsp.Integral())
    rsp.SetTitle(";%s;A.U" % rsp_str)
    rsp.Draw("HISTE")
    c.SaveAs("rsp.pdf")

    tree.Draw("1./rsp:rsp*pt>>rsp_pt(300,0,300,200,0,6)", "TMath::Abs(eta)<0.348 && TMath::Abs(eta)>0","COLZ")
    rsp_pt = ROOT.gROOT.FindObject("rsp_pt")
    rsp_pt.SetTitle(";E_{T}^{Gen};E_{T}^{L1}/E_{T}^{Gen}")
    pt_lines = []
    for p in ptBins:
        l = ROOT.TLine(p,0,p,6)
        l.SetLineStyle(2)
        pt_lines.append(l)
    [l.Draw("SAME") for l in pt_lines]
    c.SaveAs("rsp_pt.pdf")


def plot_ET(tree):
    """
    Plot comaprison of ET^L1 against ET^Gen
    """
    c = ROOT.TCanvas()
    c.SetTicks()
    tree.Draw("pt:rsp*pt>>pt_ref_l1(300,0,300,300,0,300)", "TMath::Abs(eta)<0.348 && TMath::Abs(eta)>0", "COLZ")
    pt_ref_l1 = ROOT.gROOT.FindObject("pt_ref_l1")
    pt_ref_l1.SetTitle(";E_{T}^{Gen};E_{T}^{L1}")
    pt_lines = []
    for p in ptBins:
        l = ROOT.TLine(p,0,p,300)
        l.SetLineStyle(2)
        pt_lines.append(l)
    [l.Draw("SAME") for l in pt_lines]
    c.SaveAs("pt_ref_l1.pdf")


def plot_response_eta_bins(tree):
    c = ROOT.TCanvas()
    c.SetTicks()
    for i, eta in enumerate(etaBins[0:-1]):
        etamin = eta
        etamax = etaBins[i+1]
        cutstr = "TMath::Abs(eta)<%g && TMath::Abs(eta)>%g" %(etamax, etamin)
        tree.Draw("1./rsp>>rsp_eta_%g_%g(50, 0, 2)" %(etamin, etamax), cutstr)
        rsp_eta = ROOT.gROOT.FindObject("rsp_eta_%g_%g" %(etamin, etamax))
        rsp_eta.SetTitle(";%.3f < \#eta_{gen}| < %.3f;Events" %(etamin, etamax))
        c.SaveAs("rsp_eta_%.3f_%.3f.pdf"%(etamin, etamax))


def compare_fits(tree):
    """
    Plot old vs new calibration curves
    """
    pass

if __name__ == "__main__":
    ROOT.gROOT.SetBatch(True)

    # Get input ROOT files
    inFilePairs = ROOT.TFile(sys.argv[1])
    print sys.argv[1]
    treePairs = getTree(inFilePairs, "valid")
    # inFileCalib = ROOT.TFile(sys.argv[2])
    # print sys.argv[2]
    # output_f = ROOT.TFile(sys.argv[2],"RECREATE")
    # print sys.argv[2]
    # treeCalib = getTree(inFileCalib, "valid")

    # Turn these on an off as necessary
    # plotResponseGeneral(treePairs)
    # plot_ET(treePairs)
    plot_response_eta_bins(treePairs)