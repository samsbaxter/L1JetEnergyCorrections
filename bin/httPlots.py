#!/usr/bin/env python

"""
Produce plots for HTT studies.
"""

import ROOT
import os
import binning
import common_utils as cu
from itertools import product
import uuid  # for unique object names that we don't actually care about


ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(1)
ROOT.gStyle.SetOptFit(1111)
ROOT.TH1.SetDefaultSumw2(True)
ROOT.gStyle.SetPalette(ROOT.kViridis)
# ROOT.gStyle.SetPalette(55)
# ROOT.gErrorIgnoreLevel = ROOT.kWarning # turn off the printing output

# INPUT = '/hdfs/L1JEC/L1JetEnergyCorrections/Stage2_HF_QCDSpring15_20Feb_3bf1b93_noL1JEC_PFJets_V7PFJEC/pairs/pairs_QCDFlatSpring15BX25PU10to30HCALFix_MP_ak4_ref10to5000_l130to5000_dr0p4_httL1Jets_allGenJets_MHT.root'
# OUTPUT = '/users/ra12451/L1JEC/CMSSW_8_0_0_pre6/src/L1Trigger/L1JetEnergyCorrections/Stage2_HF_QCDSpring15_20Feb_3bf1b93_noL1JEC_PFJets_V7PFJEC/httStudies'
# TITLE = 'Spring15 MC, no L1JEC'
# TITLE = 'Spring15 MC, no L1JEC'

INPUT = '/hdfs/user/ra12451/L1JEC/CMSSW_8_0_0_pre5/L1JetEnergyCorrections/Stage2_HF_QCDFlatSpring15BX25HCALFix_16Feb_80X_mcRun2_asymptotic_v1_2779cb0_JEC/pairs/pairs_QCDFlatSpring15BX25PU10to30HCALFix_MP_ak4_ref10to5000_l130to5000_dr0p4_httL1Jets_allGenJets_MHT.root'
OUTPUT = '/users/ra12451/L1JEC/CMSSW_8_0_0_pre6/src/L1Trigger/L1JetEnergyCorrections/Stage2_HF_QCDFlatSpring15BX25HCALFix_16Feb_80X_mcRun2_asymptotic_v1_2779cb0_JEC/httStudies'
TITLE = 'Spring15 MC, with L1JEC'

"""
# Some common strings
# For DATA
PT_L1_STR = 'p_{T}^{L1} [GeV]'
PT_REF_STR = 'p_{T}^{PF} [GeV]'
RSP_STR = 'Response'
HTT_L1_STR = 'HTT (L1) [GeV]'
HTT_REF_STR = 'HTT (RECO) [GeV]'
HTT_RATIO_STR = 'HTT (L1) / HTT (RECO)'
HTT_DIFF_STR = 'HTT (L1) - HTT (RECO)'
DR_STR = '#DeltaR(L1, PF)'
DETA_STR = '#Delta#eta(L1, PF)'
DPHI_STR = '#Delta#phi(L1, PF)'
NVTX_STR = "# vtx"
NUM_L1_STR = "# L1 jets"
NUM_REF_STR = "# PF jets"
MHT_L1_STR = "MHT (L1) [GeV]"
MHT_REF_STR = "MHT (RECO) [GeV]"
MHT_PHI_L1_STR = "MHT #phi (L1)"
MHT_PHI_REF_STR = "MHT #phi (RECO)"
MHT_RATIO_STR = 'MHT (L1) / MHT (RECO)'
MHT_DIFF_STR = 'MHT (L1) - MHT (RECO)'

# TITLE FOR ALL PLOTS
TITLE = 'Run260627 SingleMu with L1JEC'
"""

# Some common strings
# For MC
PT_L1_STR = 'p_{T}^{L1} [GeV]'
PT_REF_STR = 'p_{T}^{GenJet} [GeV]'
RSP_STR = 'Response'
HTT_L1_STR = 'HTT (L1) [GeV]'
HTT_REF_STR = 'HTT (GEN) [GeV]'
HTT_RATIO_STR = 'HTT (L1) / HTT (GEN)'
HTT_DIFF_STR = 'HTT (L1) - HTT (GEN)'
DR_STR = '#DeltaR(L1, PF)'
DETA_STR = '#Delta#eta(L1, GenGet)'
DPHI_STR = '#Delta#phi(L1, GenJet)'
NVTX_STR = "# vtx"
NUM_L1_STR = "# L1 jets"
NUM_REF_STR = "# GenJets"
MHT_L1_STR = "MHT (L1) [GeV]"
MHT_REF_STR = "MHT (GEN) [GeV]"
MHT_PHI_L1_STR = "MHT #phi (L1)"
MHT_PHI_REF_STR = "MHT #phi (GEN)"
MHT_RATIO_STR = 'MHT (L1) / MHT (GEN)'
MHT_DIFF_STR = 'MHT (L1) - MHT (GEN)'

