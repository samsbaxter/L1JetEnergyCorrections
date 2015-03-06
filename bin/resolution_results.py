"""
This script outputs all the resolution plots in the ROOT file as one long pdf,
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


# ptBins = list(numpy.concatenate((numpy.array([14, 18, 22, 24]), numpy.arange(28, 252, 4)))) # slightly odd binning here - why?
ptBins = binning.pt_bins
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


def plot_to_file(f, plotname, filename, xtitle="", ytitle="", xlim=None, ylim=None, drawfit=True, drawopts="", col=""):
    """
    Save plot to file (tex, png, pdf...)
    f is a TFile
    plotname is the name of the plot in the file (incl. any directories)
    filename is output, can be a list of filenames (e.g. for .tex, .pdf, .png)
    Can optionally not draw the fit to the curve
    Can also provide draw options, and axis titles and limits (each as pair of values)
    """
    r.gStyle.SetPaperSize(10.,10.)
    r.gStyle.SetOptStat("mre")
    r.gStyle.SetOptFit(1111)

    plt = (f.Get(plotname).Clone())
    plt.GetXaxis().SetTitle(xtitle)
    plt.GetXaxis().SetTitleSize(0.06)
    plt.GetXaxis().SetLabelSize(0.06)
    plt.GetYaxis().SetTitle(ytitle)
    plt.GetYaxis().SetTitleSize(0.06)
    plt.GetYaxis().SetLabelSize(0.06)
    plt.SetTitle("")
    if xlim:
        plt.GetXaxis().SetRangeUser(xlim[0], xlim[1])
    if ylim:
        plt.SetMaximum(ylim[1])
        plt.SetMinimum(ylim[0])
    if col != "":
        plt.SetLineColor(col)
        plt.SetMarkerColor(col)
        plt.SetFillColor(col)
    # if plt.GetMaximum() > 5:
    #     plt.SetMaximum(5)
    # # if plt.GetMinimum() < 5:
    #     # plt.SetMinimum(-5)
    # if not drawfit:
    #     r.gStyle.SetOptFit(0)
    #     plt.GetListOfFunctions().Remove(plt.GetListOfFunctions().At(0))
    plt.Draw(drawopts)
    for f in filename:
        r.gPad.Print(f)
    r.gPad.Clear()


def plot_res_results(in_name=""):
    """
    Puts resolution plots in one pdf. Only for one file.
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
    title = "Resolution plots, binned by $|\eta|$"
    sub = in_stem.replace("res_", "").replace("_", "\_")
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
        # Do the L1 resolution plot alongside its corresponding genjet resolution plot
        for i, eta in enumerate(etaBins[0:-1]):
            emin = eta
            emax = etaBins[i+1]

            name = "resL1_%g_%g" % (emin, emax)
            plot_to_file(f=input_file, plotname="eta_%g_%g/" %(emin, emax)+name, filename=[odir+name+".tex", odir+name+".pdf"],
                xtitle="p_{T}^{L1} [GeV]", ytitle="(p_{T}^{L1} - p_{T}^{Gen})/ p_{T}^{L1}", ylim=[0, 0.9], drawfit=True, drawopts="ALP")
            titles.append("$%g <  |\eta^{L1}| < %g$" % (emin, emax))
            plotnames.append(odir+name+".tex")

            name = "resRef_%g_%g" % (emin, emax)
            plot_to_file(f=input_file, plotname="eta_%g_%g/" %(emin, emax)+name, filename=[odir+name+".tex", odir+name+".pdf"],
                xtitle="p_{T}^{L1} [GeV]", ytitle="(p_{T}^{L1} - p_{T}^{Gen})/ p_{T}^{Gen}", ylim=[0, 0.25], drawfit=True, drawopts="ALP")
            titles.append("$%g <  |\eta^{L1}| < %g$" % (emin, emax))
            plotnames.append(odir+name+".tex")

            # print i
            print titles
            print plotnames
            if (len(plotnames) == 4) or (i == len(etaBins)-2):
                print "Writing", emin, emax
                slidetitle = "Resolution (L1 \\& GenJet)"
                slides.write(bst.make_slide(bst.four_plot_slide, titles, plotnames, slidetitle))
                titles = []
                plotnames = []

    compile_pdf(main_file, out_name, odir)


