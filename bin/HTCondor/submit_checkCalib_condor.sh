#!/bin/bash

# submit calibration jobs on HTCondor. For each job, does 1 eta bin for 1 pairs file.
# all you should change is pairsFile(s) array

declare -a pairsFiles=(
"/hdfs/user/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/Stage1_QCDSpring15_AVE20BX25_newRCTv2_calibrated_newLUT_3_Aug_15_Bristol/pairs_QCD_Pt-30to1000_Spring15_AVE20BX25_Stage1_QCDSpring15_AVE20BX25_newRCTv2_calibrated_newLUT_3_Aug_15_Bristol_gtJets_ref14to1000_l10to500.root"
"/hdfs/user/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/Stage1_QCDSpring15_AVE20BX25_newRCTv2_oldCalibrated_3_Aug_15_Bristol_v3/pairs_QCD_Pt-30to1000_Spring15_AVE20BX25_Stage1_QCDSpring15_AVE20BX25_newRCTv2_oldCalibrated_3_Aug_15_Bristol_v3_gtJets_ref14to1000_l10to500.root"
)

declare -a etaBins=(
0
0.348
0.695
1.044
1.392
1.74
2.172
3.0
3.5
4.0
4.5
5
)

# update the setup script on worker side
sed -i "s/VER=CMSSW_.*/VER=$CMSSW_VERSION/" checkCalib_condor.sh

# make a copy of the condor script
outfile="submit_checkCalib.condor"
cp submit_template.condor "$outfile"

cdir=${PWD%HTCondor}
echo $cdir

# Replace correct parts
sed -i 's/SEDNAME/checkCalib/g' $outfile
sed -i 's/SEDEXE/checkCalib_condor.sh/g' $outfile
sed -i "s@SEDINPUTFILES@$cdir/checkCalibration.py, $cdir/binning.py, $PWD/condor_wrapper.py, $cdir/correction_LUT_plot.py, $cdir/common_utils.py@" $outfile

# Queue up jobs
for pairs in "${pairsFiles[@]}"
do
    fdir=`dirname $pairs`
    fname=`basename $pairs`

    echo "Using pairs file $pairs"
    echo "Writing output to directory: $fdir"

    len=${#etaBins[@]}
    len=$(( len - 1 ))
    for ((i=0;i<$len;++i));
    do
        j=$(( i + 1 ))
        etamin=${etaBins[i]}
        etamax=${etaBins[j]}
        jobname="${etamin}to${etamax}"
        outname=${fname#pairs_}
        outname=${outname%.root}
        outname="check_${outname}_${i}.root"
        echo "$jobname"
        echo "$outname"
        echo "arguments = python checkCalibration.py ${fdir}/${fname} ${fdir}/${outname} --excl --etaInd ${i} --maxPt 250" >> "$outfile"
        echo "queue" >> "$outfile"
    done
    outname=${fname#pairs_}
    outname=${outname%.root}
    echo "arguments = python checkCalibration.py ${fdir}/${fname} ${fdir}/check_${outname}_central.root --incl --central --maxPt 250" >> "$outfile"
    echo "queue" >> "$outfile"
    echo "arguments = python checkCalibration.py ${fdir}/${fname} ${fdir}/check_${outname}_forward.root --incl --forward --maxPt 250" >> "$outfile"
    echo "queue" >> "$outfile"
    echo "arguments = python checkCalibration.py ${fdir}/${fname} ${fdir}/check_${outname}_all.root --incl --maxPt 250" >> "$outfile"
    echo "queue" >> "$outfile"

done

echo ""
echo "Condor script made"
echo "Submitting:"
# condor_submit $outfile
echo "Submit with:"
echo "condor_submit $outfile"
