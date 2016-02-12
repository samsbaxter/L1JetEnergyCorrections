#!/usr/bin/env python
"""
This script outputs all the calibration plots in the ROOT file output by
runCalibration.py as one long pdf, cos TBrowser sucks.

It will make the PDF in the same directory as the ROOT file, under a directory
named output_<ROOT file stem>
"""


import glob
import ROOT
import os
import argparse
import subprocess
import binning
import beamer_slide_templates as bst
import common_utils as cu


ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(1)

etaBins = binning.eta_bins


def plot_to_file(f, plotname, filename, xtitle="", ytitle="", title="",
                 drawopts="", drawfit=True, extend_fit=True):
    """
    f is a TFile
    filename is output, can be a list of filenames (e.g. for .tex, .pdf, .png)
    can optionally not draw the fit to the curve
    """
    ROOT.gStyle.SetPaperSize(10., 10.)
    ROOT.gStyle.SetOptStat("mre")
    ROOT.gStyle.SetOptFit(0101)  # MAGIC COMBO FOR PARAMS+ERRORS
    print plotname
    obj = f.Get(plotname)
    obj2 = f.Get(plotname + "_fit")
    if not obj:
        print "Can't find", obj
        return False

    if (drawfit and not obj2):
        print "Can't find", plotname + "_fit, not drawing fit function"
        drawfit = False

    p = obj.Clone()
    # p.GetYaxis().SetTitle(ytitle)
    # p.GetXaxis().SetTitle(xtitle)
    p.SetTitle(';'.join([title, xtitle, ytitle]))
    p.Draw(drawopts)

    if drawfit:
        p2 = obj2.Clone()
        # p2.GetYaxis().SetTitle(ytitle)
        # p2.GetXaxis().SetTitle(xtitle)
        p2.SetTitle(';'.join([title, xtitle, ytitle]))
        fn = p2.GetListOfFunctions().At(0)
        if fn:
            fn.SetLineWidth(2)
        p2.Draw(drawopts + "SAME")

        # draw fit over full range, not just fitted range
        if extend_fit:
            fn2 = fn.Clone()
            fn2.SetRange(0, 1000)
            fn2.SetLineStyle(3)
            fn2.SetLineWidth(2)
            fn2.Draw("SAME")
        p.Draw(drawopts + "SAME")

    ROOT.gPad.Update()
    ROOT.gPad.SetTicks(1, 1)

    # Draw fit stats box
    if drawfit:
        st = p2.FindObject("stats")
        st.SetFillStyle(0)
        st.SetX1NDC(0.6)
        st.SetX2NDC(0.9)
        st.SetY1NDC(0.55)
        st.SetY2NDC(0.9)

    for f in filename:
        ROOT.gPad.Print(f)

    ROOT.gPad.Clear()

    return True


def plot_corr_results(in_name=""):
    """
    Puts correction plots in one pdf.
    """
    # Setup input file
    print "Opening", in_name
    in_stem = os.path.basename(in_name).replace(".root", "")
    input_file = cu.open_root_file(in_name)

    # Setup output directory & filenames
    odir = os.path.dirname(os.path.abspath(in_name)) + "/" + in_stem + "/"
    cu.check_dir_exists_create(odir)

    out_name = odir + in_stem + ".pdf"
    out_stem = out_name.replace(".pdf", "")
    print "Writing to", out_name

    # Start beamer file
    # Use template - change title, subtitle, include file
    frontpage_title = "Correction value plots, binned by $|\eta|$"
    sub = in_stem.replace("output_", "").replace("_", "\_")
    sub = sub.replace("_ak", r"\\_ak")
    subtitle = "{\\tt " + sub + "}"
    slides_file = out_stem + "_slides.tex"
    main_file = out_stem + ".tex"
    with open("beamer_template.tex", "r") as t:
        with open(main_file, "w") as f:
            substitute = {"@TITLE": frontpage_title, "@SUBTITLE": subtitle,
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
            emax = etaBins[i + 1]
            name = "l1corr_eta_%g_%g" % (emin, emax)
            bin_title = "%g <  |\eta^{L1}| < %g" % (emin, emax)
            if plot_to_file(input_file,
                            name,
                            [odir + name + ".tex", odir + name + ".pdf"],
                            xtitle="<p_{T}^{L1}> [GeV]",
                            ytitle="Correction = 1/< p_{T}^{L1}/p_{T}^{Ref} >",
                            title="",
                            drawfit=True,
                            extend_fit=True):
                titles.append("$%s$" % bin_title)
                plotnames.append(odir + name + ".tex")
            print i
            print titles
            print plotnames
            if (((i + 1) % 4 == 0) and (i != 0)) or (i == len(etaBins) - 2):
                print "Writing", emin, emax
                slidetitle = "Correction value"
                slides.write(bst.make_slide(bst.four_plot_slide, titles, plotnames, slidetitle))
                titles = []
                plotnames = []

    compile_pdf(main_file, out_name, odir, 1)


def compile_pdf(texfile, pdffile, outdir, num_compilation=1):
    """
    Compile the pdf
    Do it twice to get TOC and page num right
    """

    output = "-output-directory=%s" % outdir
    for i in range(num_compilation):
        subprocess.call(["lualatex", "-interaction", "nonstopmode", output, texfile])

    # Open the result
    # subprocess.call(["open", pdffile])

    # Tidy up all the non .tex or .pdf files
    for f in glob.glob(os.path.join(outdir, texfile.replace(".tex", ".*"))):
        if os.path.splitext(f)[1] not in [".tex", ".pdf"]:
            print 'deleting', f
            os.remove(f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="input ROOT filename")
    args = parser.parse_args()

    plot_corr_results(in_name=args.input)
