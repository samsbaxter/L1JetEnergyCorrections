"""
CRAB3 template config for GCT, Stage 1 specific configs
"""

from WMCore.Configuration import Configuration

config = Configuration()

config.section_("General")
config.General.transferLogs = True

config.section_("JobType")
config.JobType.pluginName  = 'Analysis'

config.section_("Data")
config.Data.splitting = 'FileBased'
config.Data.publication = False

config.section_("Site")
# Where the output files will be transmitted to
# config.Site.storageSite = 'T2_UK_SGrid_Bristol'
config.Site.storageSite = 'T2_UK_SGrid_RALPP'
