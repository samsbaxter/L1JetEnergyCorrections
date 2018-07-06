"""
CRAB3 template config for more specific configs (See crab dir)
"""

from CRABClient.UserUtilities import config
config = config()


config.General.transferLogs = True
config.JobType.pluginName  = 'Analysis'
config.Data.secondaryInputDataset = '/JetHT/Run2017B-v1/RAW'
config.Data.splitting = 'LumiBased'
config.Data.lumiMask = 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions17/13TeV/Final/Cert_294927-306462_13TeV_PromptReco_Collisions17_JSON.txt'
config.Data.runRange='301914'
config.Data.ignoreLocality = True
config.Data.publication = False

config.Site.whitelist = ['T2_CH_CERN']
#config.Site.ignoreGlobalBlacklist = True
# Where the output files will be transmitted to
config.Site.storageSite = 'T2_UK_London_IC'
# config.Site.storageSite = 'T2_UK_SGrid_RALPP'