# AXIS LIMITS
NB_HTT, HTT_MIN, HTT_MAX = 200, 0, 600

NB_RSP, RSP_MIN, RSP_MAX = 50, 0.5, 2.5

NB_DR, DR_MIN, DR_MAX = 40, 0, 0.4

NB_PT, PT_MIN, PT_MAX = 40, 0, 400

NB_HTT_RATIO, HTT_RATIO_MIN, HTT_RATIO_MAX = 200, 0, 5

NB_HTT_DIFF, HTT_DIFF_MIN, HTT_DIFF_MAX = 200, -200, 200

NB_NJET, NJET_MIN, NJET_MAX = 10, 0, 10

NB_MHT, MHT_MIN, MHT_MAX = 100, 0, 200

NB_MHT_PHI, MHT_PHI_MIN, MHT_PHI_MAX = 200, -3.14, 3.14

NB_MHT_RATIO, MHT_RATIO_MIN, MHT_RATIO_MAX = 100, 0, 5

NB_MHT_DIFF, MHT_DIFF_MIN, MHT_DIFF_MAX = 100, 0, 5


COMMON_CUT = '!(httL1 < 0.1 && httRef < 0.1) && numPUVertices <25 && numPUVertices>15'


def generate_canvas(w=700, h=600):
    """TCanvas factory method.

    Parameters
    ----------
    w : int, optional
        Width of canvas
    h : int, optional
        Height of canvas

    Returns
    -------
    ROOT.TCanvas
        Canvas object.
    """
    c = ROOT.TCanvas("c", "", w, h)
    c.SetTicks(1, 1)
    return c


def generate_cut_strings(var, bin_edges, bottom_inclusive=True):
    """Convert a series of bin edges into cut strings.

    Parameters
    ----------
    var : str
        Variable name
    bin_edges : list[[float, float]]
        List of pairs of bin edges.
    bottom_inclusive : bool, optional
        Make low bound inclusive
    """
    incl = '=' if bottom_inclusive else ''
    return ['{var} >{incl} {low:g} && {var} < {high:g}'.format(var=var, low=bin_low,
                                                               high=bin_high, incl=incl)
            for (bin_low, bin_high) in bin_edges]


def generate_cut_labels(var, bin_edges, bottom_inclusive=True):
    """Convert a series fo bin edges into labels for legends, etc

    Parameters
    ----------
    var : str
        Description
    bin_edges : list[[float, float]]
        Description
    bottom_inclusive : bool, optional
        Make lower bound inclusive
    """
    incl = '=' if bottom_inclusive else ''
    return ['{low:g} <{incl} {var} < {high:g}'.format(var=var, low=bin_low,
                                                      high=bin_high, incl=incl)
            for (bin_low, bin_high) in bin_edges]


