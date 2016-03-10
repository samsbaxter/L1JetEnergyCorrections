"""
CRAB3 simple config.

Blank strings should be filled in!

Change storageSite to somewhere you have write permissions.
"""

from CRABClient.UserUtilities import config
config = config()

config.General.transferLogs = True
config.General.requestName = ""  # put some descriptive name for the set of jobs here

config.JobType.pluginName = 'Analysis'
config.JobType.psetName = ""  # the cmssw config file path
config.JobType.inputFiles = ['Fall15_25nsV2_MC.db']

config.Data.splitting = 'FileBased'
# config.Data.splitting = 'LumiBased'  # use this for data

config.Data.publication = False

config.Data.inputDataset = ""  # your AOD/RECO dataset here
config.Data.useParent = True  # for 2-file solution
config.Data.unitsPerJob = 1

# These values only make sense for processing data:
# Select input data based on a lumi mask
# config.Data.lumiMask = 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions15/13TeV/Cert_246908-260627_13TeV_PromptReco_Collisions15_25ns_JSON_v2.txt'
# Select input data based on run-ranges
# config.Data.runRange = '260627'

# Where the output files will be transmitted to
config.Site.storageSite = 'T2_UK_SGrid_Bristol'
