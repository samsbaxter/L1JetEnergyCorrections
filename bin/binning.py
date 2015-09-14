"""
Centralised way to keep track of pt & eta binning.

For future, may need to split up into GCT/Stage1 Vs Stage 2...
"""


import ROOT
import array
import numpy as np

ROOT.PyConfig.IgnoreCommandLineOptions = True


############
# PT BINS
############
pt_bins = list(np.arange(14, 254, 4))
# wider binning at higher pt for low stats regions
pt_bins_wide = list(np.concatenate((np.arange(14, 50, 4), np.arange(50, 270, 20)))) # larger bins at higher pt

# 8 GeV bins for resolution plots
pt_bins_8 = list(np.arange(14,246,8))
pt_bins_8.append(250)
# and wider ones for low stat bins
pt_bins_8_wide = list(np.concatenate((np.arange(14,54,8), np.arange(54, 242, 20))))
pt_bins_8_wide.append(250)

############
# ETA BINS
############
eta_bins = [0.0, 0.348, 0.695, 1.044, 1.392, 1.74, 2.172, 3.0, 3.5, 4.0, 4.5, 5]
eta_bins_all = [-5, -4.5, -4.0, -3.5, -3.0, -2.172, -1.74, -1.392, -1.044, -0.695, -0.348, 0.0, 0.348, 0.695, 1.044, 1.392, 1.74, 2.172, 3.0, 3.5, 4.0, 4.5, 5]
eta_bins_central = [eta for eta in eta_bins if eta < 3.1]
eta_bins_forward = [eta for eta in eta_bins if eta > 2.9]
# a handy palette of colours
eta_bin_colors = [ROOT.kRed, ROOT.kBlue, ROOT.kGreen+2, ROOT.kBlack, ROOT.kMagenta, ROOT.kOrange+7, ROOT.kAzure+1, ROOT.kRed+3, ROOT.kViolet+1, ROOT.kOrange, ROOT.kTeal-5]
