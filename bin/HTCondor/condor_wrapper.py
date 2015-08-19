#!/usr/bin/env python

"""
Wrapper for python code to run on condor. Have to do it this way,
becasue we can't stream to hdfs, so have to manually edit the output file path
to some temporary file, then move it to hdfs afterwards.

MASSIVE PAIN IN THE ARSE

"""

import os
import sys
import re
import subprocess
import argparse
import random, string

print "condor_wrapper, innit"
print sys.argv
parser = argparse.ArgumentParser()
parser.add_argument("filestem", help="stem for output file e.g. resolution, output, check ...")
parser.add_argument("command", help="command that you would run e.g. python runCalibration.py pairs.root output.root", nargs=argparse.REMAINDER)
args = parser.parse_args()

print args
outputname = ""
# make unique output filename in case 2 jobs run on same node
random_str = ''.join(random.choice(string.lowercase) for i in xrange(3))
tmpname = "temp_%s.root" % (random_str)

commands = args.command
for i, opt in enumerate(commands):
    if re.match(r"/hdfs/user/ra12451/L1JEC/CMSSW_\d_\d_.*/src/L1Trigger/L1JetEnergyCorrections/.*/%s.*" % args.filestem, opt):
        outputname=opt
        print opt
        commands[i] = tmpname

# Actaully call the commands
print ' '.join(commands)
subprocess.call(commands)

# Copy across to HDFS
# cmd = "mv %s %s" % (tmpname, outputname)
cmd = "hadoop fs -copyFromLocal -f %s %s" % (tmpname, outputname.replace("/hdfs", ""))
print cmd
subprocess.call(cmd.split())

# Remove the temp file
os.remove(tmpname)