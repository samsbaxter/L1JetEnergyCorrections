#!/usr/bin/env python
"""
This script pulls the correction functions from the ROOT file 
output by runCalibration.py, and then:

- makes a LUT with them
- prints them in py/cpp format so the user can play with it
- plots them over suitable pt range, to check they are sensible

Robin Aggleton
"""

import ROOT
import sys
import array
import numpy as np
from itertools import izip
import os
import argparse
import binning
import common_utils as cu
from runCalibration import generate_eta_graph_name


ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(1)
ROOT.gStyle.SetOptFit(1111)

# Et(L1) limits used for the big plot of all functions
etmin, etmax = 0.1, 30


class MultiFunc(object):
    """Class to handle using different TF1s over different ranges.

    E.g. y = x for x = [0,1], then y = x^2 for [1, Inf]
    This was created since it is so hard (impossible?) to do in ROOT.
    """

    def __init__(self, functions_dict):
        """Constructor takes as argument a dictionary, where each key is a tuple,
        and each value is a TF1 object.

        The tuple must have 2 elements: lower and upper bounds, which define the
        valid function range.

        e.g.
        lin = ROOT.TF1("lin", "x")
        quad = ROOT.TF1("quad", "x*x")

        functions_dict = {
            (-np.inf, 1): lin,
            (1, np.inf): quad
        }
        f = c.MultiFunc(functions_dict)
        f.Eval(0.5) # 0.5
        f.Eval(3) # 9
        """
        self.functions_dict = functions_dict


    def Eval(self, x):
        """Emulate TF1.Eval() but will call the correct function,
        depending on which function is applicable for the value of x."""
        return [func for lim, func in self.functions_dict.iteritems() if lim[0] <= x < lim[1]][0].Eval(x)


    def Draw(self, args=None):
        """Draw the various functions"""

        if "SAME" not in args:
            # make a 'blank' function to occupy the complete range of x values:
            lower_lim = min([lim[0] for lim in self.functions_dict.keys()])
            if np.isneginf(lower_lim):
                lower_lim = -999
            upper_lim = max([lim[1] for lim in self.functions_dict.keys()])
            if np.isposinf(lower_lim):
                upper_lim = 999
            blank = ROOT.TF1("blank"+str(np.random.randint(0,10000)), "1.5", lower_lim, upper_lim)
            blank.Draw()
            max_value = max([func.GetMaximum(lim[0], lim[1]) for lim, func in self.functions_dict.iteritems()]) * 1.1
            blank.SetMaximum(max_value)
            min_value = min([func.GetMinimum(lim[0], lim[1]) for lim, func in self.functions_dict.iteritems()]) * 0.9
            blank.SetMinimum(min_value)
            ROOT.SetOwnership(blank, False) # NEED THIS SO IT ACTUALLY GETS DRAWN. SERIOUSLY, WTF?!
            blank.SetLineColor(ROOT.kWhite)

        # now draw the rest of the functions
        args = "" if not args else args
        for func in self.functions_dict.values():
            func.Draw("SAME" + args)


def print_function(function, lang="cpp"):
    """Print TF1 to screen so can replicate in ROOT

    Can choose language (py, cpp)
    """

    rangemin = ROOT.Double() # eurghhhhh - fixes pass by reference
    rangemax = ROOT.Double()
    function.GetRange(rangemin, rangemax)
    params = [function.GetParameter(i) for i in range(function.GetNumberFreeParameters())]
    name = function.GetName().replace(".", "p")

    print ""

    if lang.lower() == "py" or lang.lower() == "cpp":
        if lang.lower() == 'py':
            print "import ROOT"
            print '%s = ROOT.TF1("%s", "%s", %g, %g);' % (name, name, function.GetExpFormula(), rangemin, rangemax)
        elif lang.lower() == 'cpp':
            print 'TF1 %s("%s", "%s", %g, %g);' % (name, name, function.GetExpFormula(), rangemin, rangemax)
        for i, param in enumerate(params):
            print "%s.SetParameter(%d, %.8f)" % (name, i, param)
    elif lang.lower() == "numpy":
        print "import numpy as np"
        print "import matplotlib.pyplot as plt"
        print "et = np.arange(%g, %g, 0.1)" % (etmin, etmax)
        for i, param in enumerate(params):
            print "p%d = %.8f" % (i, param)
        print "def pf_func(et, p0, p1, p2, p3, p4, p5):"
        print "    return p0 + (p1/(np.power(np.log10(et), 2)+p2)) + p3 * np.exp(-1.*p4*np.power(np.log10(et)-p5, 2))"
        print ""
        print ""
        print "plt.plot(et, pf_func(et, p0, p1, p2, p3, p4, p5), lw=2, color='red')"
        print "plt.xlabel(r'$E_T$');plt.ylabel('Correction Factor')"
        print "plt.show()"
        # print "plt.savefig('plot.pdf')"

    print ""


