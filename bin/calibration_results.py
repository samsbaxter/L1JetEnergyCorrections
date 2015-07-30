#!/usr/bin/env python
"""
This script outputs all the calibration plots in the ROOT file as one long pdf,
cos TBrowser sucks.
"""

import ROOT as r
import sys
import os
import numpy
import argparse
import numpy
from itertools import izip
import subprocess
import binning
import beamer_slide_templates as bst


r.PyConfig.IgnoreCommandLineOptions = True
r.gROOT.SetBatch(1)

etaBins = binning.eta_bins


def open_root_file(filename):
    """
    Safe way to open ROOT file. Could be improved.
    """
    f = r.TFile(filename)
    if f.IsZombie():
        raise RuntimeError("Can't open file %s" % filename)
    return f


def check_dir_exists(d):
    """
    Check directory exists. If not, make it.
    """
    opath = os.path.abspath(d)
    if not os.path.isdir(opath):
        os.makedirs(opath)


def plot_to_file(f, plotname, filename, xtitle="", ytitle="", title="", drawopts="", drawfit=True, extend_fit=True):
    """
    f is a TFile
    filename is output, can be a list of filenames (e.g. for .tex, .pdf, .png)
    can optionally not draw the fit to the curve
    """
    r.gStyle.SetPaperSize(10.,10.)
    r.gStyle.SetOptStat("mre")
    r.gStyle.SetOptFit(0101) # MAGIC COMBO FOR PARAMS+ERRORS - ignore the ROOT docs
    # p = r.TGraphErrors(f.Get(plotname).Clone())
    print plotname
    obj = f.Get(plotname)
    obj2 = f.Get(plotname+"_fit")
    if not obj or (drawfit and not obj2):
        print "Can't find", obj
        return False
    else:
        p = obj.Clone()
        p2 = obj2.Clone()
        p.GetYaxis().SetTitle(ytitle)
        p2.GetYaxis().SetTitle(ytitle)
        p.GetXaxis().SetTitle(xtitle)
        p2.GetXaxis().SetTitle(xtitle)
        p.SetTitle(title)
        p2.SetTitle(title)
        if not drawfit:
            p2.GetListOfFunctions().Remove(p.GetListOfFunctions().At(0))
        else:
            fn = p2.GetListOfFunctions().At(0)
            fn.SetLineWidth(2)
        p.Draw(drawopts)
        p2.Draw(drawopts+"SAME")
        # draw fit over full range, not just fitted range
        if drawfit and extend_fit:
            fn = p2.GetListOfFunctions().At(0)
            fn2 = fn.Clone()
            fn2.SetRange(0,250)
            fn2.SetLineStyle(3)
            fn2.SetLineWidth(2)
            fn2.Draw("SAME")
        p.Draw(drawopts+"SAME")
        r.gPad.Update()

        # Draw fit stats box
        st = p2.FindObject("stats")
        st.SetFillStyle(0)
        st.SetX1NDC(0.6)
        st.SetX2NDC(0.9)
        st.SetY1NDC(0.55)
        st.SetY2NDC(0.9)
        for f in filename:
            r.gPad.Print(f)
        r.gPad.Clear()
        return True


def plot_corr_results(in_name=""):
    """
    Puts correction plots in one pdf.
    """
    # Setup input file
    print "Opening", in_name
    in_stem = os.path.basename(in_name).replace(".root", "")
    input_file = open_root_file(in_name)

    # Setup output directory & filenames
    odir = os.path.dirname(os.path.abspath(in_name))+"/"+in_stem+"/"
    check_dir_exists(odir)

    out_name = odir+in_stem+".pdf"
    out_stem = out_name.replace(".pdf","")
    print "Writing to", out_name

    # Start beamer file
    # Use template - change title, subtitle, include file
    title = "Correction value plots, binned by $|\eta|$"
    sub = in_stem.replace("output_", "").replace("_", "\_")
    sub = sub.replace("_ak", r"\\_ak")
    subtitle = "{\\tt " + sub +"}"
    slides_file = out_stem+"_slides.tex"
    main_file = out_stem+".tex"
    with open("beamer_template.tex", "r") as t:
        with open(main_file, "w") as f:
            substitute = {"@TITLE": title, "@SUBTITLE": subtitle,
                          "@FILE": slides_file}
            for line in t:
                for k in substitute:
                    if k in line:
                        line = line.replace(k, substitute[k])
                f.write(line)

    # Now make the slides file
    with open(slides_file, "w") as slides:
        titles = []
        plotnames = []
        for i, eta in enumerate(etaBins[0:-1]):
            emin = eta
            emax = etaBins[i+1]
            name = "l1corr_eta_%g_%g" % (emin, emax)
            bin_title = "%g <  |\eta^{L1}| < %g" % (emin, emax)
            if plot_to_file(input_file,
                        name,
                        [odir+name+".tex", odir+name+".pdf"],
                        xtitle="<p_{T}^{L1}> [GeV]",
                        ytitle="1/< p_{T}^{L1}/p_{T}^{Ref} > = correction\ value",
                        title="",
                        drawfit=True,
                        extend_fit=True):
                titles.append("$%s$" % bin_title)
                plotnames.append(odir+name+".tex")
            print i
            print titles
            print plotnames
            if (((i+1) % 4 == 0) and (i != 0)) or (i == len(etaBins)-2):
                print "Writing", emin, emax
                # slidetitle = "Correction value, $0 < p_{T}^{L1} < 500~\\mathrm{GeV}$, $14 < p_{T}^{Gen} < 500~\\mathrm{GeV}$"
                # slidetitle = "Correction value, $0 < p_{T}^{L1} < 250~\\mathrm{GeV}$, $14 < p_{T}^{Gen} < 250~\\mathrm{GeV}$"
                slidetitle = "Correction value"
                slides.write(bst.make_slide(bst.four_plot_slide, titles, plotnames, slidetitle))
                titles = []
                plotnames = []

    compile_pdf(main_file, out_name, odir)


