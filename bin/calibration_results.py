"""
This script outputs all the plots in the ROOT file as one long pdf,
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

r.gROOT.SetBatch(1)
# ptBins = list(numpy.concatenate((numpy.array([14, 18, 22, 24]), numpy.arange(28, 252, 4)))) # slightly odd binning here - why?
ptBins = list(numpy.arange(14, 254, 4))
etaBins = [0.0, 0.348, 0.695, 1.044, 1.392, 1.74, 2.172, 3.0, 3.5, 4.0, 4.5, 5.001]

                # \includegraphics[width=0.85\textwidth]{@PLOT1}
four_plot_slide = \
r"""
\section{@SLIDE_TITLE}
\begin{frame}{@SLIDE_TITLE}
\vspace{-.3cm}
\begin{columns}
\begin{column}{0.5\textwidth}
\begin{center}
@PLOT1TITLE
\\
\scalebox{0.5}{\input{@PLOT1}}
\\
@PLOT3TITLE
\\
\scalebox{0.5}{\input{@PLOT3}}
\end{center}
\end{column}

\begin{column}{0.5\textwidth}
\begin{center}
@PLOT2TITLE
\\
\scalebox{0.5}{\input{@PLOT2}}
\\
@PLOT4TITLE
\\
\scalebox{0.5}{\input{@PLOT4}}
\end{center}
\end{column}
\end{columns}
\end{frame}
"""


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


def make_four_slide(titles, plotnames, slidetitle="Correction values"):
    """
    Auto makes a slide with up to 4 figures with corresponding titles
    """
    print "make 4 slide"
    slide = four_plot_slide.replace("@SLIDE_TITLE", slidetitle)
    for i, item in enumerate(izip(titles, plotnames)):
            slide = slide.replace("@PLOT"+str(i+1)+"TITLE", item[0])
            slide = slide.replace("@PLOT"+str(i+1), item[1])
    for i in range(len(titles),5):
        slide = slide.replace("@PLOT"+str(i+1)+"TITLE", "")
        slide = slide.replace("\scalebox{0.5}{\input{@PLOT"+str(i+1)+"}}", "") # to avoid "missing .tex file" error
        slide = slide.replace("\\\\\n\n","")  # remove usless line breaks
    slide = slide.replace("\n\n\\\\", "\\\\")
    return slide


def plot_to_file(f, plotname, filename, xtitle="", ytitle="", drawfit=True, drawopts=""):
    """
    f is a TFile
    filename is output, can be a list of filenames (e.g. for .tex, .pdf, .png)
    can optionally not draw the fit to the curve
    """
    r.gStyle.SetPaperSize(10.,10.)
    r.gStyle.SetOptStat("mre")
    # p = r.TGraphErrors(f.Get(plotname).Clone())
    print plotname
    p = (f.Get(plotname).Clone())
    p.GetYaxis().SetTitle(ytitle)
    p.GetXaxis().SetTitle(xtitle)
    p.SetTitle("")
    # p.SetMaximum(1.5)
    # p.SetMinimum(0)
    # if p.GetMaximum() > 5:
    #     p.SetMaximum(5)
    # # if p.GetMinimum() < 5:
    #     # p.SetMinimum(-5)
    if not drawfit:
        p.GetListOfFunctions().Remove(p.GetListOfFunctions().At(0))
    p.Draw(drawopts)
    for f in filename:
        r.gPad.Print(f)
    r.gPad.Clear()


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
    subtitle = "{\\tt " + sub +"}"
    # subtitle = "For Stage 1 + new RCT calibs"
    # subtitle = "For GCT with fit 30 - 250 GeV"
    # subtitle += "\\\ {\\tt /RelValQCD_FlatPt_15_3000HS_13/CMSSW_7_3_0-MCRUN2_73_V7-v1/GEN-SIM-DIGI-RAW-HLTDEBUG}"
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
            plot_to_file(input_file, "l1corr_eta_%g_%g" % (emin, emax), [odir+name+".tex", odir+name+".pdf"], xtitile="<p_{T}^{L1}> [GeV]", ytitle="1/< p_{T}^{L1}/p_{T}^{Ref} >", drawfit=True)
            titles.append("$%g <  |\eta| < %g$" % (emin, emax))
            plotnames.append(odir+name+".tex")
            print i
            print titles
            print plotnames
            if (((i+1) % 4 == 0) and (i != 0)) or (i == len(etaBins)-2):
                print "Writing", emin, emax
                slidetitle = "Correction value, $0 < p_{T}^{L1} < 500~\\mathrm{GeV}$, $14 < p_{T}^{Gen} < 500~\\mathrm{GeV}$"
                # slidetitle = "Correction value, $0 < p_{T}^{L1} < 250~\\mathrm{GeV}$, $14 < p_{T}^{Gen} < 250~\\mathrm{GeV}$"
                # slidetitle = "Correction value"
                slides.write(make_four_slide(titles, plotnames, slidetitle))
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
            for j, pt in enumerate(ptBins[0:-1]):
                ptmin = pt
                ptmax = ptBins[j+1]
                # for each pt bin we have a L1 pt plot, and a response plot w/fit
                l1name = "L1_pt_genpt_%g_%g" % (ptmin, ptmax)
                # plot_to_file(input_file, "eta_%g_%g/Histograms/%s" % (emin, emax, l1name), [out_dir_eta+l1name+".tex", out_dir_eta+l1name+".pdf"], xtitle="p_{T}^{L1}", ytitle="", drawfit=True)
                plotnames.append(out_dir_eta+l1name+".tex")

                rspname = "Rsp_genpt_%g_%g" % (ptmin, ptmax)
                # plot_to_file(input_file, "eta_%g_%g/Histograms/%s" % (emin, emax, rspname), [out_dir_eta+rspname+".tex", out_dir_eta+rspname+".pdf"], xtitle="response = p_{T}^{L1}/p_{T}^{Gen}", ytitle="", drawfit=True)
                plotnames.append(out_dir_eta+rspname+".tex")

                titles.append("$%g < |p_{T}^{Gen}| < %g GeV$" % (ptmin, ptmax))
                titles.append("")

                if (len(plotnames) == 4):
                    print "Writing", emin, emax, ptmin, ptmax
                    slidetitle = "$%g <  |\eta| < %g$" % (emin, emax)
                    slides.write(make_four_slide(titles, plotnames, slidetitle))
                    titles = []
                    plotnames = []

    compile_pdf(main_file, out_name, odir)


def compile_pdf(texfile, pdffile, outdir):
    """
    Compile the pdf
    Use lualatex for custom font. Do it twice to get TOC and page num right
    """

    output = "-output-directory=%s" % outdir
    # subprocess.call(["lualatex", "-interaction", "nonstopmode", output, out_stem+".tex"])
    # subprocess.call(["lualatex", "-interaction", "nonstopmode", output, out_stem+".tex"])
    subprocess.call(["lualatex", output, texfile])
    # subprocess.call(["lualatex", output, texfile])
    # Open the result
    subprocess.call(["open", pdffile])


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input ROOT filename")
    args = parser.parse_args()

    # plot_corr_results(in_name=args.input)
    plot_bin_results(in_name=args.input)
