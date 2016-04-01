#!/bin/bash -e
#
# Make GIFS from list files
# User should just pass any number of directories as arguments.
# This script will look for list*.txt files in each and make a GIF
# with the same name but with ".gif" extension
for d in $@; do
    # echo $d
    for f in $(find $d -name "list*.txt"); do
        echo "Doing $f"
        pwd=$PWD
        gifdir=$(dirname $f)
        cd $gifdir
        listfile=$(basename $f)
        gifname=${listfile/txt/gif}
        nice -n 10 time convert -dispose Background -delay 50 -loop 0 @$listfile $gifname
        cd $pwd
    done
done