def print_GCT_lut_file(fit_params, eta_bins, filename):
    """
    Take fit parameters and print to file, for use in CMSSW config file with GCT emulator.

    Eta bins are in order from the center to forwards i.e. 0-0.348, 0.348-0.695, etc

    IMPORTANT: high precision is required, particularly if you are using the PF
    correction function and [3] is large - then precision of [4] in particular
    is crucial. A change from 3 d.p. to 6 d.p. changes the correction factor
    from -1.27682 to 2.152 !!!
    """
    # check
    if (1 + len(fit_params)) != len(eta_bins):
        print "ERROR: no. of eta bins in fit_params not same as no. of eta bins in setup"
        return

    with open(filename, "w") as lut_file:
        lut_file.write("# put this in your py config file\n")
        lut_file.write("PFCoefficients = cms.PSet(\n")

        # non tau bit first
        for i, bin in enumerate(fit_params):
            line = "    nonTauJetCalib%i = cms.vdouble(" % i
            line += ','.join([str("%.8f" % x) for x in fit_params[i]])
            line += "),\n"
            lut_file.write(line)

        # tau bit - only central region
        for i, bin in enumerate(fit_params):
            if eta_bins[i + 1] <= 3.0:
                line = "    tauJetCalib%i = cms.vdouble(" % i
                line += ','.join([str("%.8f" % x) for x in fit_params[i]])
                line += "),\n"
                lut_file.write(line)

        lut_file.write(")\n")


def print_Stage1_lut_file(fit_functions, eta_bins, filename):
    """
    Take fit parameters and print to file, for use in CMSSW config file with Stage 1 emulator.

    fit_params is a list, where each entry is a list of fit parameters for a given eta bin.
    The order MUST be in physical eta, so the first entry coveres 0 - 0.348.

    Note that the LUT has entries for both + and - eta. It refers to eta by region number (0 - 21),
    *not* physical eta. Thus the first bin for the LUT must be 4.5 - 5 NOT 0 - 0.348.
    Don't worry, this method handles that conversion.

    Please update the header if necessary - check with Len.

    Adapted by code originally by Maria Cepeda.

    IMPORTANT: high precision is required, particularly if you are using the PF
    correction function and [3] is large - then precision of [4] in particular
    is crucial. A change from 3 d.p. to 6 d.p. changes the correction factor
    from -1.27682 to 2.152 !!!
    """
        # check
    if (1 + len(fit_functions)) != len(eta_bins):
        print "ERROR: no. of eta bins in fit_functions not same as no. of eta bins in setup"
        return

    with open(filename, "w") as lut_file:
        with open(filename.replace(".txt", "_dump.txt"), "w") as dump_file:
            header = """#<header> V1 15 7 </header>
########################################
# jet calibration and ranking LUT
# MSB 5 bits are eta value, LSB 10 bits
# are jet pt (not 14!, make sure to cap)
########################################
# Second  attempt at preliminar CalibJet for FirmwareVersion3
# Symmetric in Eta and RANK=0 jets do not scale up
#########################################
"""
            lut_file.write(header)

            for eta in xrange(22):

                param_ind = (10 - eta) if eta < 11 else (eta - 11)
                print "Eta region:", eta, " = physical eta bin:", param_ind
                for pt in xrange(1025):

                    if pt >(1<<10)-1:
                        pt = ((1<<10) -1)
                        break

                    lut_address = (eta<<10) + pt
                    physPt = pt / 2. # convert HW pt to physical pt
                    pt_corr = physPt * fit_functions[param_ind].Eval(physPt)
                    if pt_corr < 0: # avoid -ve pt
                        pt_corr = 0
                    RANKCALIB = int(pt_corr / 4);  # The 4 is to go to the 4 GeV binning at the GT
                    if (RANKCALIB > 63): # cap pt
                        RANKCALIB = 63;
                    line = "%s %s\n" % (lut_address, RANKCALIB)
                    lut_file.write(line);
                    dump_line = "eta: %d phys pt: %f LUT address: %d corrValue: %f corrPhysPt: %f RANKCALIB: %d\n" % (eta, physPt, lut_address, fit_functions[param_ind].Eval(physPt), pt_corr, RANKCALIB)
                    dump_file.write(dump_line)


