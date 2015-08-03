#!/usr/bin/env python

"""
Wrapper for python code to run on condor. Have to do it this way,
becasue we can't stream to hdfs, so have to manually edit the output file path
to some temporary file, then move it to hdfs afterwards.

MASSIVE PAIN IN THE ARSE

"""

import sys
import re
import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("filestem", help="stem for output file e.g. resolution, output, check ...")
parser.add_argument("command", help="command that you would run e.g. python runCalibration.py pairs.root output.root", nargs=argparse.REMAINDER)
args = parser.parse_args()

print args
outputname = ""
tmpname = "temp.root"

commands = args.command
for i, opt in enumerate(commands):
    if re.match(r"/hdfs/user/ra12451/L1JEC/CMSSW_\d_\d_.*/src/L1Trigger/L1JetEnergyCorrections/.*/%s.*" % args.filestem, opt):
        outputname=opt
        print opt
        commands[i] = tmpname

print ' '.join(commands)

subprocess.call(commands)

cmd = "mv %s %s" % (tmpname, outputname)
print cmd
subprocess.call(cmd.split())