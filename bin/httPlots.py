#!/usr/bin/env python

"""
Produce plots for HTT studies.
"""

import ROOT
import os
import binning
import common_utils as cu
from itertools import product


ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(1)
ROOT.gStyle.SetOptFit(1111)
ROOT.TH1.SetDefaultSumw2(True)
ROOT.gStyle.SetPalette(55)


ODIR = '/users/ra12451/L1JEC/CMSSW_8_0_0_pre6/src/L1Trigger/L1JetEnergyCorrections/httStudies'

INPUT_FILES = [
    '/users/ra12451/L1JEC/CMSSW_8_0_0_pre6/src/L1Trigger/L1JetEnergyCorrections/httStudies/pairs_all.root',
    '/users/ra12451/L1JEC/CMSSW_8_0_0_pre6/src/L1Trigger/L1JetEnergyCorrections/httStudies/pairs_muMult0.root',
    '/users/ra12451/L1JEC/CMSSW_8_0_0_pre6/src/L1Trigger/L1JetEnergyCorrections/httStudies/pairs_clean.root'
]


# Some common strings
PT_L1_STR = 'p_{T}^{L1} [GeV]'
PT_REF_STR = 'p_{T}^{PF} [GeV]'
RSP_STR = 'Response'
HTT_L1_STR = 'HTT (L1) [GeV]'
HTT_REF_STR = 'HTT (RECO) [GeV]'
DR_STR = '#DeltaR(L1, PF)'


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


def make_2d_plot(tree,
                 xvar, xtitle, xbins, xmin, xmax,
                 yvar, ytitle, ybins, ymin, ymax,
                 output_filename, cut='', title='', logz=False, normx=False,
                 horizontal_line=False, diagonal_line=False):
    """Make a 2D heat map.

    Parameters
    ----------
    tree : ROOT.TTree
        Description
    xvar : str
        Description
    xtitle : str
        Description
    xbins : int
        Description
    xmin : int
        Description
    xmax : int
        Description
    yvar : str
        Description
    ytitle : str
        Description
    ybins : int
        Description
    ymin : int
        Description
    ymax : int
        Description
    output_filename : str
        Description
    cut : str, optional
        Description
    title : str, optional
        Description
    logz : bool, optional
        Description
    normx : bool, optional
        Description
    horizontal_line : bool, optional
        Draw a horizontal line at y = 1
    diagonal_line : bool, optional
        Draw a diagonal line for y = x
    """
    canv = generate_canvas()
    if logz:
        canv.SetLogz()
    hname = 'h'
    h = ROOT.TH2D(hname, ';'.join([title, xtitle, ytitle]),
                  xbins, xmin, xmax, ybins, ymin, ymax)
    tree.Draw("%s:%s>>%s" % (yvar, xvar, hname), cut, 'COLZ')
    h.SetTitleOffset(1.15, 'X')
    h.SetTitleOffset(1.2, 'Y')
    if normx:
        h = cu.norm_vertical_bins(h)
        h.Draw("COLZ")

    line = None
    if horizontal_line:
        line = ROOT.TLine(xmin, 1, xmax, 1)
    if diagonal_line:
        line = ROOT.TLine(xmin, ymin, xmax, ymax)
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
    canv.SaveAs(out_stem + app + ext)


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

    cut = ''
    # if 'clean' in in_stem.lower():
    #     cut = 'httRef>0'
    # elif 'mumult0' in in_stem.lower():
    #     cut = 'httRef>0'

    for logz in [True, False]:
        make_2d_plot(tree, 'httRef', HTT_REF_STR, 80, 0, 800, 'httL1', HTT_L1_STR, 80, 0, 800,
                     os.path.join(output_dir, 'httRef_httL1.pdf'), logz=logz, normx=False,
                     cut=cut, title='Run260627 SingleMu with L1JEC', diagonal_line=True)

    do_dr_plots(tree, output_dir, cut)

    do_rsp_plots(tree, output_dir, cut)

    f.Close()


def do_dr_plots(tree, output_dir, cut=''):
    """Do DeltaR plots

    Parameters
    ----------
    tree : ROOT.TTree
        Treee with variables
    output_dir : str
        Output directory for plots
    cut : str, optional
        Cut to apply when filling plots
    """
    for logz, normx in product([True, False], [True, False]):
        title = 'Run260627 SingleMu with L1JEC'
        make_2d_plot(tree, 'rsp', RSP_STR, 50, 0.5, 2.5, 'dr', DR_STR, 40, 0, 0.4,
                     os.path.join(output_dir, 'dr_rsp.pdf'), logz=logz, normx=normx,
                     cut=cut, title=title, horizontal_line=True)
        make_2d_plot(tree, 'httL1', HTT_L1_STR, 40, 0, 200, 'dr', DR_STR, 40, 0, 0.4,
                     os.path.join(output_dir, 'dr_httL1.pdf'), logz=logz, normx=normx,
                     cut=cut, title=title, horizontal_line=True)
        make_2d_plot(tree, 'httRef', HTT_REF_STR, 40, 0, 200, 'dr', DR_STR, 40, 0, 0.4,
                     os.path.join(output_dir, 'dr_httRef.pdf'), logz=logz, normx=normx,
                     cut=cut, title=title, horizontal_line=True)


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
        title = 'Run260627 SingleMu with L1JEC'
        make_2d_plot(tree, 'pt', PT_L1_STR, 40, 0, 200, 'rsp', RSP_STR, 50, 0.5, 2.5,
                     os.path.join(output_dir, 'rsp_pt.pdf'), logz=logz, normx=normx,
                     cut=cut, title=title, horizontal_line=True)
        make_2d_plot(tree, 'ptRef', PT_REF_STR, 40, 0, 200, 'rsp', RSP_STR, 50, 0.5, 2.5,
                     os.path.join(output_dir, 'rsp_ptRef.pdf'), logz=logz, normx=normx,
                     cut=cut, title=title, horizontal_line=True)
        make_2d_plot(tree, 'httL1', HTT_L1_STR, 40, 0, 200, 'rsp', RSP_STR, 50, 0.5, 2.5,
                     os.path.join(output_dir, 'rsp_httL1.pdf'), logz=logz, normx=normx,
                     cut=cut, title=title, horizontal_line=True)
        make_2d_plot(tree, 'httRef', HTT_REF_STR, 40, 0, 200, 'rsp', RSP_STR, 50, 0.5, 2.5,
                     os.path.join(output_dir, 'rsp_httRef.pdf'), logz=logz, normx=normx,
                     cut=cut, title=title, horizontal_line=True)
        # plot rsp in bins of HTT(l1)

        # plot rsp in bins of HTT(Ref)


if __name__ == "__main__":
    for ifile in INPUT_FILES:
        make_htt_plots(ifile, ODIR)