def make_2d_plot(tree,
                 xvar, xtitle, xbins, xmin, xmax,
                 yvar, ytitle, ybins, ymin, ymax,
                 output_filename, cut='', title='',
                 logz=False, normx=False, rescale_peak=True,
                 horizontal_line=False, diagonal_line=False):
    """Make a 2D heat map.

    Parameters
    ----------
    tree : ROOT.TTree
        TTree with branches to plots
    xvar : str
        Variable to plot on x axis
    xtitle : str
        Title of x axis
    xbins : int
        Number of bins on x axis
    xmin : int
        Minimum of x axis range
    xmax : int
        Maximum of x axis range
    yvar : str
        Varaible to plot on y axis
    ytitle : str
        Title of y axis
    ybins : int
        Number of bins on y axis
    ymin : int
        Minimum of y axis range
    ymax : int
        Maximum of y axis range
    output_filename : str
        Output filename for plot
    cut : str, optional
        Cut string to apply when doing Draw()
    title : str, optional
        Title of plot
    logz : bool, optional
        Make Z axis log
    normx : bool, optional
        Normalise each x axis bin s.t. integral over y bins = 1
    rescale_peak : bool, optional
        (Only applies if nromx=True). Rescale peak value in each x bin to be uniform
        across all bins, i.e. sets peak color same in all x bins.
    horizontal_line : bool, optional
        Draw a horizontal line at y = 1
    diagonal_line : bool, optional
        Draw a diagonal line for y = x

    Returns
    -------
    str
        Filename of plot.
    """
    canv = generate_canvas()
    if logz:
        canv.SetLogz()
    hname = str(uuid.uuid1())
    if normx and not logz:
        title += " (NormX)"
    if normx and logz:
        title += " (NormX, log Z scale)"
    h = ROOT.TH2D(hname, ';'.join([title, xtitle, ytitle]),
                  xbins, xmin, xmax, ybins, ymin, ymax)
    tree.Draw("%s:%s>>%s" % (yvar, xvar, hname), cut, 'COLZ')
    h.SetTitleOffset(1.15, 'X')
    h.SetTitleOffset(1.2, 'Y')
    if normx:
        h = cu.norm_vertical_bins(h, rescale_peaks=True)
        h.Draw("COL")

    line = None
    if horizontal_line:
        line = ROOT.TLine(xmin, 1, xmax, 1)
    if diagonal_line:
        upper_lim = xmax if ymax > xmax else ymax
        line = ROOT.TLine(xmin, ymin, upper_lim, upper_lim)
    if line:
        line.SetLineWidth(2)
        line.SetLineStyle(2)
        line.Draw()

    out_stem, ext = os.path.splitext(output_filename)

    app = ''
    if logz:
        app += '_log'
    if normx:
        app += "_normX"
    final_filename = out_stem + app + ext
    canv.SaveAs(final_filename)
    return final_filename


def make_slice_plots(tree, var, xtitle, xbins, xmin, xmax, cuts,
                     output_filename, title='', labels=None, colors=None, styles=None,
                     logy=False, normalise=False):
    """Plot a variable in 'slices' of another, using a series of cuts.

    Parameters
    ----------
    tree : ROOT.TTree
        Description
    var : str
        Description
    xtitle : str
        Description
    xbins : int
        Description
    xmin : float
        Description
    xmax : float
        Description
    cuts : list[str]
        Description
    output_filename : TYPE
        Description
    title : str, optional
        Description
    labels : list[str], optional
        For each graph in legend
    colors : list[int], optional
        For each graph color
    styles : list[int], optional
        For each graph linestyle
    logy : bool, optional
        Description
    normalise : bool, optional
        Description

    Returns
    -------
    str
        Filename of plot
    """
    if labels and len(labels) != len(cuts):
            raise RuntimeError('Incorrect number of labels specified')
    if colors and len(colors) != len(cuts):
            raise RuntimeError('Incorrect number of colors specified')
    if styles and len(styles) != len(cuts):
            raise RuntimeError('Incorrect number of styles specified')
    canv = generate_canvas()
    canv.SetGridx()
    canv.SetGridy()
    if logy:
        canv.SetLogy()
    hists = []
    ytitle = 'p.d.f.' if normalise else 'N'
    hstack = ROOT.THStack("hst", ';'.join([title, xtitle, ytitle]))
    draw_opts = 'HISTE'
    leg = ROOT.TLegend(0.5, 0.6, 0.88, 0.88)
    for i, cut in enumerate(cuts):
        hname = str(uuid.uuid1())
        h = ROOT.TH1D(hname, ';'.join([title, xtitle, ytitle]), xbins, xmin, xmax)
        tree.Draw("%s>>%s" % (var, hname), cut, draw_opts)
        h.SetLineWidth(2)
        if h.Integral() == 0:
            continue
        if normalise:
            h.Scale(1. / h.Integral())
        if colors:
            h.SetLineColor(colors[i])
        if styles:
            h.SetLineStyle(styles[i])
        hists.append(h)
        hstack.Add(h)
        label = labels[i] if labels else cut
        leg.AddEntry(h, label, 'L')

    hstack.Draw(draw_opts + ' NOSTACK')
    hstack.GetYaxis().SetTitleOffset(1.3)
    leg.Draw()
    canv.SaveAs(output_filename)
    return output_filename