def make_fancy_fits(fits, graphs):
    """
    Make fancy fit, by checking for deviations between graph and fit at low pT.
    Then below the pT where they differ, just use the last good correction factor.

    This generates a new set of correction functions, represented by MultiFunc objects.
    """
    new_functions = []

    c = ROOT.TCanvas("c", "", 600, 600)

    for i, (fit, gr) in enumerate(zip(fits, graphs)):
        x_arr, y_arr = cu.get_xy(gr)
        ex_arr, ey_arr = cu.get_exey(gr)

        pt_merge = 0
        corr_merge = 0

        print "Eta bin", str(i)
        print "pt, correction acc. to graph, correcction acc. to fit, diff"

        for j, (pt, corr, pt_err, corr_err) in enumerate(izip(x_arr[::-1], y_arr[::-1], ex_arr[::-1], ey_arr[::-1])):
            # Loop through each point of the graph in reverse,
            # only considering points with pt < 40.
            # Determine where the function and graph separate by
            # looking at the difference
            # The error arrays are redundant for now, but are included incase
            # the user wishes to use their values in the future
            if pt > 40:
                continue
            print pt, corr, fit.Eval(pt), abs(fit.Eval(pt) - corr)
            if abs(fit.Eval(pt) - corr) > 0.05:
                break
            else:
                pt_merge = pt
                corr_merge = fit.Eval(pt)

        print "pt_merge:", pt_merge, "corr val:", fit.Eval(pt_merge), "corr merge", corr_merge

        # Make our new 'frankenstein' function: constant for pt < pt_merge,
        # then the original function for pt > pt_merge
        constant = ROOT.TF1("constant%d" % i, "%.8f" % corr_merge, 0, pt_merge)
        constant.SetParameter(0, corr_merge)

        function_str = "[0]+[1]/(pow(log10(x),2)+[2])+[3]*exp(-[4]*(log10(x)-[5])*(log10(x)-[5]))"
        for p in xrange(fit.GetNumberFreeParameters()):
            function_str = function_str.replace("[%d]" % p, "%.8f" % fit.GetParameter(p))
        fit_new = ROOT.TF1("fitfcn%d" % i, function_str, pt_merge*0.8, 512)
        # set lower range below pt_merge just for drawing purposes

        functions_dict = {(0, pt_merge): constant,
                          (pt_merge, 512): fit_new}
        total_fit = MultiFunc(functions_dict)
        new_functions.append(total_fit)

    return new_functions


def plot_correction_map(corr_fn, filename="correction_map.pdf"):
    """Make plot of pt before Vs after to show mapping"""

    # jet pTs, pre calibration
    min_pre = 0
    max_pre = 52
    jet_pt_pre = np.arange(min_pre, max_pre, 0.5)

    # Post calibration
    jet_pt_post = np.array([pt * corr_fn.Eval(pt) for pt in jet_pt_pre])

    # Make coloured blocks to show the L1 pT bins
    blocks = []  # for persistence otherwise garbabe collected
    gct_bins = np.arange(4, 16 + (18*4), 4)
    for i, pt in enumerate(gct_bins):
        if pt+4 < jet_pt_post[0] or pt > jet_pt_post[-1]:
            continue
        b = ROOT.TBox(min_pre, pt, max_pre, pt+4)
        col = 30 if i % 2 else 38
        b.SetFillColor(col)
        b.SetLineStyle(0)
        blocks.append(b)

    # Plot
    c = ROOT.TCanvas("c","", 800, 800)
    c.SetTicks(1, 1)
    c.SetGrid(1, 1)
    gr = ROOT.TGraph(len(jet_pt_pre), jet_pt_pre, jet_pt_post)
    gr.SetMarkerColor(ROOT.kRed)
    gr.SetTitle("Input jets at 0.5 GeV intervals;p_{T}^{pre};p_{T}^{post}")
    gr.SetMarkerStyle(2)
    gr.Draw("AP")
    [b.Draw() for b in blocks]
    gr.Draw("P")
    # Some helpful lines
    def draw_lines(pt):
        lx = ROOT.TLine(pt, gr.GetYaxis().GetXmin(), pt, pt*corr_fn.Eval(pt))
        lx.SetLineStyle(2)
        lx.Draw()
        ly = ROOT.TLine(0, pt*corr_fn.Eval(pt), pt, pt*corr_fn.Eval(pt))
        ly.SetLineStyle(2)
        ly.Draw()
    draw_lines(5)
    draw_lines(30)
    c.SaveAs(filename)


