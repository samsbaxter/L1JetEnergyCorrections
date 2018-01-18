"""
CRAB3 template config for more specific configs (See crab dir)
"""

from CRABClient.UserUtilities import config
config = config()


config.General.transferLogs = True
config.JobType.pluginName  = 'Analysis'
config.Data.secondaryInputDataset = '/JetHT/Run2016G-v1/RAW'
config.Data.splitting = 'LumiBased'
config.Data.lumiMask = 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions16/13TeV/Final/Cert_271036-284044_13TeV_PromptReco_Collisions16_JSON.txt'
#config.Data.runRange='278820'
config.Data.publication = False

# Where the output files will be transmitted to
config.Site.storageSite = 'T2_UK_London_IC'
# config.Site.storageSite = 'T2_UK_SGrid_RALPP'
