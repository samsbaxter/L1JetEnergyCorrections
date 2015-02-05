import ROOT
import sys
import numpy

"""
This script produces plots for showing off in notes/presentations, etc

Robin Aggleton
"""

ROOT.TH1.SetDefaultSumw2(True)
ROOT.gStyle.SetOptFit(0111)

# etaBins = [ 0.0,0.348, 0.695, 1.044, 1.392, 1.74, 2.172, 3.0] #, 3.5, 4.0, 4.5, 5.001]
etaBins = [ 0.0,0.348, 0.695, 1.044, 1.392, 1.74, 2.172, 3.0, 3.5, 4.0, 4.5, 5.001]
ptBins_1 = [14,18,22,24]
ptBins_2 = numpy.arange(28,120,4)
ptBins = ptBins_1[:]
ptBins+=list(ptBins_2)
ptBins = list(numpy.arange(14, 254, 4))


# Some common strings
# Yes globals bad, yada yada

rsp_str = "E_{T}^{L1}/E_{T}^{Gen}"
etaRef_str = "|#eta^{Gen}|"
etaL1_str = "|#eta^{L1}|"
dr_str = "#DeltaR(Gen jet - L1 jet)"
etL1_str = "E_{T}^{L1}"
etGen_str = "E_{T}^{Gen}"

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
    Plot comparison of ET^L1 against ET^Gen
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
    """
    Plot response for each eta bin
    """
    c = ROOT.TCanvas()
    c.SetTicks()
    for i, eta in enumerate(etaBins[0:-1]):
        etamin = eta
        etamax = etaBins[i+1]
        cutstr = "TMath::Abs(eta)<%g && TMath::Abs(eta)>%g" %(etamax, etamin)
        tree.Draw("1./rsp>>rsp_eta_%g_%g(50, 0, 2)" %(etamin, etamax), cutstr, "HISTE")
        rsp_eta = ROOT.gROOT.FindObject("rsp_eta_%g_%g" %(etamin, etamax))
        rsp_eta.SetTitle("%.3f < \#eta_{gen}| < %.3f;E_{T}^{L1}/E_{T}^{Gen};Events" %(etamin, etamax))
        c.SaveAs("rsp_eta_%.3f_%.3f.pdf"%(etamin, etamax))


def plot_example_et_bin_response(file, etamin, etamax, ptmin, ptmax):
    """
    Plot example ETL1 for ETGen bin, and corresponding resp with fit
    """
    c = ROOT.TCanvas()
    c.SetTicks()
    print "eta_%s_%s/Histograms/L1_pt_genpt_%s_%s" %(etamin, etamax, ptmin, ptmax)
    h_ET = file.Get("eta_%s_%s/Histograms/L1_pt_genpt_%s_%s" %(etamin, etamax, ptmin, ptmax)).Clone()
    h_ET.Rebin(2)
    h_ET.SetTitle("%s < \#eta_{gen}| < %s, %s < E_{T}^{Gen} < %s GeV;E_{T}^{L1} [GeV];Events" % (etamin, etamax, ptmin, ptmax))
    h_ET.Draw("HISTE")
    c.SaveAs("L1_pt_genpt_%s_%s_eta_%s_%s.pdf" %(ptmin, ptmax, etamin, etamax))

    h_rsp = file.Get("eta_%s_%s/Histograms/Rsp_genpt_%s_%s" %(etamin, etamax, ptmin, ptmax)).Clone()
    h_rsp.SetTitle("Response for %s < \#eta_{gen}| < %s, %s < E_{T}^{Gen} < %s GeV;E_{T}^{L1}/E_{T}^{Gen};Events" %(etamin, etamax, ptmin, ptmax))
    h_rsp.Draw()
    c.SaveAs("rsp_%s_%s_eta_%s_%s.pdf" % (ptmin, ptmax, etamin, etamax))

    g_calib = file.Get("l1corr_eta_%s_%s" %(etamin, etamax)).Clone()
    g_calib.SetTitle(";<E_{T}^{L1}> [GeV]; 1/<E_{T}^{L1}/E_{T}^{Gen}>")
    g_calib.Draw("APL")
    c.SaveAs("calib_%s_%s.pdf" %(etamin, etamax))