def make_htt_plots(input_filename, output_dir):
    """Make HTT plots for one input file.

    Parameters
    ----------
    input_filename : str
        Name of pairs ROOT file.
    output_dir : str
        Name of output directory for plots.
    """
    in_stem = os.path.splitext(os.path.basename(input_filename))[0]
    output_dir = os.path.join(output_dir, in_stem)
    if not os.path.isdir(output_dir):
        print 'Making output dir', output_dir
        os.makedirs(output_dir)

    f = cu.open_root_file(input_filename)
    tree = cu.get_from_file(f, "valid")

    common_cut = COMMON_CUT
    norm_cut = '1./nMatches'  # normalisation, for event-level quantities, since we store it for each match in an event
    if common_cut != '':
        norm_cut += ' && %s' % common_cut

    do_htt_plots(tree, output_dir, norm_cut)

    do_mht_plots(tree, output_dir, norm_cut)

    # Do plots where y axis is some variable of interest
    do_dr_plots(tree, output_dir, common_cut)

    do_rsp_plots(tree, output_dir, common_cut)

    do_nvtx_plots(tree, output_dir, norm_cut)

    do_njets_plots(tree, output_dir, norm_cut)

    do_jet_pt_plots(tree, output_dir, common_cut)

    f.Close()


def do_htt_plots(tree, output_dir, cut=''):
    """Do HTT plots (httRatio, HTT diff).

    Parameters
    ----------
    tree : ROOT.TTree
        Tree with variables
    output_dir : str
        Output directory for plots
    cut : str, optional
        Cut to apply when filling plots. MUST INCLUDE NORMALISATION CUT
    """
    for logz in [True, False]:
        make_2d_plot(tree, 'httRef', HTT_REF_STR, NB_HTT, HTT_MIN, HTT_MAX, 'httL1', HTT_L1_STR, NB_HTT, HTT_MIN, HTT_MAX,
                     os.path.join(output_dir, 'httRef_httL1.pdf'), logz=logz, normx=False,
                     cut=cut, title=TITLE, diagonal_line=True)
        for normx in [True, False]:
            make_2d_plot(tree, 'httL1', HTT_L1_STR, NB_HTT, HTT_MIN, HTT_MAX, 'httL1/httRef', HTT_RATIO_STR, NB_HTT_RATIO, HTT_RATIO_MIN, HTT_RATIO_MAX,
                         os.path.join(output_dir, 'httRatio_httL1.pdf'), logz=logz, normx=normx,
                         cut=cut, title=TITLE, horizontal_line=True)
            make_2d_plot(tree, 'httRef', HTT_REF_STR, NB_HTT, HTT_MIN, HTT_MAX, 'httL1/httRef', HTT_RATIO_STR, NB_HTT_RATIO, HTT_RATIO_MIN, HTT_RATIO_MAX,
                         os.path.join(output_dir, 'httRatio_httRef.pdf'), logz=logz, normx=normx,
                         cut=cut, title=TITLE, horizontal_line=True)

            make_2d_plot(tree, 'httL1', HTT_L1_STR, NB_HTT, HTT_MIN, HTT_MAX, 'httL1-httRef', HTT_DIFF_STR, NB_HTT_DIFF, HTT_DIFF_MIN, HTT_DIFF_MAX,
                         os.path.join(output_dir, 'httDiff_httL1.pdf'), logz=logz, normx=normx,
                         cut=cut, title=TITLE, horizontal_line=True)
            make_2d_plot(tree, 'httRef', HTT_REF_STR, NB_HTT, HTT_MIN, HTT_MAX, 'httL1-httRef', HTT_DIFF_STR, NB_HTT_DIFF, HTT_DIFF_MIN, HTT_DIFF_MAX,
                         os.path.join(output_dir, 'httDiff_httRef.pdf'), logz=logz, normx=normx,
                         cut=cut, title=TITLE, horizontal_line=True)
            make_2d_plot(tree, 'httL1/httRef', HTT_RATIO_STR, NB_HTT_RATIO, HTT_RATIO_MIN, HTT_RATIO_MAX,
                         'httL1-httRef', HTT_DIFF_STR, NB_HTT_DIFF, HTT_DIFF_MIN, HTT_DIFF_MAX,
                         os.path.join(output_dir, 'httDiff_httRatio.pdf'), logz=logz, normx=normx,
                         cut=cut, title=TITLE, horizontal_line=True)


