from WMCore.Configuration import Configuration

config = Configuration()

config.section_("General")
job_append = "_stage1_newRCT_noJEC"

# TTbar fall13
config.General.requestName   = 'l1ntuple_ttbar_PU20bx25'+job_append

# QCD flat spring14
# config.General.requestName   = 'l1ntuple_spring14_qcd_15to3000_flat20to50_bx25'+job_append

# RelVal QCD
# config.General.requestName   = 'l1ntuple_relval_qcd_15to3000_CMSSW_7_3_0-MCRUN2_73_GCT'
# config.General.requestName   = 'l1ntuple_relval_ttbar_cmssw_7_3_0_PU50ns'+job_append

config.General.transferLogs = True

config.section_("JobType")
config.JobType.pluginName  = 'Analysis'
# Name of the CMSSW configuration file
# config.JobType.psetName    = '../l1Ntuple_GCT_cfg.py'
config.JobType.psetName    = '../python/SimL1Emulator_Stage1_newRCT.py'

config.section_("Data")
config.Data.splitting = 'FileBased'
config.Data.publication = False

# TTbar fall13
config.Data.inputDataset = '/TT_Tune4C_13TeV-pythia8-tauola/Fall13dr-tsg_PU20bx25_POSTLS162_V2-v1/GEN-SIM-RAW'
config.Data.unitsPerJob = 100

# QCD flat spring14
# config.Data.inputDataset = '/QCD_Pt-15to3000_Tune4C_Flat_13TeV_pythia8/Spring14dr-Flat20to50_POSTLS170_V5-v1/GEN-SIM-RAW'
# config.Data.unitsPerJob = 50

# RelVal QCD
# config.Data.inputDataset = "/RelValQCD_FlatPt_15_3000HS_13/CMSSW_7_3_0-MCRUN2_73_V7-v1/GEN-SIM-DIGI-RAW-HLTDEBUG"
# config.Data.unitsPerJob = 25

# RelVal ttbar
# config.Data.inputDataset = "/RelValTTbar_13/CMSSW_7_3_0-PU50ns_MCRUN2_73_V9_71XGENSIM_FIXGT-v1/GEN-SIM-DIGI-RAW-HLTDEBUG"
# config.Data.unitsPerJob = 25

config.section_("Site")
# Where the output files will be transmitted to
config.Site.storageSite = 'T2_UK_SGrid_Bristol'