def plot_all_functions(functions, filename, eta_bins, et_min=0, et_max=30):
    """Draw all corrections functions on one big canvas"""
    canv = ROOT.TCanvas("canv", "", 3800, 1200)
    nrows = 2
    ncols = ((len(binning.eta_bins)-1) / nrows) + 1
    canv.Divide(ncols, nrows)

    # vertical line to intersect graph
    vert_line = ROOT.TLine(5, 0, 5, 3)
    vert_line.SetLineStyle(3)
    vert_line.SetLineWidth(1)

    # horizontal line to intersect graph
    hori_line = ROOT.TLine(et_min, 2, et_max, 2)
    hori_line.SetLineStyle(3)

    for i, fit_func in enumerate(functions):
        canv.cd(i+1)
        fit_func.SetRange(et_min, et_max)
        fit_func.SetLineWidth(1)
        fit_func.SetTitle("%g - %g" % (eta_bins[i], eta_bins[i+1]))
        fit_func.Draw()
        corr_5 = fit_func.Eval(5)
        vert_line.SetY1(-15)
        vert_line.SetY2(15)
        ROOT.gPad.SetTicks(1, 1)
        ROOT.gPad.SetGrid(1, 1)
        vert_line.Draw()
        l2 = hori_line.Clone()
        l2.SetY1(corr_5)
        l2.SetY2(corr_5)
        l2.Draw("SAME")

    canv.SaveAs(filename)


def main(in_args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="input ROOT filename")
    parser.add_argument("lut", help="output LUT filename", default="my_lut.txt")
    parser.add_argument("--gct", help="Make LUT for GCT", action='store_true')
    parser.add_argument("--stage1", help="Make LUT for Stage 1", action='store_true')
    parser.add_argument("--fancy", help="Make fancy LUT. "
                        "This checks for low pT deviations and caps the correction value",
                        action='store_true')
    parser.add_argument("--plots", help="Make plots to check sensibility of correction functions.",
                        action='store_true')
    parser.add_argument("--cpp", help="print ROOT C++ code to screen", action='store_true')
    parser.add_argument("--python", help="print PyROOT code to screen", action='store_true')
    parser.add_argument("--numpy", help="print numpy code to screen", action='store_true')
    args = parser.parse_args(args=in_args)

    if not args.gct and not args.stage1:
        print "You didn't pick which format for the LUT - not making a LUT unless you choose!"

    in_file = cu.open_root_file(args.input)
    out_dir = os.path.dirname(args.lut)

    all_fit_params = []
    all_fits = []
    all_graphs = []

    etaBins = binning.eta_bins
    for i, (eta_min, eta_max) in enumerate(izip(etaBins[:-1], etaBins[1:])):
        print "Eta bin:", eta_min, "-", eta_max

        # get the fitted TF1
        fit_func = cu.get_from_file(in_file, "fitfcneta_%g_%g" % (eta_min, eta_max))
        all_fits.append(fit_func)
        fit_params = [fit_func.GetParameter(par) for par in range(fit_func.GetNumberFreeParameters())]
        all_fit_params.append(fit_params)
        print "Fit parameters:", fit_params

        # get the corresponding fit graph
        fit_graph = cu.get_from_file(in_file, generate_eta_graph_name(eta_min, eta_max))
        all_graphs.append(fit_graph)

        print "Fit fn evaluated at 5 GeV:", fit_func.Eval(5)

        # Print function to screen
        if args.cpp:
            print_function(fit_func, "cpp")
        if args.python:
            print_function(fit_func, "py")
        if args.numpy:
            print_function(fit_func, "numpy")


    # Print all functions to one canvas
    plot_all_functions(all_fits, os.path.join(out_dir, "all_raw_fits.pdf"), etaBins, etmin, etmax)

    # Make LUTs
    if args.gct:
        print_GCT_lut_file(all_fit_params, etaBins, args.lut)
    elif args.stage1:
        fits = make_fancy_fits(all_fits, all_graphs) if args.fancy else all_fits
        print_Stage1_lut_file(fits, etaBins, args.lut)
        if args.plots:
            for i, (total_fit, gr) in enumerate(izip(fits, all_graphs)):
                c = ROOT.TCanvas("c%d" % i, "SCREW ROOT", 600, 600)
                c.SetTicks(1,1)
                gr.Draw("ALP")
                y_ax = gr.GetYaxis()
                y_ax.SetRangeUser(0.9*y_ax.GetXmin(), 1.1 * y_ax.GetXmax())
                total_fit.Draw("SAME")
                c.SaveAs(os.path.join(out_dir, "fancyfit_%d.pdf" % i))


    if args.plots:
        # Plot function mapping
        for i, (eta_min, eta_max, fit_func) in enumerate(izip(etaBins[:-1], etaBins[1:], fits)):
            plot_correction_map(fit_func, os.path.join(out_dir, "correction_map_%g_%g.pdf" % (eta_min, eta_max)))


if __name__ == "__main__":
    main()
