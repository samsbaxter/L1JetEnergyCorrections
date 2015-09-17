#!/bin/usr/env python
"""
Little script to plot several graphs and/or fit functions on the same canvas.
Can take any graph, from any file.

TODO: expand to hists?

Example usage:

    A = Contribution("a.root", "li1corr_eta_0_0.348")
    B = Contribution("b.root", "li1corr_eta_0_0.348")
    p = Plot([A, B], "graphfunction", xlim=[0, 50])
    p.plot()
    p.save("AB.pdf")

"""

import os
import ROOT
import random
# from itertools import izip, product, chain
import common_utils as cu
import binning as binning


ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(1)
ROOT.TH1.SetDefaultSumw2()
ROOT.gStyle.SetOptStat(0);
ROOT.gStyle.SetPalette(55)


class MultiFunc(object):
    """Class to handle multiple TF1s, like a TMultiGraph, because ROOT doesn't.

    TODO: implement so can iterate over containees e.g.

    for f in mulitf:
        f.Print()

    NOT SOPHISTICATED, JUST A CONTAINER.
    """
    def __init__(self):
        self.funcs = []

    def Add(self, func):
        self.funcs.append(func)

    def Draw(self, option=""):
        """Draw all the TF1s, adjust the axis sizes properly"""
        # if ROOT.gPad:
        #     if not ROOT.gPad.IsEditable():
        #         ROOT.gROOT.MakeDefCanvas()
        #     if "a" in option.lower():
        #         ROOT.gPad.Clear()

        # Draw, and figure out max/min of axes for some auto-ranging
        x_low, x_high = ROOT.Double(0), ROOT.Double(0)
        x_min, x_max = 999, -999
        y_min, y_max = 999, -999
        for i, f in enumerate(self.funcs):
            if i == 0:
                f.Draw(option)
            else:
                f.Draw(option+"SAME")

            f.GetRange(x_low, x_high)
            x_min = x_low if x_low < x_min else x_min
            x_max = x_high if x_high > x_max else x_max
            y_min = f.GetMinimum(x_low, x_high) if f.GetMinimum(x_low, x_high) < y_min else y_min
            y_max = f.GetMaximum(x_low, x_high) if f.GetMaximum(x_low, x_high) > y_max else y_max
        if x_max < x_min:
            raise Exception("MultiFunc: x_min > x_max")
        if y_max < y_min:
            raise Exception("MultiFunc: y_min > y_max")

        print x_min, x_max
        print y_min, y_max

        self.funcs[0].GetXaxis().SetRangeUser(x_min * 0.95, x_max * 1.05)
        self.funcs[0].GetYaxis().SetRangeUser(y_min * 0.95, y_max * 1.05)

    def Mod(self):
        """If we want to do any sort of styling, need to access the first drawn func"""
        return self.funcs[0]


class Contribution(object):
    """Basic class to handle information about one contribution to a canvas."""

    def __init__(self, file_name, obj_name, label="",
                 line_width=1, line_color=ROOT.kRed, line_style=1,
                 marker_size=1, marker_color=ROOT.kRed, marker_style=1):
        """
        file_name: str. Name of ROOT file to get object from.
        obj_name: str. Name of object in ROOT file.
        label: str. Title of contribution, to be used in legend.
        line_width: int. Width of line.
        line_color: int or ROOT color. Color of line.
        line_style: int. Line style.
        marker_size: int. Size of marker
        marker_color: int or ROOT color. Color of markers.
        marker_style: int. Marker style.
        """
        self.file_name = file_name
        self.obj_name = obj_name
        self.label = label
        self.line_width = line_width
        self.line_color = line_color
        self.line_style = line_style
        self.marker_size = marker_size
        self.marker_color = marker_color
        self.marker_style = marker_style

    def get_obj(self):
        """Get object for this contribution."""
        input_file = cu.open_root_file(self.file_name)
        self.obj = cu.get_from_file(input_file, self.obj_name)
        self.obj.SetLineWidth(self.line_width)
        self.obj.SetLineColor(self.line_color)
        self.obj.SetLineStyle(self.line_style)
        self.obj.SetMarkerSize(self.marker_size)
        self.obj.SetMarkerColor(self.marker_color)
        self.obj.SetMarkerStyle(self.marker_style)
        input_file.Close()
        return self.obj