def do_mht_plots(tree, output_dir, cut=''):
    """Do MHT plots

    Parameters
    ----------
    tree : ROOT.TTree
        Tree with variables
    output_dir : str
        Output directory for plots
    cut : str, optional
        Cut to apply when filling plots. MUST INCLUDE NORMALISATION CUT
    """
    for logz in [True, False]:
        make_2d_plot(tree, 'mhtRef', MHT_REF_STR, NB_MHT, MHT_MIN, MHT_MAX, 'mhtL1', MHT_L1_STR, NB_MHT, MHT_MIN, MHT_MAX,
                     os.path.join(output_dir, 'mhtRef_mhtL1.pdf'), logz=logz, normx=False,
                     cut=cut, title=TITLE, diagonal_line=True)
        for normx in [True, False]:
            make_2d_plot(tree, 'mhtL1', MHT_L1_STR, NB_MHT, MHT_MIN, MHT_MAX, 'mhtL1/mhtRef', MHT_RATIO_STR, NB_MHT_RATIO, MHT_RATIO_MIN, MHT_RATIO_MAX,
                         os.path.join(output_dir, 'mhtRatio_mhtL1.pdf'), logz=logz, normx=normx,
                         cut=cut, title=TITLE, horizontal_line=True)
            make_2d_plot(tree, 'mhtRef', MHT_REF_STR, NB_MHT, MHT_MIN, MHT_MAX, 'mhtL1/mhtRef', MHT_RATIO_STR, NB_MHT_RATIO, MHT_RATIO_MIN, MHT_RATIO_MAX,
                         os.path.join(output_dir, 'mhtRatio_mhtRef.pdf'), logz=logz, normx=normx,
                         cut=cut, title=TITLE, horizontal_line=True)
            make_2d_plot(tree, 'TVector2::Phi_mpi_pi(mhtPhiL1 - mhtPhiRef)', '#Delta#phi MHT', NB_MHT_PHI, MHT_PHI_MIN, MHT_PHI_MAX, 'mhtL1/mhtRef', MHT_RATIO_STR, NB_MHT_RATIO, MHT_RATIO_MIN, MHT_RATIO_MAX,
                         os.path.join(output_dir, 'mhtRatio_mhtPhiDiff.pdf'), logz=logz, normx=normx,
                         cut=cut, title=TITLE, horizontal_line=True)
            make_2d_plot(tree, 'mhtL1', MHT_L1_STR, NB_MHT, MHT_MIN, MHT_MAX, 'mhtL1-mhtRef', MHT_DIFF_STR, NB_MHT_DIFF, MHT_DIFF_MIN, MHT_DIFF_MAX,
                         os.path.join(output_dir, 'mhtDiff_mhtL1.pdf'), logz=logz, normx=normx,
                         cut=cut, title=TITLE, horizontal_line=True)
            make_2d_plot(tree, 'mhtRef', MHT_REF_STR, NB_MHT, MHT_MIN, MHT_MAX, 'mhtL1-mhtRef', MHT_DIFF_STR, NB_MHT_DIFF, MHT_DIFF_MIN, MHT_DIFF_MAX,
                         os.path.join(output_dir, 'mhtDiff_mhtRef.pdf'), logz=logz, normx=normx,
                         cut=cut, title=TITLE, horizontal_line=True)
            make_2d_plot(tree, 'mhtL1/mhtRef', MHT_RATIO_STR, NB_MHT_RATIO, MHT_RATIO_MIN, MHT_RATIO_MAX,
                         'mhtL1-mhtRef', MHT_DIFF_STR, NB_MHT_DIFF, MHT_DIFF_MIN, MHT_DIFF_MAX,
                         os.path.join(output_dir, 'mhtDiff_httRatio.pdf'), logz=logz, normx=normx,
                         cut=cut, title=TITLE, horizontal_line=True)


