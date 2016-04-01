#!/usr/bin/env python

"""
Submit showoffPlots jobs on HTCondor.

Requires the htcondenser package: https://github.com/raggleton/htcondenser
"""


import os
from time import strftime
import logging
from random import randint
import sys
sys.path.append(os.path.dirname(os.getcwd()))  # to import binning.py
import binning
from binning import pairwise
import htcondenser as ht
import condorCommon as cc
# from distutils.spawn import find_executable


logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
log = logging.getLogger(__name__)


# Add files + options here
CONFIGS = []

for jst in range(2, 7):
    # runcalib plots
    CONFIGS.extend([
    {'input': '/hdfs/L1JEC/CMSSW_8_0_2/L1JetEnergyCorrections/Stage2_HF_QCDFall15_16Mar_int-v14_layer1_noL1JEC_jst%d_RAWONLY_v2/output/output_QCDFlatFall15NoPU_MP_ak4_ref10to5000_l10to5000_dr0p4.root' % jst,
     'type': '--calib',
     'args': '--detail',
     'title': 'Fall15 MC, 0PU, Stage 2 + bitwise Layer 1 + Layer 1 calibs, no L1JEC, Jet Seed Threshold %d GeV' % jst,
     'dest': None},
    {'input': '/hdfs/L1JEC/CMSSW_8_0_2/L1JetEnergyCorrections/Stage2_HF_QCDFall15_16Mar_int-v14_layer1_noL1JEC_jst%d_RAWONLY_v2/output/output_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p4_PU0to10.root' % jst,
     'type': '--calib',
     'args': '--detail',
     'title': 'Fall15 MC, PU0-10, Stage 2 + bitwise Layer 1 + Layer 1 calibs, no L1JEC, Jet Seed Threshold %d GeV' % jst,
     'dest': None},
    {'input': '/hdfs/L1JEC/CMSSW_8_0_2/L1JetEnergyCorrections/Stage2_HF_QCDFall15_16Mar_int-v14_layer1_noL1JEC_jst%d_RAWONLY_v2/output/output_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p4_PU15to25.root' % jst,
     'type': '--calib',
     'args': '--detail',
     'title': 'Fall15 MC, PU15-25, Stage 2 + bitwise Layer 1 + Layer 1 calibs, no L1JEC, Jet Seed Threshold %d GeV' % jst,
     'dest': None},
    {'input': '/hdfs/L1JEC/CMSSW_8_0_2/L1JetEnergyCorrections/Stage2_HF_QCDFall15_16Mar_int-v14_layer1_noL1JEC_jst%d_RAWONLY_v2/output/output_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p4_PU30to40.root' % jst,
     'type': '--calib',
     'args': '--detail',
     'title': 'Fall15 MC, PU30-40, Stage 2 + bitwise Layer 1 + Layer 1 calibs, no L1JEC, Jet Seed Threshold %d GeV' % jst,
     'dest': None}])
    # checkcal plots
    CONFIGS.extend([
    {'input': '/hdfs/L1JEC/CMSSW_8_0_2/L1JetEnergyCorrections/Stage2_HF_QCDFall15_16Mar_int-v14_layer1_noL1JEC_jst%d_RAWONLY/check/check_QCDFlatFall15NoPU_MP_ak4_ref10to5000_l10to5000_dr0p4_maxPt1022.root' % jst,
     'type': '--checkcal',
     'args': '--detail',
     'title': 'Fall15 MC, 0PU, Stage 2 + bitwise Layer 1 + Layer 1 calibs, no L1JEC, Jet Seed Threshold %d GeV' % jst,
     'dest': None},
    {'input': '/hdfs/L1JEC/CMSSW_8_0_2/L1JetEnergyCorrections/Stage2_HF_QCDFall15_16Mar_int-v14_layer1_noL1JEC_jst%d_RAWONLY/check/check_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p4_PU0to10_maxPt1022.root' % jst,
     'type': '--checkcal',
     'args': '--detail',
     'title': 'Fall15 MC, PU0-10, Stage 2 + bitwise Layer 1 + Layer 1 calibs, no L1JEC, Jet Seed Threshold %d GeV' % jst,
     'dest': None},
    {'input': '/hdfs/L1JEC/CMSSW_8_0_2/L1JetEnergyCorrections/Stage2_HF_QCDFall15_16Mar_int-v14_layer1_noL1JEC_jst%d_RAWONLY/check/check_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p4_PU15to25_maxPt1022.root' % jst,
     'type': '--checkcal',
     'args': '--detail',
     'title': 'Fall15 MC, PU15-25, Stage 2 + bitwise Layer 1 + Layer 1 calibs, no L1JEC, Jet Seed Threshold %d GeV' % jst,
     'dest': None},
    {'input': '/hdfs/L1JEC/CMSSW_8_0_2/L1JetEnergyCorrections/Stage2_HF_QCDFall15_16Mar_int-v14_layer1_noL1JEC_jst%d_RAWONLY/check/check_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p4_PU30to40_maxPt1022.root' % jst,
     'type': '--checkcal',
     'args': '--detail',
     'title': 'Fall15 MC, PU30-40, Stage 2 + bitwise Layer 1 + Layer 1 calibs, no L1JEC, Jet Seed Threshold %d GeV' % jst,
     'dest': None}])

