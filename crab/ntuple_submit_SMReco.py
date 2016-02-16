from CRABClient.UserUtilities import config
config = config()

config.General.requestName = 'run260627_SingleMuReReco_HF_L1JEC_2779cb0_Bristol'
config.General.transferLogs = True

config.JobType.pluginName = 'Analysis'
# Name of the CMSSW configuration file
config.JobType.psetName = '../python/ntuple_maker_SMReco.py'
# config.JobType.inputFiles = ['Summer15_25nsV6_DATA.db']

config.Data.inputDataset = '/SingleMuon/Run2015D-16Dec2015-v1/AOD'
config.Data.secondaryInputDataset = '/SingleMuon/Run2015D-v1/RAW'

config.Data.splitting = 'LumiBased'
config.Data.unitsPerJob = 4
config.Data.publication = False
# This string is used to construct the output dataset name
config.Data.outputDatasetTag = 'run260627_SingleMuReReco_HF_L1JEC_2779cb0'

# These values only make sense for processing data
#    Select input data based on a lumi mask
config.Data.lumiMask = 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions15/13TeV/Cert_246908-260627_13TeV_PromptReco_Collisions15_25ns_JSON_v2.txt'
#    Select input data based on run-ranges
config.Data.runRange = '260627'

# Where the output files will be transmitted to
# config.Site.storageSite = 'T2_UK_SGrid_RALPP'
config.Site.storageSite = 'T2_UK_SGrid_Bristol'
