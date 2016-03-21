#!/bin/bash -e
#
# Do fits for output files.
# User should just pass any number of directories as arguments.
# This script will look for output*.root files in each and process.
for d in $@; do
    # echo $d
    for f in $d/output*.root; do
        echo "Doing $f"
        python runCalibration.py $f $f --redo-correction-fit --inherit-params --stage2 --central
    done
done