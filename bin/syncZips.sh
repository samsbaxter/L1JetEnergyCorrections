#!/bin/bash -e
#
# Sync showoffPlot ZIPs, and untar them
#

unzip() {
    # $1 is tar file
    # $2 is dest dir
    echo "Unzip into $2"
    mkdir -p "$2"
    tar xzf "$1" -C "$2"
}

startdir="/hdfs/L1JEC/CMSSW_8_0_2/L1JetEnergyCorrections"
dest=".."
for f in $startdir/*; do
    echo "Looking in $f"
    basedir=$(basename $f)
    for tf in $(find $f -name "showoff*tar.gz"); do
        # Copy zip file
        subdir=$(dirname ${tf#$f})
        tardir="$dest/$basedir/$subdir/"
        echo "$tf -> $tardir"
        mkdir -p $tardir
        tarfile=$(basename $tf)
        tardest="$tardir/$tarfile"
        # test if the file exists and actually needs copying
        if [ -e $tardest ]; then
            cmp --silent "$tf" "$tardest"
            compare=$?
            # Need to update local copy
            if [[ $compare != 0 ]]; then
                echo "REPLACE"
                # need to rm as hadoop can't overwrite with copyToLocal
                if [ -e "$tardest" ]; then
                    rm "$tardest"
                fi
                hadoop fs -copyToLocal ${tf#/hdfs} $tardir
                # Do unzipping
                showoffdir="$tardir/${tarfile%%.*}"
                unzip $tardest $showoffdir
            else
                echo "$tardest is up to date, skipping"
            fi
        else
            hadoop fs -copyToLocal ${tf#/hdfs} $tardir
            # Do unzipping
            showoffdir="$tardir/${tarfile%%.*}"
            unzip $tardest $showoffdir
        fi
    done
done