def closure_et(tree, etamin, etamax):
    """
    Do closure test as fn of L1 ET
    """
    c = ROOT.TCanvas()
    c.SetTicks()
    fitfcn = ROOT.TF1("fitfcn", "[0]+[1]/(pow(log10((x)),2)+[2])+[3]*exp(-[4]*(log10((x))-[5])*(log10((x))-[5]))", 20, 500)
    # fitfcn.SetParameter(0, -0.1234)
    # fitfcn.SetParameter(1, 20.75)
    # fitfcn.SetParameter(2, 6.708)
    # fitfcn.SetParameter(3, -0.7638)
    # fitfcn.SetParameter(4, 0.01114)
    # fitfcn.SetParameter(5, -5.511)

    fitfcn.SetParameter(0, 0.8357)
    fitfcn.SetParameter(1, -0.01692)
    fitfcn.SetParameter(2, -0.9205)
    fitfcn.SetParameter(3, -15.55)
    fitfcn.SetParameter(4, 0.01014)
    fitfcn.SetParameter(5, -24.13)

    corr_pt = str(fitfcn.GetExpFormula("p"))
    corr_pt = corr_pt.replace("(x)","(pt)")
    corr_rsp = "(1./rsp)*"+corr_pt
    corr_pt = "pt*"+corr_pt
    print corr_pt
    print corr_rsp

    cutstr = "TMath::Abs(eta)>%g && TMath::Abs(eta)<%g" % (etamin, etamax)

    gr_uncorr = ROOT.TGraphErrors()
    gr_corr = ROOT.TGraphErrors()
    grc = 0

    for i, pt in enumerate(ptBins[0:-1]):
        ptmin = pt
        ptmax = ptBins[i+1]
        print "Doing bin", ptmin, "-", ptmax

        ptcut = "(pt*rsp>%.3f) && (pt*rsp < %.3f)" %(ptmin, ptmax)
        pt_eta_cut = cutstr+" && " + ptcut
        print pt_eta_cut

        tree.Draw("pt>>h_uncorr_et_%f_%f(400,0,200)" %(ptmin, ptmax),pt_eta_cut)
        h_uncorr_et = ROOT.gROOT.FindObject("h_uncorr_et_%f_%f" %(ptmin, ptmax))

        print h_uncorr_et.Integral()

        tree.Draw(corr_pt+">>h_corr_et_%f_%f(400,0,200)" %(ptmin, ptmax),pt_eta_cut)
        h_corr_et = ROOT.gROOT.FindObject("h_corr_et_%f_%f" %(ptmin, ptmax))

        tree.Draw("1./rsp>>h_uncorr_rsp_%f_%f(500, 0, 5)" %(ptmin, ptmax), pt_eta_cut)
        h_uncorr_rsp = ROOT.gROOT.FindObject("h_uncorr_rsp_%f_%f" %(ptmin, ptmax))

        tree.Draw(corr_rsp+">>h_corr_rsp_%f_%f(500, 0, 5)" %(ptmin, ptmax), pt_eta_cut )
        h_corr_rsp = ROOT.gROOT.FindObject("h_corr_rsp_%f_%f" %(ptmin, ptmax))

        if h_uncorr_et.GetEntries() > 0:
            print h_uncorr_et.GetMean(), h_uncorr_rsp.GetMean()
            gr_uncorr.SetPoint(grc, h_uncorr_et.GetMean(), h_uncorr_rsp.GetMean())
            gr_uncorr.SetPointError(grc, h_uncorr_et.GetMeanError(), h_uncorr_rsp.GetMeanError())
        if h_corr_et.GetEntries() > 0:
            print h_corr_et.GetMean(), h_corr_rsp.GetMean()
            gr_corr.SetPoint(grc, h_corr_et.GetMean(), h_corr_rsp.GetMean())
            gr_corr.SetPointError(grc, h_corr_et.GetMeanError(), h_corr_rsp.GetMeanError())

        grc += 1

    gr_uncorr.SetMarkerStyle(21)
    gr_uncorr.SetMarkerColor(ROOT.kBlue)

    gr_corr.SetMarkerStyle(22)
    gr_corr.SetMarkerColor(ROOT.kRed)

    gr_uncorr.GetXaxis().SetTitle(etL1_str)
    gr_uncorr.GetYaxis().SetTitle(rsp_str)
    gr_corr.GetXaxis().SetTitle(etL1_str)
    gr_corr.GetYaxis().SetTitle(rsp_str)

    mg = ROOT.TMultiGraph()
    mg.Add(gr_uncorr)
    mg.Add(gr_corr)
    mg.Draw("AP")

    leg = ROOT.TLegend(0.6, 0.67, 0.87, 0.87)
    leg.AddEntry(gr_uncorr, "Uncorrected L1" , "p")
    leg.AddEntry(gr_corr, "Corrected L1" , "p")
    leg.SetFillColor(0)
    leg.SetFillStyle(0)
    leg.SetLineColor(0)
    leg.SetLineStyle(0)
    leg.SetLineWidth(2)
    leg.Draw("SAME")

    label = ROOT.TPaveText(0.1,0.91,0.4,0.96, "NDCNB")
    label.SetFillStyle(0)
    label.SetFillColor(0)
    label.SetLineColor(0)
    label.SetLineWidth(0)
    label.SetLineStyle(0)
    label.AddText("%.3f < |#eta^{Gen}| < %.3f" % (etamin, etamax))
    label.Draw("SAME")

    xmin = mg.GetHistogram().GetXaxis().GetXmin()  # bloody ridiculous
    xmax = mg.GetHistogram().GetXaxis().GetXmax()
    line = ROOT.TLine(xmin, 1, xmax, 1)
    line.SetLineStyle(2)
    line.SetLineWidth(2)
    line.Draw("SAME")

    c.SaveAs("closuretest_%.3f_%.3f.pdf"%(etamin, etamax))


def compare_fits(tree):
    """
    Plot old vs new calibration curves
    """
    pass

if __name__ == "__main__":
    ROOT.gROOT.SetBatch(True)

    # Get input ROOT files
    inFilePairs = ROOT.TFile(sys.argv[1], "READ")
    print sys.argv[1]
    treePairs = getTree(inFilePairs, "valid")
    inFileCalib = ROOT.TFile(sys.argv[2], "READ")
    print sys.argv[2]

    # output_f = ROOT.TFile(sys.argv[2],"RECREATE")
    # print sys.argv[2]
    # treeCalib = getTree(inFileCalib, "valid")

    # Turn these on an off as necessary
    # plotResponseGeneral(treePairs)
    # plot_ET(treePairs)
    # plot_response_eta_bins(treePairs)
    # plot_example_et_bin_response(inFileCalib, '0', '0.348', '82', '86')
    plot_example_et_bin_response(inFileCalib, '0.348', '0.695', '82', '86')
    # plot_example_et_bin_response(inFileCalib, '3', '3.5', '82', '86')
    # for i,eta in enumerate(etaBins[0:-1]):
    closure_et(treePairs, etaBins[1], etaBins[2])
    # closure_et(treePairs, eta, etaBins[i+1])