def do_dr_plots(tree, output_dir, cut=''):
    """Do DeltaR plots

    Parameters
    ----------
    tree : ROOT.TTree
        Tree with variables
    output_dir : str
        Output directory for plots
    cut : str, optional
        Cut to apply when filling plots
    """
    for logz, normx in product([True, False], [True, False]):
        make_2d_plot(tree, 'rsp', RSP_STR, NB_RSP, RSP_MIN, RSP_MAX, 'dr', DR_STR, NB_DR, DR_MIN, DR_MAX,
                     os.path.join(output_dir, 'dr_rsp.pdf'), logz=logz, normx=normx,
                     cut=cut, title=TITLE, horizontal_line=True)
        make_2d_plot(tree, 'httL1', HTT_L1_STR, NB_HTT, HTT_MIN, HTT_MAX, 'dr', DR_STR, NB_DR, DR_MIN, DR_MAX,
                     os.path.join(output_dir, 'dr_httL1.pdf'), logz=logz, normx=normx,
                     cut=cut, title=TITLE, horizontal_line=True)
        make_2d_plot(tree, 'httRef', HTT_REF_STR, NB_HTT, HTT_MIN, HTT_MAX, 'dr', DR_STR, NB_DR, DR_MIN, DR_MAX,
                     os.path.join(output_dir, 'dr_httRef.pdf'), logz=logz, normx=normx,
                     cut=cut, title=TITLE, horizontal_line=True)
    for logz in [True, False]:
        # dont want normx for this
        make_2d_plot(tree, 'dphi', DPHI_STR, NB_DR, -1 * DR_MAX, DR_MAX, 'deta', DETA_STR, NB_DR, -1 * DR_MAX, DR_MAX,
                     os.path.join(output_dir, 'deta_dphi.pdf'), logz=logz, normx=normx,
                     cut=cut, title=TITLE, horizontal_line=True)
    # plot dr in bins of HTT(l1)
    htt_bin_edges = [[30, 50], [50, 75], [75, 100], [100, 150], [150, 200], [200, 300], [300, 400]][:4]
    htt_bins = generate_cut_strings('httL1', htt_bin_edges)
    htt_labels = generate_cut_labels(HTT_L1_STR, htt_bin_edges)
    make_slice_plots(tree, 'dr', DR_STR, NB_DR, DR_MIN, DR_MAX, htt_bins,
                     os.path.join(output_dir, 'dr_httL1_slices.pdf'), title=TITLE,
                     normalise=True, labels=htt_labels, colors=binning.eta_bin_colors[:len(htt_bins)])
    # plot dr in bins of HTT(Ref)
    htt_bins = generate_cut_strings('httRef', htt_bin_edges)
    htt_labels = generate_cut_labels(HTT_REF_STR, htt_bin_edges)
    make_slice_plots(tree, 'dr', DR_STR, NB_DR, DR_MIN, DR_MAX, htt_bins,
                     os.path.join(output_dir, 'dr_httRef_slices.pdf'), title=TITLE,
                     normalise=True, labels=htt_labels, colors=binning.eta_bin_colors[:len(htt_bins)])


