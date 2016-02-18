import ROOT
from collections import namedtuple


ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(1)
ROOT.gStyle.SetOptFit(1111)
ROOT.TH1.SetDefaultSumw2(True)

f = ROOT.TFile("L1Ntuple_HF_JEC.root")
TR = f.Get("l1JetRecoTree/JetRecoTree")
T1 = f.Get("simCaloStage2Digis/Layer2SumTree")
T1.AddFriend(TR)

Plot = namedtuple('Plot', 'tree branchname cut color label')

def make_1D_plot(plots, title, nbins, xmin, xmax, logy, filename, mean_in_legend=False):
    """Quick way to plot several 1D hists on same canvas.

    Parameters
    ----------
    plots : list[Plot]
        PLot objects to plot.
    title : str
        Title of plot.
    nbins : int
        Number of bins.
    xmin : float
        x axis minimum
    xmax : float
        x axis maximum
    logy : bool
        Whether to make Y axis log
    filename : str
        Name of output file
    mean_in_legend : bool, optional
        Put mean of histogram in legend.
    """
    c = ROOT.TCanvas("c", "", 700, 600)
    c.SetTicks(1, 1)
    if logy:
        c.SetLogy(1)
    else:
        c.SetLogy(0)
    hists = []  # for object persistence
    hst = ROOT.THStack('hst', title)
    leg = ROOT.TLegend(0.5, 0.65, 0.88, 0.88)
    for i, plt in enumerate(plots):
        hname = "h_%s_%d" % (plt.branchname.replace('.', '-'), i)
        h = ROOT.TH1F(hname, title, nbins, xmin, xmax)
        plt.tree.Draw('%s>>%s' % (plt.branchname, hname), plt.cut)
        h.SetLineWidth(2)
        h.SetLineColor(plt.color)
        hst.Add(h)
        extra = ' (mean %.2f)' % h.GetMean() if mean_in_legend else ''
        leg.AddEntry(h, plt.label + extra)

    hst.Draw("NOSTACK HISTE")
    leg.Draw()
    c.SaveAs(filename)


# Plot multiplicities
plots = [
    Plot(tree=T1, branchname='nJetsInHTT', cut='', color=ROOT.kBlack, label='L1'),
    Plot(tree=TR, branchname='Sums.nJetsInHTT', cut='', color=ROOT.kRed, label='All PF jets'),
    Plot(tree=TR, branchname='Sums.nNoMuJetsInHTT', cut='', color=ROOT.kBlue, label='PF jets with muon mult. == 0'),
    Plot(tree=TR, branchname='Sums.nCleanJetsInHTT', cut='', color=ROOT.kGreen + 2, label='PF jets passing JetID'),
]

make_1D_plot(plots, 'Run 260627, SingleMu, all jets have corrected p_{T} > 30 GeV, |#eta| < 3;nJets;', 10, 0, 10, False, "nJetsHTT.pdf", mean_in_legend=True)

# Plot multiplicity correlations
c = ROOT.TCanvas("c", "", 700, 600)
c.SetTicks(1, 1)
c.SetLogz()
nJetsMax = 10
h2d_mult_l1_all = ROOT.TH2I("h2d_mult_l1_all", "All PF jets;NJets L1;NJets PF", nJetsMax, 0, nJetsMax, nJetsMax, 0, nJetsMax)
h2d_mult_l1_noMu = ROOT.TH2I("h2d_mult_l1_noMu", "Only muon multiplicty == 0;NJets L1;NJets PF", nJetsMax, 0, nJetsMax, nJetsMax, 0, nJetsMax)
h2d_mult_l1_clean = ROOT.TH2I("h2d_mult_l1_clean", "With all cleaning cuts + muon multiplicty == 0;NJets L1;NJets PF", nJetsMax, 0, nJetsMax, nJetsMax, 0, nJetsMax)
c.SetLogz()
line = ROOT.TLine(0, 0, nJetsMax, nJetsMax)
T1.Draw("JetRecoTree.Sums.nJetsInHTT:nJetsInHTT>>h2d_mult_l1_all", "", "COLZ")
line.Draw()
c.SaveAs("h2d_mult_l1_all.pdf")
T1.Draw("JetRecoTree.Sums.nNoMuJetsInHTT:nJetsInHTT>>h2d_mult_l1_noMu", "", "COLZ")
line.Draw()
c.SaveAs("h2d_mult_l1_noMu.pdf")
T1.Draw("JetRecoTree.Sums.nCleanJetsInHTT:nJetsInHTT>>h2d_mult_l1_clean", "", "COLZ")
line.Draw()
c.SaveAs("h2d_mult_l1_clean.pdf")

