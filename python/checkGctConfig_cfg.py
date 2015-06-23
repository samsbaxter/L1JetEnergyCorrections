import FWCore.ParameterSet.Config as cms

"""
Check GCT config params. Important when you want to implement a new set of JEC
via  L1GctConfigProducers.

Legacy GCT setup
"""

process = cms.Process("L1NTUPLE")

# import of standard configurations
process.load('Configuration/StandardSequences/Services_cff')
process.load('FWCore/MessageService/MessageLogger_cfi')
process.load('Configuration/StandardSequences/SimL1Emulator_cff')
process.load("Configuration.StandardSequences.RawToDigi_Data_cff")
process.load('Configuration.StandardSequences.L1Reco_cff') # l1extraParticles from here
process.load('Configuration.StandardSequences.Reconstruction_cff')
process.load('Configuration/StandardSequences/EndOfProcess_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration/StandardSequences/MagneticField_AutoFromDBCurrent_cff')

# Old GlobalTags
# process.load('Configuration/StandardSequences/FrontierConditions_GlobalTag_cff')

# New Global Tags
process.load('Configuration/StandardSequences/FrontierConditions_GlobalTag_condDBv2_cff')
from Configuration.AlCa.GlobalTag_condDBv2 import GlobalTag

# process.GlobalTag.globaltag = cms.string('PHYS14_ST_V1::All') # for Phys14 AVE30BX50 sample
process.GlobalTag.globaltag = cms.string('GR_P_V56') # for Phys14 AVE30BX50 sample

######################################
# Testing - check GCT config
# Need to enable in process.p as well
######################################
process.load("L1TriggerConfig.GctConfigProducers.l1GctConfigDump_cfi")
process.MessageLogger.cout.placeholder = cms.untracked.bool(False)
process.MessageLogger.cout.threshold = cms.untracked.string('INFO')
process.MessageLogger.cerr.threshold = cms.untracked.string('DEBUG')
process.MessageLogger.debugModules = cms.untracked.vstring('l1GctConfigDump')

# Load in your new config here to check post-calibration config
# process.load('l1GctConfig_742_PHYS14_ST_V1_central_cfi')

process.p = cms.Path(
    process.l1GctConfigDump # for print GCT config - not needed for production normally
)


################################
# Job options - edit these bits
################################

# output file
process.TFileService = cms.Service("TFileService",
    fileName = cms.string('gctDumpConfig.root')
)

SkipEvent = cms.untracked.vstring('ProductNotFound')

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(1) )

secFiles = cms.untracked.vstring()
process.source = cms.Source ("PoolSource",
                             # fileNames = cms.untracked.vstring('root://xrootd.unl.edu//store/mc/Phys14DR/QCD_Pt-120to170_Tune4C_13TeV_pythia8/GEN-SIM-RAW/AVE30BX50_tsg_castor_PHYS14_ST_V1-v1/00000/008671F0-508B-E411-8D9D-003048FFCC2C.root'),
                             fileNames = cms.untracked.vstring('root://xrootd.unl.edu//store/mc/Phys14DR/QCD_Pt-50to80_Tune4C_13TeV_pythia8/GEN-SIM-RAW/AVE30BX50_tsg_castor_PHYS14_ST_V1-v1/00000/001AA0E6-C58A-E411-9634-0025905A60D6.root'),
                             secondaryFileNames = secFiles
                             )
