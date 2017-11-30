from CRABClient.UserUtilities import config
config = config()

config.General.requestName = 'run276542_JetHTReReco_HF_L1JEC_30112017_ICL'
config.General.transferLogs = True

config.JobType.pluginName = 'Analysis'
# Name of the CMSSW configuration file
config.JobType.psetName = '../python/ntuple_maker_L1PF_Nov_2017.py'
# config.JobType.inputFiles = ['Summer15_25nsV6_DATA.db']

config.Data.inputDataset = '/JetHT/Run2016G-07Aug17-v1/AOD'
config.Data.secondaryInputDataset = '/JetHT/Run2016G-v1/RAW'

config.Data.splitting = 'LumiBased'
config.Data.unitsPerJob = 4
config.Data.publication = False
# This string is used to construct the output dataset name
config.Data.outputDatasetTag = 'run276542_JetHTReReco_HF_L1JEC_30112017_ICL'

# These values only make sense for processing data
#    Select input data based on a lumi mask
config.Data.lumiMask = 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions16/13TeV/Final/Cert_271036-284044_13TeV_PromptReco_Collisions16_JSON.txt'
#    Select input data based on run-ranges
config.Data.runRange = '276542'

# Where the output files will be transmitted to
# config.Site.storageSite = 'T2_UK_SGrid_RALPP'
config.Site.storageSite = 'T2_UK_London_IC'