def plot_res_compare(in_name_pre="", in_name_post=""):
    """For when you want to plot the pre and post calibrated versions on the same canvas"""
    # Setup input file (pre calib)
    print "Opening", in_name_pre
    in_stem_pre = os.path.basename(in_name_pre).replace(".root", "")
    input_file_pre = open_root_file(in_name_pre)

    # Setup input file (post calib)
    print "Opening", in_name_post
    in_stem_post = os.path.basename(in_name_post).replace(".root", "")
    input_file_post = open_root_file(in_name_post)

    # Setup output directory & filenames
    odir = os.path.dirname(os.path.abspath(in_name_pre))+"/"+in_stem_pre+"_compare/"
    check_dir_exists(odir)

    out_name = odir+in_stem_pre+"_compare.pdf"
    out_stem = out_name.replace(".pdf","")
    print "Writing to", out_name

    # Start beamer file
    # Use template - change title, subtitle, include file
    title = "Resolution plots, binned by $|\eta|$,\\\\comparing pre- and post- calibration"
    sub = in_stem_pre.replace("res_", "").replace("_", "\_")
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
        # Do the L1 resolution plot alongside its corresponding genjet resolution plot
        for i, eta in enumerate(etaBins[0:-1]):
            emin = eta
            emax = etaBins[i+1]

            name = "resL1_%g_%g" % (emin, emax)
            plot_to_file(f=input_file, plotname="eta_%g_%g/" %(emin, emax)+name, filename=[odir+name+".tex", odir+name+".pdf"],
                xtitle="p_{T}^{L1} [GeV]", ytitle="(p_{T}^{L1} - p_{T}^{Gen})/ p_{T}^{L1}", ylim=[0, 0.9], drawfit=True, drawopts="ALP")
            titles.append("$%g <  |\eta^{L1}| < %g$" % (emin, emax))
            plotnames.append(odir+name+".tex")

            name = "resRef_%g_%g" % (emin, emax)
            plot_to_file(f=input_file, plotname="eta_%g_%g/" %(emin, emax)+name, filename=[odir+name+".tex", odir+name+".pdf"],
                xtitle="p_{T}^{L1} [GeV]", ytitle="(p_{T}^{L1} - p_{T}^{Gen})/ p_{T}^{Gen}", ylim=[0, 0.25], drawfit=True, drawopts="ALP")
            titles.append("$%g <  |\eta^{L1}| < %g$" % (emin, emax))
            plotnames.append(odir+name+".tex")

            # print i
            print titles
            print plotnames
            if (len(plotnames) == 4) or (i == len(etaBins)-2):
                print "Writing", emin, emax
                slidetitle = "Resolution (L1 \\& GenJet)"
                slides.write(bst.make_slide(bst.four_plot_slide, titles, plotnames, slidetitle))
                titles = []
                plotnames = []

    compile_pdf(main_file, out_name, odir)

# TODO
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
            if emin >= 3.:
                ptBins = binning.pt_bins_wide
            for j, pt in enumerate(ptBins[0:-1]):
                ptmin = pt
                ptmax = ptBins[j+1]
                # for each pt bin we have a L1 pt plot, and a response plot w/fit
                l1name = "L1_pt_genpt_%g_%g" % (ptmin, ptmax)
                plot_to_file(input_file, "eta_%g_%g/Histograms/%s" % (emin, emax, l1name), [out_dir_eta+l1name+".tex", out_dir_eta+l1name+".pdf"], xtitle="p_{T}^{L1}", ytitle="", drawfit=True)
                plotnames.append(out_dir_eta+l1name+".tex")

                rspname = "Rsp_genpt_%g_%g" % (ptmin, ptmax)
                plot_to_file(input_file, "eta_%g_%g/Histograms/%s" % (emin, emax, rspname), [out_dir_eta+rspname+".tex", out_dir_eta+rspname+".pdf"], xtitle="response = p_{T}^{L1}/p_{T}^{Gen}", ytitle="", drawfit=True)
                plotnames.append(out_dir_eta+rspname+".tex")

                titles.append("$%g < |p_{T}^{Gen}| < %g GeV$" % (ptmin, ptmax))
                titles.append("")

                if (len(plotnames) == 4):
                    print "Writing", emin, emax, ptmin, ptmax
                    slidetitle = "$%g <  |\eta| < %g$" % (emin, emax)
                    slides.write(bst.make_slide(bst.four_plot_slide, titles, plotnames, slidetitle))
                    titles = []
                    plotnames = []

    compile_pdf(main_file, out_name, odir)


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

    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input ROOT filename")
    parser.add_argument("--detail", action="store_true", help="do all pt bin plots as well (takes much longer!)")
    # parser.add_argument("--compare", help="filename to compare <input> to (e.g post-calibration)")
    args = parser.parse_args()

    # Plot result for each eta bin & overall
    plot_res_results(in_name=args.input)

    # Plot each pt bin in every eta bin (i.e. A LOT)
    if args.detail:
        plot_bin_results(in_name=args.input)