def plot_bin_results(in_name=""):
    """
    To plot X for each pt/eta bin.
    Yes that's a lot of plots.
    """
    # Setup input file
    print "Opening", in_name
    in_stem = os.path.basename(in_name).replace(".root", "")
    input_file = open_root_file(in_name)

    # Setup output directory & filenames
    odir = os.path.dirname(os.path.abspath(in_name))+"/"+in_stem+"/"
    check_dir_exists(odir)

    # only have to change output name here - reflected automatically in tex files etc
    out_name = odir+in_stem+"_bin.pdf"
    out_stem = out_name.replace(".pdf","")
    print "Writing to", out_name

    # Start beamer file
    # Use template - change title, subtitle, include file
    title = "Results for each bin"
    sub = in_stem.replace("output_", "")
    sub = sub.replace("_", "\_")
    sub = sub.replace("_ak", r"\\_ak")
    subtitle = "{\\tt " + sub +"}"
    slides_file = out_stem+"_slides.tex"
    main_file = out_stem+".tex"
    with open("beamer_template.tex", "r") as t:
        with open(main_file, "w") as f:
            substitute = {"@TITLE": title, "@SUBTITLE": subtitle,
                          "@FILE": slides_file}
            for line in t:
                for k in substitute:
                    if k in line:
                        line = line.replace(k, substitute[k])
                f.write(line)

    # Now make the slides file
    with open(slides_file, "w") as slides:
        for i, eta in enumerate(etaBins[0:-1]):
            emin = eta
            emax = etaBins[i+1]
            titles = []
            plotnames = []
            out_dir_eta = odir+"/eta_%g_%g/" % (emin, emax)
            check_dir_exists(out_dir_eta)
            ptBins = binning.pt_bins if emin < 3 else binning.pt_bins_wide
            for j, pt in enumerate(ptBins[:-1]):
                ptmin = pt
                ptmax = ptBins[j+1]
                # for each pt bin we have a L1 pt plot, and a response plot w/fit
                l1name = "L1_pt_genpt_%g_%g" % (ptmin, ptmax)
                if plot_to_file(input_file,
                                "eta_%g_%g/Histograms/%s" % (emin, emax, l1name),
                                [out_dir_eta+l1name+".tex", out_dir_eta+l1name+".pdf"],
                                xtitle="p_{T}^{L1}", ytitle="", drawfit=True):
                    plotnames.append(out_dir_eta+l1name+".tex")

                rspname = "Rsp_genpt_%g_%g" % (ptmin, ptmax)
                if plot_to_file(input_file,
                                "eta_%g_%g/Histograms/%s" % (emin, emax, rspname),
                                [out_dir_eta+rspname+".tex", out_dir_eta+rspname+".pdf"],
                                xtitle="response = p_{T}^{L1}/p_{T}^{Gen}", ytitle="", drawfit=True):
                    plotnames.append(out_dir_eta+rspname+".tex")

                    titles.append("$%g < |p_{T}^{Gen}| < %g GeV$" % (ptmin, ptmax))
                    titles.append("")

                if (len(plotnames) == 4):
                    print "Writing", emin, emax, ptmin, ptmax
                    slidetitle = "$%g <  |\eta| < %g$" % (emin, emax)
                    slides.write(bst.make_slide(bst.four_plot_slide, titles, plotnames, slidetitle))
                    titles = []
                    plotnames = []

    # compile_pdf(main_file, out_name, odir)


def compile_pdf(texfile, pdffile, outdir):
    """
    Compile the pdf
    Use lualatex for custom font. Do it twice to get TOC and page num right
    """

    output = "-output-directory=%s" % outdir
    subprocess.call(["lualatex", "-interaction", "nonstopmode", output, texfile])
    subprocess.call(["lualatex", "-interaction", "nonstopmode", output, texfile])
    # subprocess.call(["lualatex", output, texfile])
    # subprocess.call(["lualatex", output, texfile])
    # Open the result
    subprocess.call(["open", pdffile])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="input ROOT filename")
    parser.add_argument("--detail", action="store_true", help="do all pt bin plots as well (takes much longer!)")
    args = parser.parse_args()

    # Plot for each eta bin
    plot_corr_results(in_name=args.input)

    # Plots for each pt bin in every eta bin (ie A LOT)
    if args.detail:
        plot_bin_results(in_name=args.input)