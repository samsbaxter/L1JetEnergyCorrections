#!/bin/bash -e

# This script changes permissions so Robin, Joe, and Jim can access files.
# Usage: ./changePermissions.sh <dir name>

for f in $@
do
    echo "Changing permissions for $f"
    fpath=`readlink -e $f`
    fpath=${fpath#/hdfs} # strip leading /hdfs for hadoop commands
    echo $fpath
    echo "Doing Joe"
    hadoop fs -setfacl -R -m user:jt15104:rwx $fpath*
    echo "Doing Robin"
    hadoop fs -setfacl -R -m user:ra12451:rwx $fpath*
    echo "Doing Jim"
    hadoop fs -setfacl -R -m user:phjjb:rwx $fpath*
done
