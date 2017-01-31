#!/bin/usr/env python
"""
Little script to plot several graphs and/or fit functions on the same canvas.
Can take any graph, from any file.
For calibration curve plots
"""


import os
import ROOT
import binning
from binning import pairwise
from comparator import Contribution, Plot
from copy import deepcopy
from itertools import izip
import common_utils as cu

ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(1)
ROOT.TH1.SetDefaultSumw2()
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPalette(55)


# a set of 11 varying colours
colors = [ROOT.kRed, ROOT.kBlue, ROOT.kBlack, ROOT.kGreen+2, ROOT.kMagenta,
          ROOT.kOrange+7, ROOT.kAzure+1, ROOT.kRed+3, ROOT.kViolet+1,
          ROOT.kOrange-3, ROOT.kTeal-5, ROOT.kViolet, ROOT.kCyan+4]

# x limits for "zoomed" plots
zoom_pt = [0, 150]

def setup_new_graphs(old_graphs, name_dict):
    """Create copy of graphs in old_graphs,
    renaming them by applying .format(name_dict)"""
    new_graphs = deepcopy(old_graphs)
    for ng, og in izip(new_graphs, old_graphs):
        ng.obj_name = og.obj_name.format(**name_dict)
    return new_graphs


def compare_PU_by_eta_bins(graphs, title, oDir, ylim=None, lowpt_zoom=True):
    """Plot graph contributions, with a different plot for each eta bin.
    Relies on each Contribution.obj_name in graphs being templated with the
    variables `eta_min` and `eta_max`.
    Parameters
    ----------
    graphs : list[Contribution]
        List of Contribution objects to be included on any one plot.
    title : str
        Title to put on plots
    oDir : str
        Output directory for plots
    ylim : list, optional
        Set y axis range
    lowpt_zoom : bool, optional
        Zoom in on low pt range
    """

    cu.check_dir_exists_create(oDir)
    for i, (eta_min, eta_max) in enumerate(pairwise(binning.eta_bins)):
        rename_dict = dict(eta_min=eta_min, eta_max=eta_max)
        eta_min_str = '{:g}'.format(eta_min).replace('.', 'p')
        eta_max_str = '{:g}'.format(eta_max).replace('.', 'p')

        # make a copy as we have to change the graph names
        new_graphs = setup_new_graphs(graphs, rename_dict)

        if not ylim:
            ylim = [0.5, 2] if eta_min > 2 else [0.5, 2.5]
        p = Plot(contributions=new_graphs, what="graph", xtitle="<p_{T}^{L1}>",
                 ytitle="Correction value (= 1/response)",
                 title=title.format(**rename_dict), ylim=ylim)
        p.plot()
        p.save(os.path.join(oDir, "compare_PU_eta_%s_%s.pdf" % (eta_min_str, eta_max_str)))

        if lowpt_zoom:
            # zoom in on low pT
            p = Plot(contributions=new_graphs, what="graph", xtitle="<p_{T}^{L1}>",
                     ytitle="Correction value (= 1/response)",
                     title=title.format(**rename_dict), xlim=zoom_pt, ylim=ylim)
            p.plot()
            p.save(os.path.join(oDir, "compare_PU_eta_%s_%s_pTzoomed.pdf" % (eta_min_str, eta_max_str)))


def compare():
    """Make all da plots"""

    # New 
    s2_new = '/users/jt15104/local_L1JEC_store/30June2016_QCDFlatFall15PU0to50NzshcalRaw_ak4_ref10to5000_809v70_noJEC_893ca_etaBinsSel16/runCalib_jetMetFitErr/'
    f_PU0to10_new = os.path.join(s2_new, 'totalPairs_L1Ntuple_etaBinsSel16_PU0to10_maxPt1022.root')
    f_PU15to25_new = os.path.join(s2_new, 'totalPairs_L1Ntuple_etaBinsSel16_PU15to25_maxPt1022.root')
    f_PU30to40_new = os.path.join(s2_new, 'totalPairs_L1Ntuple_etaBinsSel16_PU30to40_maxPt1022.root')
    f_PU45to55_new = os.path.join(s2_new, 'totalPairs_L1Ntuple_etaBinsSel16_PU45to55_maxPt1022.root')

    pu_labels = ['PU0to10', 'PU15to25', 'PU30to40']

    # common object name
    corr_eta_graph_name = "l1corr_eta_{eta_min:g}_{eta_max:g}"

    # --------------------------------------------------------------------
    # New Stage 2 curves
    # Plot different PU scenarios for given eta bin
    # --------------------------------------------------------------------
    graphs = [
        Contribution(file_name=f_PU0to10_new, obj_name=corr_eta_graph_name,
                     label="PU: 0 - 10", line_color=colors[1], marker_color=colors[1]),
        Contribution(file_name=f_PU15to25_new, obj_name=corr_eta_graph_name,
                     label="PU: 15 - 25", line_color=colors[2], marker_color=colors[2]),
        Contribution(file_name=f_PU30to40_new, obj_name=corr_eta_graph_name,
                     label="PU: 30 - 40", line_color=colors[3], marker_color=colors[3]),
        Contribution(file_name=f_PU45to55_new, obj_name=corr_eta_graph_name,
                     label="PU: 45 - 55", line_color=colors[4], marker_color=colors[4])
    ]
    title = "Fall15 MC, Stage2, {eta_min:g} < |#eta^{{L1}}| < {eta_max:g}"
    compare_PU_by_eta_bins(graphs, title, os.path.join(s2_new, 'comparePU'), lowpt_zoom=True)


if __name__ == "__main__":
    compare()