def do_rsp_plots(tree, output_dir, cut=''):
    """Do response plots

    Parameters
    ----------
    tree : ROOT.TTree
        Tree with variables
    output_dir : str
        Output directory for plots
    cut : str, optional
        Cut string to apply when filling plots
    """
    for logz, normx in product([True, False], [True, False]):
        make_2d_plot(tree, 'pt', PT_L1_STR, NB_PT, PT_MIN, PT_MAX, 'rsp', RSP_STR, NB_RSP, RSP_MIN, RSP_MAX,
                     os.path.join(output_dir, 'rsp_pt.pdf'), logz=logz, normx=normx,
                     cut=cut, title=TITLE, horizontal_line=True)
        make_2d_plot(tree, 'ptRef', PT_REF_STR, NB_PT, PT_MIN, PT_MAX, 'rsp', RSP_STR, NB_RSP, RSP_MIN, RSP_MAX,
                     os.path.join(output_dir, 'rsp_ptRef.pdf'), logz=logz, normx=normx,
                     cut=cut, title=TITLE, horizontal_line=True)
        make_2d_plot(tree, 'httL1', HTT_L1_STR, NB_HTT, HTT_MIN, HTT_MAX, 'rsp', RSP_STR, NB_RSP, RSP_MIN, RSP_MAX,
                     os.path.join(output_dir, 'rsp_httL1.pdf'), logz=logz, normx=normx,
                     cut=cut, title=TITLE, horizontal_line=True)
        make_2d_plot(tree, 'httRef', HTT_REF_STR, NB_HTT, HTT_MIN, HTT_MAX, 'rsp', RSP_STR, NB_RSP, RSP_MIN, RSP_MAX,
                     os.path.join(output_dir, 'rsp_httRef.pdf'), logz=logz, normx=normx,
                     cut=cut, title=TITLE, horizontal_line=True)
        make_2d_plot(tree, 'httL1/httRef', HTT_RATIO_STR, NB_HTT_RATIO, HTT_RATIO_MIN, HTT_RATIO_MAX,
                     'rsp', RSP_STR, NB_RSP, RSP_MIN, RSP_MAX,
                     os.path.join(output_dir, 'rsp_httRatio.pdf'), logz=logz, normx=normx,
                     cut=cut, title=TITLE, horizontal_line=True)

        # plot rsp in bins of HTT(l1)
        htt_bin_edges = [[30, 50], [50, 75], [75, 100], [100, 150], [150, 200], [200, 300], [300, 400]][:4]
        htt_bins = generate_cut_strings('httL1', htt_bin_edges)
        htt_labels = generate_cut_labels(HTT_L1_STR, htt_bin_edges)
        make_slice_plots(tree, 'rsp', RSP_STR, NB_RSP, RSP_MIN, RSP_MAX, htt_bins,
                         os.path.join(output_dir, 'rsp_httL1_slices.pdf'), title=TITLE,
                         normalise=True, labels=htt_labels, colors=binning.eta_bin_colors[:len(htt_bins)])
        # plot rsp in bins of HTT(Ref)
        htt_bins = generate_cut_strings('httRef', htt_bin_edges)
        htt_labels = generate_cut_labels(HTT_REF_STR, htt_bin_edges)
        make_slice_plots(tree, 'rsp', RSP_STR, NB_RSP, RSP_MIN, RSP_MAX, htt_bins,
                         os.path.join(output_dir, 'rsp_httRef_slices.pdf'), title=TITLE,
                         normalise=True, labels=htt_labels, colors=binning.eta_bin_colors[:len(htt_bins)])


def do_nvtx_plots(tree, output_dir, cut=''):
    """Do nVtx plots

    Parameters
    ----------
    tree : ROOT.TTree
        Tree with variables
    output_dir : str
        Output directory for plots
    cut : str, optional
        Cut string to apply
    """

    for logz, normx in product([True, False], [True, False]):
        make_2d_plot(tree, 'httL1', HTT_L1_STR, NB_HTT, HTT_MIN, HTT_MAX, 'numPUVertices', NVTX_STR, 20, 0, 20,
                     os.path.join(output_dir, 'nvtx_httL1.pdf'), logz=logz, normx=normx,
                     cut=cut, title=TITLE)
        make_2d_plot(tree, 'httRef', HTT_REF_STR, NB_HTT, HTT_MIN, HTT_MAX, 'numPUVertices', NVTX_STR, 20, 0, 20,
                     os.path.join(output_dir, 'nvtx_httRef.pdf'), logz=logz, normx=normx,
                     cut=cut, title=TITLE)
        make_2d_plot(tree, 'rsp', RSP_STR, 50, RSP_MIN, RSP_MAX, 'numPUVertices', NVTX_STR, 20, 0, 20,
                     os.path.join(output_dir, 'nvtx_rsp.pdf'), logz=logz, normx=normx,
                     cut=cut, title=TITLE)
        make_2d_plot(tree, 'httL1/httRef', HTT_RATIO_STR, NB_HTT_RATIO, HTT_RATIO_MIN, HTT_RATIO_MAX, 'numPUVertices', NVTX_STR, 20, 0, 20,
                     os.path.join(output_dir, 'nvtx_httRatio.pdf'), logz=logz, normx=normx,
                     cut=cut, title=TITLE)


