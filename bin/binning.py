"""
Centralised way to keep track of pt & eta binning.

For future, may need to split up into GCT/Stage1 Vs Stage 2...
"""


import array
import numpy


############
# PT BINS
############
pt_bins = list(numpy.arange(14, 254, 4))
# wider binning for low stats regions
pt_bins_wide = list(numpy.concatenate((numpy.arange(14, 50, 4), numpy.arange(50, 270, 20)))) # larger bins at higher pt

############
# ETA BINS
############
eta_bins = [0.0, 0.348, 0.695, 1.044, 1.392, 1.74, 2.172, 3.0, 3.5, 4.0, 4.5, 5.001]
