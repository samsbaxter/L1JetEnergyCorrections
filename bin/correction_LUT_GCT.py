"""Functions for printing LUT/config for GCT"""


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