# Plot kinematics
plots = [
    Plot(tree=T1, branchname='httJetEt', cut='', color=ROOT.kBlack, label='L1'),
    Plot(tree=TR, branchname='Sums.httJetEt', cut='', color=ROOT.kRed, label='All PF jets'),
    Plot(tree=TR, branchname='Sums.httJetEt', cut='Sums.httJetMuMult0', color=ROOT.kBlue, label='PF jets with muon mult. == 0'),
    Plot(tree=TR, branchname='Sums.httJetEt', cut='Sums.httJetClean', color=ROOT.kGreen + 2, label='PF jets passing JetID')
]

make_1D_plot(plots, 'Run 260627, SingleMu, all jets have corrected p_{T} > 30 GeV, |#eta| < 3;p_{T} [GeV];', 50, 0, 100, False, 'httJetEt.pdf')

plots = [
    Plot(tree=T1, branchname='httJetEta', cut='', color=ROOT.kBlack, label='L1'),
    Plot(tree=TR, branchname='Sums.httJetEta', cut='', color=ROOT.kRed, label='All PF jets'),
    Plot(tree=TR, branchname='Sums.httJetEta', cut='Sums.httJetMuMult0', color=ROOT.kBlue, label='PF jets with muon mult. == 0'),
    Plot(tree=TR, branchname='Sums.httJetEta', cut='Sums.httJetClean', color=ROOT.kGreen + 2, label='PF jets passing JetID')
]

make_1D_plot(plots, 'Run 260627, SingleMu, all jets have corrected p_{T} > 30 GeV, |#eta| < 3;#eta;', 64, -3.2, 3.2, False, 'httJetEta.pdf')

plots = [
    Plot(tree=T1, branchname='httJetPhi', cut='', color=ROOT.kBlack, label='L1'),
    Plot(tree=TR, branchname='Sums.httJetPhi', cut='', color=ROOT.kRed, label='All PF jets'),
    Plot(tree=TR, branchname='Sums.httJetPhi', cut='Sums.httJetMuMult0', color=ROOT.kBlue, label='PF jets with muon mult. == 0'),
    Plot(tree=TR, branchname='Sums.httJetPhi', cut='Sums.httJetClean', color=ROOT.kGreen + 2, label='PF jets passing JetID')
]

make_1D_plot(plots, 'Run 260627, SingleMu, all jets have corrected p_{T} > 30 GeV, |#eta| < 3;#Phi;', 64, -3.2, 3.2, False, 'httJetPhi.pdf')

# Plot et correlation
c = ROOT.TCanvas("c", "", 700, 600)
c.SetTicks(1, 1)
# c.SetLogz()
nbins_et = 50
et_max = 100
h2d_et_l1_all = ROOT.TH2I("h2d_et_l1_all", "All PF jets;L1 p_{T} [GeV];PF p_{T} [GeV]", nbins_et, 0, et_max, nbins_et, 0, et_max)
h2d_et_l1_noMu = ROOT.TH2I("h2d_et_l1_noMu", "Only muon multiplicty == 0;L1 p_{T} [GeV];PF p_{T} [GeV]", nbins_et, 0, et_max, nbins_et, 0, et_max)
h2d_et_l1_clean = ROOT.TH2I("h2d_et_l1_clean", "With all cleaning cuts + muon multiplicty == 0;L1 p_{T} [GeV];PF p_{T} [GeV]", nbins_et, 0, et_max, nbins_et, 0, et_max)
line = ROOT.TLine(0, 0, et_max, et_max)
T1.Draw("JetRecoTree.Sums.httJetEt:httJetEt>>h2d_et_l1_all", "", "COLZ")
line.Draw()
c.SaveAs("h2d_et_l1_all.pdf")
T1.Draw("JetRecoTree.Sums.httJetEt:httJetEt>>h2d_et_l1_noMu", "JetRecoTree.Sums.httJetMuMult0", "COLZ")
line.Draw()
c.SaveAs("h2d_et_l1_noMu.pdf")
T1.Draw("JetRecoTree.Sums.httJetEt:httJetEt>>h2d_et_l1_clean", "JetRecoTree.Sums.httJetClean", "COLZ")
line.Draw()
c.SaveAs("h2d_et_l1_clean.pdf")

