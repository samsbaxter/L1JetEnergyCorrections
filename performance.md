#Performance scripts

This details some scripts that are useful in studies of the jet performance.

- [Check calibrations](#check-calibrations)
  - [PBS](#pbs)
  - [HTCondor](#htcondor)
- [Resolution](#resolution)
  - [PBS](#pbs-1)
  - [HTCondor](#htcondor-1)
- [Comparing fit functions/graphs](#comparing-fit-functionsgraphs)
- [Fitting GUI](#fitting-gui)
- [Printing/Styling Plots](#printingstyling-plots)

##Check calibrations

This is done with [bin/checkCalibration.py](bin/checkCalibration.py). This takes the ROOT files of matched pairs output by `RunMatcher` as input, and makes a lot of plots to check the response of L1 jets against reference jets. This includes graphs of response vs eta/pT( both L1 and reference jet), and 2D plots of response vs pT, and pT(L1) vs pT(reference).

To run on a batch system:

###HTCondor
Use [bin/HTCondor/submit_checkCalib_dag.sh](bin/HTCondor/submit_checkCalib_dag.sh). The user must supply the name(s) of the pairs files to run over. Everything else is auto-generated.

###PBS
Use [bin/submit_check_jobs.sh](bin/submit_check_jobs.sh)

##Resolution
This is done with [bin/makeResolutionPlots.py](bin/makeResolutionPlots.py). This takes the ROOT file with matched pairs output by `RunMatcher`, and produces resolution plots stored in a ROOT file. Quantities include `L1 - Ref`, `(L1 - Ref) / L1`, and `(L1 - Ref) / Ref`. For possible options, in `bin` do `python makeResolutionPlots.py -h`. Note that there are several possible definitions of resolution, and this script covers the following:

- (pT(L1) - pT(Ref))/pT(L1), calculated on a pair-by-pair basis, binned in pT(L1). Stored as `resL1_<eta_min>_<eta_max>`.
- (pT(L1) - pT(Ref))/pT(Ref), calculated on a pair-by-pair basis, binned in pT(L1). Stored as `resRefL1_<eta_min>_<eta_max>`.
- (pT(L1) - pT(Ref))/pT(Ref), calculated on a pair-by-pair basis, binned in pT(L1). Stored as `resRefRef_<eta_min>_<eta_max>`.
- use the width of the pT(L1) - pT(Ref) distribution, then divide by the average pT(L1). This is done in bins of pT(L1). Stored as `resL1_<eta_min>_<eta_max>_diff`.
- use the width of the pT(L1) - pT(Ref) distribution, then divide by the average pT(Ref). This is done in bins of pT(Ref). Stored as `resRefRef_<eta_min>_<eta_max>_diff`. **This is the correct one for performance plots, and is the one used by `showoffPlots.py`**.

To run on a batch system:

###HTCondor
Use [bin/HTCondor/submit_resolution_dag.sh](bin/HTCondor/submit_resolution_dag.sh). The user must supply the name(s) of the pairs files to run over. Everything else is auto-generated.

###PBS
Use [bin/submit_resolution_jobs.sh](bin/submit_resolution_jobs.sh)

##Comparing fit functions/graphs

This is done in [bin/compareFits.py](bin/compareFits.py). It's a bit ad-hoc for now, but is designed such that you can just make a `Plot` object from various `Contribution` objects. See examples in the script.

##Fitting GUI

This program, [bin/play_fitting_gui.py](bin/play_fitting_gui.py) has 2 purposes: 1) to explore the possible space covered by the correction function, and 2) provide a way to get a decent set of starting parameters for fitting in ROOT (since it struggles sometimes). This requires the `tkinter` python package, which should come as default. You can also load a graph from a file, e.g. from the output file from `runCalibration.py`. This is still under development, so is a little rough.

Run with:

```
python play_fitting_gui.py
```

##Printing/Styling Plots
There are several other useful scripts in the [bin](bin) directory designed for quick'n'easy styling & printing to PDF. Doing `python <scriptname> -h` should elucidates the possible options.

- [showoffPlots.py](bin/showoffPlots.py) This takes in ROOT files output by `runCalibration` / `RunMatcher` / `checkCalibration` / `makeResolutionPlots`, to quickly output PDF plots for use in presentation or similar. **Note** you should set the variables `plot_labels` and `plot_title` to something suitable. (The former is a list, to handle when there are multiple input files to be plotted on the same canvas, e.g. comparing different sets of calibrations.)

- [calibration_slides.py](bin/calibration_slides.py) This takes the ROOT file output by `runCalibration.py` and turns it into a set of PDF slides with the plots for all eta bins.
