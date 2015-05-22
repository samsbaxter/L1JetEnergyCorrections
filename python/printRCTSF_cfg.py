import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing
options = VarParsing ('analysis')

process = cms.Process("L1Digis")
# options.inputFiles = '/store/user/ldodd/DYJetsToLL_M-50_13TeV-pythia6/DYJetsToLL_M-50_13TeV-pythia6_Fall13dr-tsg_PU20bx25_POSTLS162_V2-v1/05a81b8d696d27a5c3c2ca036967addd/skim_101_1_XPk.root'
options.inputFiles = 'root://xrootd.unl.edu//store/mc/RunIISpring15Digi74/QCD_Pt_80to120_TuneCUETP8M1_13TeV_pythia8/GEN-SIM-RAW/AVE_30_BX_50ns_tsg_MCRUN2_74_V6-v1/60000/08ABF6F2-C0ED-E411-9597-0025905A60A8.root'
process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(1)
)
process.source = cms.Source(
    "PoolSource",
    fileNames = cms.untracked.vstring(options.inputFiles),
    noEventSort = cms.untracked.bool(True),
    duplicateCheckMode = cms.untracked.string('noDuplicateCheck')
)

from CondCore.DBCommon.CondDBSetup_cfi import CondDBSetup
process.newRCTConfig = cms.ESSource("PoolDBESSource",
     CondDBSetup,
     # Using prep database, presumably by the time the tag is in production, it will be in a global tag.
     connect = cms.string('frontier://FrontierPrep/CMS_COND_L1T'),
     # This is optional, just prints some info about reading the tag
     DumpStat=cms.untracked.bool(True),
     toGet = cms.VPSet(
         cms.PSet(
             record = cms.string('L1RCTParametersRcd'),
             tag = cms.string('L1RCTParametersRcd_L1TDevelCollisions_ExtendedScaleFactorsV1')
         )
     )
)
# This tells the EventSetup to pick this record over whatever is in the global tag.
process.prefer("newRCTConfig") 


process.l1RCTParametersTest = cms.EDAnalyzer("L1RCTParametersTester")  # don't forget to include me in a cms.Path()

process.p1 = cms.Path(process.l1RCTParametersTest)
