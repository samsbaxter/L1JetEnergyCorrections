"""
Plot same fn with diff params for comparison
"""

import ROOT
import numpy as np
from binBanding import plot_bin_band
import matplotlib.pyplot as plt
from binning import eta_bins

ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(1)
ROOT.TH1.SetDefaultSumw2()
# ROOT.gStyle.SetOptTitle(0);
ROOT.gStyle.SetOptStat(0);
ROOT.gStyle.SetPalette(55)



def plot_comparison(params1, label1, params2, label2, title="", plotname="fn_compare.pdf"):
    """Plot same fn for 2 set of parameters, with individual labels"""
    fitfcn = ROOT.TF1("fitfcn", "[0]+[1]/(pow(log10(x),2)+[2])+[3]*exp(-[4]*(log10(x)-[5])*(log10(x)-[5]))", 0, 50)
    fcn1 = fitfcn.Clone("fcn1")
    for i, p in enumerate(params1):
        fcn1.SetParameter(i, p)
    fcn1.SetLineColor(ROOT.kBlack)

    fcn2 = fitfcn.Clone("fcn2")
    for i, p in enumerate(params2):
        fcn2.SetParameter(i, p)
    fcn2.SetLineColor(ROOT.kRed)

    max1 = fcn1.GetMaximum()
    max2 = fcn2.GetMaximum()

    c = ROOT.TCanvas("c", "", 600, 500)
    c.SetTicks(1,1)
    c.SetGrid()
    c.SetTitle(title)
    fcn1.Draw()
    fcn2.Draw("SAME")
    fcn1.GetYaxis().SetRangeUser(0, max(max1, max2)*1.1)
    fcn1.GetXaxis().SetTitle("p_{T} [GeV]")

    leg = ROOT.TLegend(0.65, 0.65, 0.88, 0.88)
    leg.AddEntry(fcn1, label1, "L")
    leg.AddEntry(fcn2, label2, "L")
    leg.Draw()

    c.SaveAs(plotname)


def pf_func(et, params):
    """NumPy version of fit fn"""
    return params[0] + (params[1]/(np.power(np.log10(et), 2)+params[2])) + params[3] * np.exp(-1.*params[4]*np.power(np.log10(et)-params[5], 2))


def plot_comparison_numpy(params1, label1, color1='black', params2=None, label2="", color2='red', title="", plotname=""):
    """Plot same fn for 2 sets of parameters, with indiviudal labels

    Uses numpy.
    """
    pt = np.arange(0.5, 20, 0.5)
    corrections1 = pf_func(pt, params1)

    plt.plot(pt, corrections1, 'x-', color=color1, label=label1, lw=1.5)
    if params2:
        corrections2 = pf_func(pt, params2)
        plt.plot(pt, corrections2, 'd-', color=color2, label=label2, lw=1.5)
    plt.xlabel(r"$p_T^{in} \mathrm{[GeV]}$")
    plt.ylabel("Corr. factor")
    # plt.set_xscale('log')
    plt.minorticks_on()
    plt.grid(b=True, which='major', axis='both')
    plt.grid(b=True, which='minor', axis='both')
    plt.xlim(left=pt[0]-0.5)

    # draw intersection lines for 5, 10
    for p, lc in zip([0.5, 5, 10], ["purple", "blue", "green"]):
        corr = pf_func(p, params1)
        plt.vlines(p, ymin=plt.ylim()[0], ymax=corr, color=lc, linestyle='dashed', linewidth=1.5, label=r'$p_T^{in}$' + ' = %g GeV,\ncorr. factor = %.3f' % (p, corr))
        plt.hlines(corr, xmin=0, xmax=p, color=lc, linestyle='dashed', linewidth=1.5)
    plt.title(title)
    plt.legend(fontsize=12, loc=0)
    if plotname != "":
        plt.savefig(plotname)
        plt.cla()