def do_njets_plots(tree, output_dir, cut=''):
    """Do nJets plots.

    Parameters
    ----------
    tree : ROOT.TTree
        Description
    output_dir : str
        Description
    cut : str, optional
        Description
    """
    for logz, normx in product([True, False], [True, False]):
        make_2d_plot(tree, 'httL1', HTT_L1_STR, NB_HTT, HTT_MIN, HTT_MAX, 'nL1', NUM_L1_STR, 10, 0, 10,
                     os.path.join(output_dir, 'nL1jets_httL1.pdf'), logz=logz, normx=normx,
                     cut=cut, title=TITLE)
        make_2d_plot(tree, 'httL1', HTT_L1_STR, NB_HTT, HTT_MIN, HTT_MAX, 'nRef', NUM_REF_STR, 10, 0, 10,
                     os.path.join(output_dir, 'nRefjets_httL1.pdf'), logz=logz, normx=normx,
                     cut=cut, title=TITLE)
        make_2d_plot(tree, 'httRef', HTT_REF_STR, NB_HTT, HTT_MIN, HTT_MAX, 'nL1', NUM_L1_STR, 10, 0, 10,
                     os.path.join(output_dir, 'nL1jets_httRef.pdf'), logz=logz, normx=normx,
                     cut=cut, title=TITLE)
        make_2d_plot(tree, 'httRef', HTT_REF_STR, NB_HTT, HTT_MIN, HTT_MAX, 'nRef', NUM_REF_STR, 10, 0, 10,
                     os.path.join(output_dir, 'nRefjets_httRef.pdf'), logz=logz, normx=normx,
                     cut=cut, title=TITLE)
        make_2d_plot(tree, 'httL1/httRef', HTT_RATIO_STR, NB_HTT_RATIO, HTT_RATIO_MIN, HTT_RATIO_MAX,
                     'nL1', NUM_L1_STR, 10, 0, 10,
                     os.path.join(output_dir, 'nL1Jets_httRatio.pdf'), logz=logz, normx=normx,
                     cut=cut, title=TITLE)
        make_2d_plot(tree, 'httL1/httRef', HTT_RATIO_STR, NB_HTT_RATIO, HTT_RATIO_MIN, HTT_RATIO_MAX,
                     'nRef', NUM_REF_STR, 10, 0, 10,
                     os.path.join(output_dir, 'nRefJets_httRatio.pdf'), logz=logz, normx=normx,
                     cut=cut, title=TITLE)
        make_2d_plot(tree, 'httL1/httRef', HTT_RATIO_STR, NB_HTT_RATIO, HTT_RATIO_MIN, HTT_RATIO_MAX,
                     'nL1/nRef', '# L1 jets / # PF jets', 10, 0, 5,
                     os.path.join(output_dir, 'nJetRatio_httRatio.pdf'), logz=logz, normx=normx,
                     cut=cut, title=TITLE)


def do_jet_pt_plots(tree, output_dir, cut=''):
    """Do jet pt plots

    Parameters
    ----------
    tree : ROOT.TTree
        Description
    output_dir : str
        Description
    cut : str, optional
        Description
    """
    for logz, normx in product([True, False], [True, False]):
        make_2d_plot(tree, 'httL1', HTT_L1_STR, NB_HTT, HTT_MIN, HTT_MAX, 'pt', PT_L1_STR, NB_PT, PT_MIN, PT_MAX,
                     os.path.join(output_dir, 'pt_httL1.pdf'), logz=logz, normx=normx,
                     cut=cut, title=TITLE, diagonal_line=True)
        make_2d_plot(tree, 'httL1', HTT_L1_STR, NB_HTT, HTT_MIN, HTT_MAX, 'ptRef', PT_REF_STR, NB_PT, PT_MIN, PT_MAX,
                     os.path.join(output_dir, 'ptRef_httL1.pdf'), logz=logz, normx=normx,
                     cut=cut, title=TITLE, diagonal_line=True)
        make_2d_plot(tree, 'httRef', HTT_REF_STR, NB_HTT, HTT_MIN, HTT_MAX, 'pt', PT_L1_STR, NB_PT, PT_MIN, PT_MAX,
                     os.path.join(output_dir, 'pt_httRef.pdf'), logz=logz, normx=normx,
                     cut=cut, title=TITLE, diagonal_line=True)
        make_2d_plot(tree, 'httRef', HTT_REF_STR, NB_HTT, HTT_MIN, HTT_MAX, 'ptRef', PT_REF_STR, NB_PT, PT_MIN, PT_MAX,
                     os.path.join(output_dir, 'ptRef_httRef.pdf'), logz=logz, normx=normx,
                     cut=cut, title=TITLE, diagonal_line=True)


if __name__ == "__main__":
    make_htt_plots(INPUT, OUTPUT)
