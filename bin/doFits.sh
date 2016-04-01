#!/bin/bash -e
#
# Do fits for output files, and make LUTs
# User should just pass any number of directories as arguments.
# This script will look for output*.root files in each and process.
for d in $@; do
    echo "Doing dir $d"
    for f in $(find $d -name output*.root); do
        echo "Doing $f"
        # python runCalibration.py $f $f --redo-correction-fit --inherit-params --stage2 --central
        echo "Doing LUT"
        basefile=$(basename $f)
        lut=${basefile/.root/.txt}
        lut=${lut/output_/lut_}
        python correction_LUT_plot.py --stage2Func --plots --fancy $f $d/$lut
    done
done