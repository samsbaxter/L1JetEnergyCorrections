from WMCore.Configuration import Configuration

config = Configuration()

config.section_("General")
config.General.requestName   = 'l1ntuple_ttbar_PU20bx25'
config.General.transferLogs = True

config.section_("JobType")
config.JobType.pluginName  = 'Analysis'
# Name of the CMSSW configuration file
config.JobType.psetName    = 'l1Ntuple_cfg.py'

config.section_("Data")
config.Data.inputDataset = '/TT_Tune4C_13TeV-pythia8-tauola/Fall13dr-tsg_PU20bx25_POSTLS162_V2-v1/GEN-SIM-RAW'
config.Data.splitting = 'FileBased'
config.Data.unitsPerJob = 100
config.Data.publication = False
# This string is used to construct the output dataset name
# config.Data.publishDataName = 'CRAB3-test-ttbar'

# These values only make sense for processing data
#    Select input data based on a lumi mask
# config.Data.lumiMask = 'Cert_190456-208686_8TeV_PromptReco_Collisions12_JSON.txt'
#    Select input data based on run-ranges
# config.Data.runRange = '190456-194076'

config.section_("Site")
# Where the output files will be transmitted to
config.Site.storageSite = 'T2_UK_SGrid_Bristol'