# Plot eta correlation
c = ROOT.TCanvas("c", "", 700, 600)
c.SetTicks(1, 1)
# c.SetLogz()
nbins_eta = 64
eta_min, eta_max = -3.2, 3.2
h2d_eta_l1_all = ROOT.TH2I("h2d_eta_l1_all", "All PF jets;L1 #eta;PF #eta", nbins_eta, eta_min, eta_max, nbins_eta, eta_min, eta_max)
h2d_eta_l1_noMu = ROOT.TH2I("h2d_eta_l1_noMu", "Only muon multiplicty == 0;L1 #eta;PF #eta", nbins_eta, eta_min, eta_max, nbins_eta, eta_min, eta_max)
h2d_eta_l1_clean = ROOT.TH2I("h2d_eta_l1_clean", "With all cleaning cuts + muon multiplicty == 0;L1 #eta;PF #eta", nbins_eta, eta_min, eta_max, nbins_eta, eta_min, eta_max)
T1.Draw("JetRecoTree.Sums.httJetEta:httJetEta>>h2d_eta_l1_all", "", "COLZ")
c.SaveAs("h2d_eta_l1_all.pdf")
T1.Draw("JetRecoTree.Sums.httJetEta:httJetEta>>h2d_eta_l1_noMu", "JetRecoTree.Sums.httJetMuMult0", "COLZ")
c.SaveAs("h2d_eta_l1_noMu.pdf")
T1.Draw("JetRecoTree.Sums.httJetEta:httJetEta>>h2d_eta_l1_clean", "JetRecoTree.Sums.httJetClean", "COLZ")
c.SaveAs("h2d_eta_l1_clean.pdf")

# Plot phi correlation
c = ROOT.TCanvas("c", "", 700, 600)
c.SetTicks(1, 1)
# c.SetLogz()
nbins_phi = 64
phi_min, phi_max = -3.2, 3.2
h2d_phi_l1_all = ROOT.TH2I("h2d_phi_l1_all", "All PF jets;L1 #phi;PF #phi", nbins_phi, phi_min, phi_max, nbins_phi, phi_min, phi_max)
h2d_phi_l1_noMu = ROOT.TH2I("h2d_phi_l1_noMu", "Only muon multiplicty == 0;L1 #phi;PF #phi", nbins_phi, phi_min, phi_max, nbins_phi, phi_min, phi_max)
h2d_phi_l1_clean = ROOT.TH2I("h2d_phi_l1_clean", "With all cleaning cuts + muon multiplicty == 0;L1 #phi;PF #phi", nbins_phi, phi_min, phi_max, nbins_phi, phi_min, phi_max)
T1.Draw("JetRecoTree.Sums.httJetPhi:httJetPhi>>h2d_phi_l1_all", "", "COLZ")
c.SaveAs("h2d_phi_l1_all.pdf")
T1.Draw("JetRecoTree.Sums.httJetPhi:httJetPhi>>h2d_phi_l1_noMu", "JetRecoTree.Sums.httJetMuMult0", "COLZ")
c.SaveAs("h2d_phi_l1_noMu.pdf")
T1.Draw("JetRecoTree.Sums.httJetPhi:httJetPhi>>h2d_phi_l1_clean", "JetRecoTree.Sums.httJetClean", "COLZ")
c.SaveAs("h2d_phi_l1_clean.pdf")