class Plot(object):
    """
    Basic class to handle information about one plot,
    which can have several contributions.
    """

    def __init__(self, contributions=None, what="graph",
                 title="", xtitle="", ytitle="", xlim=None, ylim=None,
                 legend=True, extend=False):
        """
        contributions: list. List of Contribution objects.
        what: str. Options are "graph", "function", "both". "both" assumes
            that the function is 'conatined' in the graph
        title: str. Title of plot.
        xtitle: str. X axis title.
        ytitle: str. Y axis title.
        xlim: list. Limits of x axis. If None then determines suitable limits.
        ylim: list. Limits of y axis. If None then determines suitable limits.
        legend: bool. Include legend on plot.
        extend: bool. Extend functions to cover the whole x axis range.
        """
        self.contributions = contributions if contributions else []
        self.plot_what = what
        self.title = title
        self.xtitle = xtitle
        self.ytitle = ytitle
        self.xlim = xlim
        self.ylim = ylim
        self.do_legend = legend
        self.legend = ROOT.TLegend(0.65, 0.55, 0.87, 0.87) if legend else None
        self.do_extend = extend
        self.container = None
        self.canvas = None

    def add_contribution(self, *contribution):
        """Add Contribution to Plot. Can be single item or list."""
        self.contributions.extend(*contribution)

    def plot(self, draw_opts=None):
        """Make the plot.

        draw_opts: str. Same options as you would pass to Draw() in ROOT.
        """

        # First make a container
        if self.plot_what in ["graph", "both"]:
            self.container = ROOT.TMultiGraph()
        else:
            self.container = MultiFunc()

        # Now add all the contributions to the container, styling as we go
        if len(self.contributions) == 0:
            raise UnboundLocalError("contributions list is empty")

        for c in self.contributions:
            obj = c.get_obj().Clone()

            if self.plot_what == "graph":
                # if drawing only graph, we need to remove the fit if there is one
                obj.GetListOfFunctions().Remove(obj.GetListOfFunctions().At(0))
            else:
                # if drawing function, extend range as per user's request
                if self.do_extend:
                    if self.plot_what == 'function':
                        obj.SetRange(self.xlim[0], self.xlim[1])
                    elif self.plot_what == "both":
                        obj.GetListOfFunctions().At(0).SetRange(self.xlim[0], self.xlim[1])

            self.container.Add(obj)
            if self.do_legend:
                self.legend.AddEntry(obj, c.label, "LP")

        # Plot the container
        # need different default drawing options for TF1s vs TGraphs
        # (ALP won't actually display axis for TF1)
        if draw_opts is None:
            if self.plot_what in ["graph", 'both']:
                draw_opts = "ALP"
            elif self.plot_what in ['function']:
                draw_opts = ""

        # Need a canvas
        # If we have "SAME" hten we want to draw this Plot object
        # on the current canvas
        # Otherwise, we create a new one
        if "SAME" in draw_opts:
            self.canvas = ROOT.gPad
            self.canvas.cd()
            print "Using existing canvas", self.canvas.GetName()
        else:
            rand = random.randint(0, 100) # need a unique name
            self.canvas = ROOT.TCanvas("canv%s" % rand, "", 800, 600)
            self.canvas.SetTicks(1, 1)

        self.container.Draw(draw_opts)

        # Customise
        if self.plot_what != 'function':
            modifier = self.container
        else:
            modifier = self.container.Mod()

        modifier.SetTitle("%s;%s;%s" % (self.title, self.xtitle, self.ytitle))
        if self.xlim:
            modifier.GetXaxis().SetRangeUser(*self.xlim)
        if self.ylim:
            modifier.GetYaxis().SetRangeUser(*self.ylim)

        # Plot legend
        if self.do_legend:
            self.legend.Draw()

    def save(self, filename):
        """Save the plot to file. Do some check to make sure dir exists."""
        if not os.path.isdir(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        self.canvas.SaveAs(filename)


def compare():
    """Make all da plots"""

    # a set of 11 varying colours
    colors = [ROOT.kRed, ROOT.kBlue, ROOT.kBlack, ROOT.kGreen+2, ROOT.kMagenta,
              ROOT.kOrange+7, ROOT.kAzure+1, ROOT.kRed+3, ROOT.kViolet+1,
              ROOT.kOrange, ROOT.kTeal-5]

    d = "/users/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/"

    # Old spring 15 MC, had PU20
    f_jetSeed0_old = os.path.join(d, 'Stage1_QCDSpring15_AVE20BX25_stage1NoLut_rctv4_jetSeed0/ref14to1000_l10to1000_dr0p7/output_QCD_Pt-15to170_300to800_Spring15_AVE20BX25_Stage1_MCRUN2_74_V9_jetSeed0_noStage1Lut_rctv4_preGt_ak4_ref14to1000_l10to500_dr0p7.root')
    f_jetSeed5_old = os.path.join(d, "Stage1_QCDSpring15_AVE20BX25_stage1NoLut_rctv4_jetSeed5/new/ref14to1000_l10to500_dr0p7/output_QCD_Pt-15to170_300to1000_Spring15_AVE20BX25_Stage1_jetSeed5_MCRUN2_V9_noStage1Lut_rctv4_preGt_ak4_ref14to1000_l10to500_dr0p7.root")
    f_jetSeed10_old = os.path.join(d, "Stage1_QCDSpring15_AVE20BX25_stage1NoLut_rctv4_jetSeed10/output_QCD_Pt-15to1000_Spring15_AVE20BX25_Stage1_QCDSpring15_newRCTv2_preGt_ak4_ref14to1000_l10to500_fitMin20_HFfix_noGaussFitCheck.root")

    # New spring 15 MC, 0PU, various jet seeds
    # "New" = with HF fix
    f_jetSeed0_new_0PU = os.path.join(d, 'Stage1_QCDFlatSpring15BX25HCALFix_stage1NoLut_rctv4_jetSeed0_newPUSmc/output/output_QCDFlatSpring15BX25FlatNoPUHCALFix_Stage1_MCRUN2_74_V9_jetSeed0_noStage1Lut_newPUSmc_rctv4_preGt_ak4_ref14to1000_l10to500_dr0p7.root')
    f_jetSeed5_new_0PU = os.path.join(d, 'Stage1_QCDFlatSpring15BX25HCALFix_stage1NoLut_rctv4_jetSeed5_newPUSmc/output/output_QCDFlatSpring15BX25FlatNoPUHCALFix_Stage1_MCRUN2_74_V9_jetSeed5_noStage1Lut_newPUSmc_rctv4_preGt_ak4_ref14to1000_l10to500_dr0p7.root')

    # New spring 15 MC, jet seed0, binned by PU
    f_jetSeed0_new_PU0to10 = os.path.join(d, "Stage1_QCDFlatSpring15BX25HCALFix_stage1NoLut_rctv4_jetSeed0_newPUSmc/output/output_QCDFlatSpring15BX25PU10to30HCALFix_Stage1_MCRUN2_74_V9_jetSeed0_noStage1Lut_newPUSmc_rctv4_preGt_ak4_ref14to1000_l10to500_dr0p7_PU0to10.root")
    f_jetSeed0_new_PU15to25 = os.path.join(d, "Stage1_QCDFlatSpring15BX25HCALFix_stage1NoLut_rctv4_jetSeed0_newPUSmc/output/output_QCDFlatSpring15BX25PU10to30HCALFix_Stage1_MCRUN2_74_V9_jetSeed0_noStage1Lut_newPUSmc_rctv4_preGt_ak4_ref14to1000_l10to500_dr0p7_PU15to25.root")
    f_jetSeed0_new_PU30to40 = os.path.join(d, "Stage1_QCDFlatSpring15BX25HCALFix_stage1NoLut_rctv4_jetSeed0_newPUSmc/output/output_QCDFlatSpring15BX25PU10to30HCALFix_Stage1_MCRUN2_74_V9_jetSeed0_noStage1Lut_newPUSmc_rctv4_preGt_ak4_ref14to1000_l10to500_dr0p7_PU30to40.root")

    # New spring 15 MC, jet seed5, binned by PU
    f_jetSeed5_new_PU0to10 = os.path.join(d, "Stage1_QCDFlatSpring15BX25HCALFix_stage1NoLut_rctv4_jetSeed5_newPUSmc/output/output_QCDFlatSpring15BX25PU10to30HCALFix_Stage1_MCRUN2_74_V9_jetSeed5_noStage1Lut_newPUSmc_rctv4_preGt_ak4_ref14to1000_l10to500_dr0p7_PU0to10.root")
    f_jetSeed5_new_PU15to25 = os.path.join(d, "Stage1_QCDFlatSpring15BX25HCALFix_stage1NoLut_rctv4_jetSeed5_newPUSmc/output/output_QCDFlatSpring15BX25PU10to30HCALFix_Stage1_MCRUN2_74_V9_jetSeed5_noStage1Lut_newPUSmc_rctv4_preGt_ak4_ref14to1000_l10to500_dr0p7_PU15to25.root")
    f_jetSeed5_new_PU30to40 = os.path.join(d, "Stage1_QCDFlatSpring15BX25HCALFix_stage1NoLut_rctv4_jetSeed5_newPUSmc/output/output_QCDFlatSpring15BX25PU10to30HCALFix_Stage1_MCRUN2_74_V9_jetSeed5_noStage1Lut_newPUSmc_rctv4_preGt_ak4_ref14to1000_l10to500_dr0p7_PU30to40.root")

    # New Spring 15 MC, jet seed 5, old PUS table, binned by PU
    f_jetSeed5_new_PU0to10_oldPUS = os.path.join(d, "Stage1_QCDFlatSpring15BX25HCALFix_stage1NoLut_rctv4_jetSeed5/output/output_QCDFlatSpring15BX25PU10to30HCALFix_Stage1_MCRUN2_74_V9_jetSeed5_noStage1Lut_rctv4_preGt_ak4_ref14to1000_l10to500_dr0p7_PU0to10.root")
    f_jetSeed5_new_PU15to25_oldPUS = os.path.join(d, "Stage1_QCDFlatSpring15BX25HCALFix_stage1NoLut_rctv4_jetSeed5/output/output_QCDFlatSpring15BX25PU10to30HCALFix_Stage1_MCRUN2_74_V9_jetSeed5_noStage1Lut_rctv4_preGt_ak4_ref14to1000_l10to500_dr0p7_PU15to25.root")
    f_jetSeed5_new_PU30to40_oldPUS = os.path.join(d, "Stage1_QCDFlatSpring15BX25HCALFix_stage1NoLut_rctv4_jetSeed5/output/output_QCDFlatSpring15BX25PU10to30HCALFix_Stage1_MCRUN2_74_V9_jetSeed5_noStage1Lut_rctv4_preGt_ak4_ref14to1000_l10to500_dr0p7_PU30to40.root")

    # Loop over eta bins
    for i, (eta_min, eta_max) in enumerate(zip(binning.eta_bins[:-1], binning.eta_bins[1:])):

        # --------------------------------------------------------------------
        # Compare v2 and v3 corrections
        # --------------------------------------------------------------------
        graphs = [
            # Contribution(file_name=f_jetSeed5_old, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
            #             label="V2 (jet seed 5)", line_color=colors[3], marker_color=colors[3]),
            Contribution(file_name=f_jetSeed10_old, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                        label="V2 (jet seed 10)", line_color=colors[3], marker_color=colors[3]),
            Contribution(file_name=f_jetSeed5_new_PU15to25, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                        label="#splitline{V3 (jet seed 5,}{new PUS, HF fix)}", line_color=colors[1], marker_color=colors[1]),
        ]
        ylim = None
        if eta_min == 3.5 or eta_min == 4.5:
            ylim = [1., 2.8]
        p = Plot(contributions=graphs, what="graph", xtitle="<p_{T}^{L1}>", ytitle="Correction value (= 1/response)",
                 title="Spring15 MC + no JEC, 25ns, %g < |#eta| < %g" % (eta_min, eta_max), xlim=[0, 250], ylim=ylim)
        p.plot()
        oDir = "smallStudies/Spring15_compareV2_V3"
        p.save(os.path.join(oDir, "compare_V2_V3_eta_%g_%g.pdf" % (eta_min, eta_max)))

        graphs2 = [
            # Contribution(file_name=f_jetSeed5_old, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
            #             label="V2 (jet seed 5)", line_color=colors[3], marker_color=colors[3]),
            Contribution(file_name=f_jetSeed10_old, obj_name="fitfcneta_%g_%g" % (eta_min, eta_max),
                        label="V2 (jet seed 10)", line_color=colors[3], marker_color=colors[3]),
            Contribution(file_name=f_jetSeed5_new_PU15to25, obj_name="fitfcneta_%g_%g" % (eta_min, eta_max),
                        label="#splitline{V3 (jet seed 5,}{new PUS, HF fix)}", line_color=colors[1], marker_color=colors[1]),
        ]
        ylim = None
        if eta_min == 3.5 or eta_min == 4.5:
            ylim = [1., 2.8]
        p2 = Plot(contributions=graphs2, what="function", xtitle="<p_{T}^{L1}>", ytitle="Correction value (= 1/response)",
                  title="Spring15 MC + no JEC, 25ns, %g < |#eta| < %g" % (eta_min, eta_max), xlim=[0, 250], ylim=ylim, extend=True)
        p2.plot("SAME")
        p.container.GetHistogram().GetXaxis().SetRangeUser(0, 250)
        oDir = "smallStudies/Spring15_compareV2_V3"
        p2.save(os.path.join(oDir, "compare_V2_V3_eta_%g_%g_both.pdf" % (eta_min, eta_max)))

"""
        # --------------------------------------------------------------------
        # Compare 0, 5, 10 jet seeds (original Spring15 MC)
        # --------------------------------------------------------------------
        graphs = [
            Contribution(file_name=f_jetSeed0_old, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="seed 0", line_color=colors[0], marker_color=colors[0]),
            Contribution(file_name=f_jetSeed5_old, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="seed 5", line_color=colors[1], marker_color=colors[1]),
            Contribution(file_name=f_jetSeed10_old, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="seed 10", line_color=colors[2], marker_color=colors[2])
        ]
        p = Plot(contributions=graphs, what="both", xtitle="<p_{T}^{L1}>", ytitle="Correction value (= 1/response)",
                 title="Original Spring15 MC + no JEC, 25ns, PU20, %g < |#eta| < %g" % (eta_min, eta_max), xlim=[0, 250])
        p.plot()
        oDir = "smallStudies/Spring15_compareSeeds"
        p.save(os.path.join(oDir, "compare_0_5_10_seeds_eta_%g_%g.pdf" % (eta_min, eta_max)))

        # Add the fit functions on top
        graphs2 = [
            Contribution(file_name=f_jetSeed0_old, obj_name="fitfcneta_%g_%g" % (eta_min, eta_max),
                                     label="seed 0", line_color=colors[0], marker_color=colors[0], line_width=2, line_style=2),
            Contribution(file_name=f_jetSeed5_old, obj_name="fitfcneta_%g_%g" % (eta_min, eta_max),
                                     label="seed 5", line_color=colors[1], marker_color=colors[1], line_width=2, line_style=2),
            Contribution(file_name=f_jetSeed10_old, obj_name="fitfcneta_%g_%g" % (eta_min, eta_max),
                                     label="seed 10", line_color=colors[2], marker_color=colors[2], line_width=2, line_style=2)
        ]

        p2 = Plot(contributions=graphs2, what="function", xtitle="<p_{T}^{L1}>", ytitle="Correction value (= 1/response)",
                 title="Original Spring15 MC + no JEC, 25ns, PU20, %g < |#eta| < %g" % (eta_min, eta_max), xlim=[0, 250], extend=True)
        p2.plot(draw_opts="SAME")
        oDir = "smallStudies/Spring15_compareSeeds"
        p2.save(os.path.join(oDir, "compare_0_5_10_seeds_eta_%g_%g_both.pdf" % (eta_min, eta_max)))


        # --------------------------------------------------------------------
        # Compare diff PU scenarios for new MC
        # --------------------------------------------------------------------
        # no JEC, seed 0
        ylim = None
        if eta_min > 4.4:
            ylim = [1.2, 3]
        elif eta_min > 3.9:
            ylim = [1.2, 2.6]
        graphs = [
            Contribution(file_name=f_jetSeed0_new_0PU, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 0", line_color=colors[0], marker_color=colors[0]),
            Contribution(file_name=f_jetSeed0_new_PU0to10, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 0 - 10", line_color=colors[1], marker_color=colors[1]),
            Contribution(file_name=f_jetSeed0_new_PU15to25, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 15 - 25", line_color=colors[2], marker_color=colors[2]),
            Contribution(file_name=f_jetSeed0_new_PU30to40, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 30 - 40", line_color=colors[3], marker_color=colors[3])
        ]
        p = Plot(contributions=graphs, what="both", xtitle="<p_{T}^{L1}>", ytitle="Correction value (= 1/response)",
                 title="Spring15 MC + HF fix + no JEC, jet seed 0 GeV, %g < |#eta| < %g" % (eta_min, eta_max),
                 ylim=ylim)
        p.plot()
        oDir = "smallStudies/Spring15_HFfix_pu_binning_jetSeed0"
        p.save(os.path.join(oDir, "compare_PU_eta_%g_%g.pdf" % (eta_min, eta_max)))

        # no JEC, seed 5
        ylim = None
        if eta_min > 4.4:
            ylim = [1.2, 2.6]
        elif eta_min > 3.9:
            ylim = [1.2, 2]

        graphs = [
            Contribution(file_name=f_jetSeed5_new_0PU, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="0PU", line_color=colors[0], marker_color=colors[0]),
            Contribution(file_name=f_jetSeed5_new_PU0to10, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 0 - 10", line_color=colors[1], marker_color=colors[1]),
            Contribution(file_name=f_jetSeed5_new_PU15to25, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 15 - 25", line_color=colors[2], marker_color=colors[2]),
            Contribution(file_name=f_jetSeed5_new_PU30to40, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="PU: 30 - 40", line_color=colors[3], marker_color=colors[3])
        ]
        p = Plot(contributions=graphs, what="both", xtitle="<p_{T}^{L1}>", ytitle="Correction value (= 1/response)",
                 title="Spring15 MC + HF fix + no JEC, jet seed 5 GeV, %g < |#eta| < %g" % (eta_min, eta_max),
                 ylim=ylim)
        p.plot()
        oDir = "smallStudies/Spring15_HFfix_pu_binning_jetSeed5"
        p.save(os.path.join(oDir, "compare_PU_eta_%g_%g.pdf" % (eta_min, eta_max)))

        # JECv2 set seed 0

        # JECv2 set seed 5


        # --------------------------------------------------------------------
        # Compare old/new PUS table for HF fix MC
        # --------------------------------------------------------------------
        graphs = [
            Contribution(file_name=f_jetSeed5_new_PU15to25_oldPUS, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="Spring15 MC + HF fix, old PUS, PU: 15-25", line_color=colors[3], marker_color=colors[3]),
            Contribution(file_name=f_jetSeed5_new_PU15to25, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="Spring15 MC + HF fix, new PUS, PU: 15-25", line_color=colors[4], marker_color=colors[4])
        ]
        ylim = None
        if eta_min > 4.4:
            ylim = [1.2, 2.6]
        elif eta_min > 3.9:
            ylim = [1.2, 2]
        p = Plot(contributions=graphs, what="both", xtitle="<p_{T}^{L1}>", ytitle="Correction value (= 1/response)",
                 title="No JEC, 25ns, jet seed 5, %g < |#eta| < %g" % (eta_min, eta_max), ylim=ylim)
        p.legend.SetX1(0.5)
        p.legend.SetY1(0.6)
        p.plot()
        oDir = "smallStudies/Spring15_HFfix_comparePUS_jetSeed5"
        p.save(os.path.join(oDir, "compare_old_new_PUS_seed5_eta_%g_%g.pdf" % (eta_min, eta_max)))


        # --------------------------------------------------------------------
        # Compare old vs new Spring15 MC
        # --------------------------------------------------------------------
        # jet seed 5
        graphs = [
            Contribution(file_name=f_jetSeed5_old, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="Original Spring15 MC, PU20", line_color=colors[1], marker_color=colors[1]),
            Contribution(file_name=f_jetSeed5_new_PU15to25, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="With HF fix, PU 15-25", line_color=colors[2], marker_color=colors[2])
        ]
        ylim = None
        if eta_min > 4.4:
            ylim = [1.2, 2.6]
        elif eta_min > 3.9:
            ylim = [1.2, 2]
        p = Plot(contributions=graphs, what="both", xtitle="<p_{T}^{L1}>", ytitle="Correction value (= 1/response)",
                 title="No JEC, 25ns, jet seed 5, %g < |#eta| < %g" % (eta_min, eta_max), ylim=ylim)
        p.legend.SetX1(0.5)
        p.legend.SetY1(0.6)
        p.plot()
        oDir = "smallStudies/Spring15_compareOldVsNew_jetSeed5"
        p.save(os.path.join(oDir, "compare_old_new_seed5_eta_%g_%g.pdf" % (eta_min, eta_max)))

        # jet seed 0
        graphs = [
            Contribution(file_name=f_jetSeed0_old, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="Original Spring15 MC, PU20", line_color=colors[1], marker_color=colors[1]),
            Contribution(file_name=f_jetSeed0_new_PU15to25, obj_name="l1corr_eta_%g_%g" % (eta_min, eta_max),
                         label="With HF fix, PU 15-25", line_color=colors[2], marker_color=colors[2])
        ]
        p = Plot(contributions=graphs, what="both", xtitle="<p_{T}^{L1}>", ytitle="Correction value (= 1/response)",
                 title="No JEC, 25ns, jet seed 0, %g < |#eta| < %g" % (eta_min, eta_max))
        p.legend.SetX1(0.5)
        p.legend.SetY1(0.6)
        p.plot()
        oDir = "smallStudies/Spring15_compareOldVsNew_jetSeed0"
        p.save(os.path.join(oDir, "compare_old_new_seed0_eta_%g_%g.pdf" % (eta_min, eta_max)))
"""

if __name__ == "__main__":
    compare()