# Directory for logs (should be on /storage)
# Will be created automatically by htcondenser
datestamp = strftime("%d_%b_%y")
LOG_DIR = '/storage/%s/L1JEC/%s/L1JetEnergyCorrections/jobs/showoff/%s' % (os.environ['LOGNAME'], os.environ['CMSSW_VERSION'], datestamp)


def submit_all_showoff_jobs(configs, log_dir):
    common_input_files = ['../showoffPlots.py', '../binning.py', '../common_utils.py', '../runCalibration.py']

    for config in configs:
        # auto-generate output dir
        if not config['dest']:
            out_dir = os.path.dirname(config['input'])
            config['dest'] = out_dir
            log.info('Auto-setting output dir to %s', config['dest'])

        # setup ZIP filename
        filename = os.path.basename(config['input'])
        out_dir = '_'.join(['showoff'] + filename.replace(".root", "").split('_')[1:])
        zip_filename = os.path.basename(out_dir) + '.tar.gz'

        arg_str = ' '.join(['showoffPlots.py', config['type'], config['input'],
                            config['args'], '--oDir', config['dest'],
                            '--title="%s"' % config['title'], '--zip', zip_filename,
                            '--gifs', '--gifexe', '/software/ra12451/ImageMagick-install/bin/convert'])
        log.debug(arg_str)
        submit_showoff_job(arg_str=arg_str, out_dir=config['dest'],
                           log_dir=log_dir, common_input_files=common_input_files,
                           output_files=[zip_filename])


def submit_showoff_job(arg_str, out_dir, log_dir, common_input_files, output_files):
    log.debug(arg_str)
    log_stem = 'showoff.$(cluster).$(process)'
    timestamp = strftime("%H%M%S")
    showoff_jobs = ht.JobSet(exe='python', copy_exe=False,
                             filename=os.path.join(log_dir, 'submit_showoff_%s.condor' % timestamp),
                             setup_script='worker_setup.sh',
                             share_exe_setup=True,
                             out_dir=log_dir, out_file=log_stem + '.out',
                             err_dir=log_dir, err_file=log_stem + '.err',
                             log_dir=log_dir, log_file=log_stem + '.log',
                             cpus=1, memory='100MB', disk='200MB',
                             transfer_hdfs_input=False,
                             common_input_files=common_input_files,
                             hdfs_store=out_dir)

    # We don't want to stream-write plots to HDFS - easier to make them all on
    # the worker node, zip it up, then transfer to HDFS
    rand_int = randint(0, 1000)
    tmp_oDir = 'showoff_%s_%d' % (timestamp, rand_int)
    if '--oDir' not in arg_str:
        arg_str += ' --oDir %s' % tmp_oDir
    else:
        arg_str = arg_str.replace('--oDir %s' % out_dir, '--oDir %s' % tmp_oDir)

    sj = ht.Job(name=tmp_oDir, args=arg_str.split(),
                input_files=None, output_files=output_files,
                hdfs_mirror_dir=out_dir)
    showoff_jobs.add_job(sj)
    showoff_jobs.submit()


if __name__ == "__main__":
    submit_all_showoff_jobs(configs=CONFIGS, log_dir=LOG_DIR)