def plot_bin_band_all(corr_fns, titles, plotname="binBandingAll.pdf"):
    """Plot post pt Vs pre pt, with bands for 4 GeV granularity"""

    # Internal jet pTs, pre calibration
    min_pre = 0.5
    max_pre = 20
    pt_pre = np.arange(min_pre, max_pre, 0.5)

    n_cols = 3
    n_rows = len(corr_fns) / 3
    if len(corr_fns) % 3 != 0:
        n_rows += 1

    c1 = ROOT.TCanvas("c_all","", 600*n_cols, 600*n_rows)
    c1.SetTicks(1, 1)
    c1.Divide(n_cols, n_rows)
    shit_to_keep_showing = [] # need this otherwise python will auto garbage collect
    for ic, corr_fn in enumerate(corr_fns,1):
        c1.cd(ic)

        # Post calibration
        pt_post = np.array([pt * corr_fn.Eval(pt) for pt in pt_pre])

        # Make coloured blocks to show the bins
        blocks = []
        lower_bound = pt_pre[0] / 4
        if pt_post[-1] % 4 != 0:
            upper_bound = 4*(1+(pt_post[-1] / 4))
        else:
            upper_bound = pt_post[-1]
        gct_bins = np.arange(0, upper_bound+4, 4)
        for i, pt in enumerate(gct_bins):
            # skip if
            if pt+4 < pt_post[0] or pt > pt_post[-1]:
                continue
            b = ROOT.TBox(min_pre, pt, max_pre, pt+4)
            col = 30 if i % 2 else 38
            b.SetFillColorAlpha(col, 0.7)
            b.SetLineStyle(0)
            blocks.append(b)
        shit_to_keep_showing.append(blocks)

        # Plot
        gr = ROOT.TGraph(len(pt_pre), pt_pre, pt_post)
        gr.SetMarkerColor(ROOT.kRed)
        gr.SetMarkerStyle(2)
        gr.SetTitle(titles[ic-1]+";p_{T}^{pre} [GeV];p_{T}^{post} [GeV]")
        gr.Draw("AP")
        [b.Draw() for b in blocks]
        gr.Draw("P")
        # some helpful lines at 0.5, 5, 10
        for p in [0.5, 5, 10]:
            l_x = ROOT.TLine(p, 0, p, p*corr_fn.Eval(p))
            l_x.SetLineStyle(2)
            l_x.SetLineColor(ROOT.kBlue)
            l_x.Draw()
            shit_to_keep_showing.append(l_x)
            l_y = ROOT.TLine(0, p*corr_fn.Eval(p), p, p*corr_fn.Eval(p))
            l_y.SetLineStyle(2)
            l_y.SetLineColor(ROOT.kBlue)
            l_y.Draw()
            shit_to_keep_showing.append(l_y)

        shit_to_keep_showing.append(gr)
    c1.SaveAs(plotname)


if __name__ == "__main__":
    # old_0_0p348 = [1.14, 2.297, 5.959, 1.181, 0.7286, 0.3673]
    # new_0_0p348 = [3.32079045, 30.10690152, 2.91713150, -206.73606994, 0.00701027, -20.22374281]
    # plot_comparison(old_0_0p348, "2012", new_0_0p348, "New", "fn_compare_0_0p348_newRCTv2.pdf")
    fitfcn = ROOT.TF1("fitfcn", "[0]+[1]/(pow(log10(x),2)+[2])+[3]*exp(-[4]*(log10(x)-[5])*(log10(x)-[5]))", 0, 20)

    # 2012 calibs by themselves
    old_0_0p348 = [1.114,2.297,5.959,1.181,0.7286,0.3673]
    old_0p348_0p695 = [0.7842,4.331,2.672,0.5743,0.8811,0.4085]
    old_0p695_1p044 = [0.961,2.941,2.4,1.248,0.666,0.1041]
    old_1p044_1p392 = [0.6318,6.6,3.21,0.8551,0.9786,0.291]
    old_1p392_1p74 = [0.3456,8.992,3.165,0.5798,2.146,0.4912]
    old_1p74_2p172 = [0.8501,3.892,2.466,1.236,0.8323,0.1809]
    old_2p172_3 = [0.9027,2.581,1.453,1.029,0.6767,-0.1476]
    old_3_3p5 = [1.117,2.382,1.769,0.0,-1.306,-0.4741]
    old_3p5_4 = [1.634,-1.01,0.7184,1.639,0.6727,-0.2129]
    old_4_4p5 = [0.9862,3.138,4.672,2.362,1.55,-0.7154]
    old_4p5_5 = [1.245,1.103,1.919,0.3054,5.745,0.8622]

    param_sets = [old_0_0p348, old_0p348_0p695, old_0p695_1p044, old_1p044_1p392, old_1p392_1p74, old_1p74_2p172, old_2p172_3, old_3_3p5, old_3p5_4, old_4_4p5, old_4p5_5]
    corr_fns = []
    titles = []
    for ip, params in enumerate(param_sets):
        f = fitfcn.Clone("fitfcn_%g_%g" % (eta_bins[ip], eta_bins[ip+1]))
        [f.SetParameter(i,x) for i,x in enumerate(params)]
        corr_fns.append(f)
        titles.append("2012_%g_%g" % (eta_bins[ip], eta_bins[ip+1]))
        titles[-1] = titles[-1].replace(".","p")

        # individual plots
        plot_comparison_numpy(params, "2012", color1='red', title=titles[ip], plotname="fn_%s.pdf" % titles[ip])
        plot_bin_band(corr_fns[ip], title=titles[ip], plotname="binBands_%s.pdf" % titles[ip])

    # do one big plot of correction functions
    fig = plt.figure()
    n_cols = 3
    n_rows = len(param_sets) / 3
    if len(param_sets) % 3 != 0:
        n_rows += 1
    fig.set_size_inches(24, 8*n_rows)
    for i, pset in enumerate(param_sets, 1):
        ax = fig.add_subplot(n_rows, n_cols, i)
        plot_comparison_numpy(pset, "2012", color1='red', title=titles[i-1], plotname="")
    plt.savefig("fn_2012_all.pdf")


    # do one big plot for pre vs post pt
    plot_bin_band_all(corr_fns, titles, plotname="binBandingAll.pdf")