import ROOT
import sys

"""
This script produces plots for showing off in notes/presentations, etc

Robin Aggleton
"""

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
    Plots response VS eta, response Vs dR, and dR
    """
    tree.Draw("1./rsp:TMath::Abs(deta-eta)>>rsp_eta(250,0,5,200,0,2","","COLZ")
    rsp_eta = ROOT.gROOT.FindObject("rsp_eta")
    rsp_eta.SetTitle(';|#eta^{Gen}|;E_{T}^{L1}/E_{T}^{Gen}')
    getDefCanvas().SaveAs("rsp_eta.pdf")

    tree.Draw("1./rsp:dr>>rsp_dr(45,0,0.9,300,0,2)","","COLZ")
    rsp_dr = ROOT.gROOT.FindObject("rsp_dr")
    rsp_dr.SetTitle(";%s;%s" % (dr_str,rsp_str))
    getDefCanvas().SaveAs("rsp_dr.pdf")

    dr = rsp_dr.ProjectionX("dr")
    dr.Sumw2()
    dr.Scale(1./dr.Integral())
    dr.SetTitle(";%s;A.U." % dr_str)
    dr.Draw("HISTE")
    getDefCanvas().SaveAs("dr.pdf")



if __name__ == "__main__":

    ROOT.gROOT.SetBatch(True)

    # Get input ROOT files
    inFile = ROOT.TFile(sys.argv[1])
    print sys.argv[1]
    # output_f = ROOT.TFile(sys.argv[2],"RECREATE")
    # print sys.argv[2]
    tree = getTree(inFile, "valid")

    # Turn these on an off as necessary
    plotResponseGeneral(tree)

