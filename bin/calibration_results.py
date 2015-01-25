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
    return slide


def plot_to_tex(f, plotname, texname):
    """
    f is a TFile
    """
    r.gStyle.SetPaperSize(10.,10.)
    p = f.Get(plotname)
    # p.Draw()
    p.SetMaximum(1.2)
    p.SetMinimum(0.3)
    p.Draw()
    r.gPad.Print(texname)
    r.gPad.Clear()


def plot_to_pdf(f, plotname, pdfname):
    """
    f is a TFile
    """
    r.gStyle.SetPaperSize(10.,10.)
    p = f.Get(plotname)
    p.Draw()
    r.gPad.SaveAs(pdfname)
    r.gPad.Clear()


def plot_corr_results(in_name=""):
    """
    Puts corrections in one pdf.
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
    subtitle = "For Stage 1 + new RCT calibs"
    slides_file = out_stem+"_slides.tex"
    with open("beamer_template.tex", "r") as t:
        with open(out_stem+".tex", "w") as f:
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
            plot_to_tex(input_file, "l1corr_eta_%g_%g" % (emin, emax), odir+name+".tex")
            plot_to_pdf(input_file, "l1corr_eta_%g_%g" % (emin, emax), odir+name+".pdf")
            titles.append("$%g <  |\eta| < %g$" % (emin, emax))
            plotnames.append(odir+name+".tex")
            print i
            print titles
            print plotnames
            if (((i+1) % 4 == 0) and (i != 0)) or (i == len(etaBins)-2):
                print "Writing", emin, emax
                slidetitle = "Correction value, $0 < p_{T}^{L1} < 500~\\textrm{GeV}$, $14 < p_{T}^{Gen} < 500~\\textrm{GeV}$"
                slidetitle = "Correction value"
                slides.write(make_four_slide(titles, plotnames, slidetitle))
                titles = []
                plotnames = []

    # Now compile
    # Now make the pdf
    # Use lualatex for custom font
    # Do it twice to get TOC and page num right
    output = "-output-directory=%s" % odir
    # subprocess.call(["lualatex", "-interaction", "nonstopmode", output, out_stem+".tex"])
    # subprocess.call(["lualatex", "-interaction", "nonstopmode", output, out_stem+".tex"])
    subprocess.call(["lualatex", output, out_stem+".tex"])
    subprocess.call(["lualatex", output, out_stem+".tex"])
    # Open the result
    subprocess.call(["open", out_name])


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-I", "--input", help="input ROOT filename")
    args = parser.parse_args()

    plot_corr_results(in_name=args.input)
