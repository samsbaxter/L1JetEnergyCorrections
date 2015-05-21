import FWCore.ParameterSet.Config as cms

"""
Minimal RawToDigi config

Legacy GCT setup, with option to re-run the RCT to include new RCT calibs.
Produces GCT internal jet collection with finer granularity & no filtering
to do calibrations properly.

YOU MUST RUN WITH CMSSW 74X OR NEWER TO PICK UP THE NEW RCT CALIBS.
"""

##############################
# Some handy options
##############################
# To save the EDM content as well:
# (WARNING: DON'T do this for big production - will be HUGE)
save_EDM = True

# Things to append to L1Ntuple/EDM filename
file_append = "_Spring15"

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
process.load('Configuration/StandardSequences/FrontierConditions_GlobalTag_cff')

process.MessageLogger.cerr.FwkReport.reportEvery = 200
process.MessageLogger.suppressWarning = cms.untracked.vstring(
    "l1ExtraTreeProducer",
    "l1ExtraTreeProducerGctIntern",
    "l1ExtraTreeProducerGenAk5",
    "l1ExtraTreeProducerGenAk4",
    "csctfDigis"
    )

##############################
# Rerun the GCT for internal jet collection
# We will actually use 2 instances of the GCT emulator here for comparison:
#
# - simGctDigis runs over regions from the unpacker (gctDigis)
# - simGctDigisRCT runs over regions from running the RCT emulator again (simRctDigis)
##############################

process.gctDigis.numberOfGctSamplesToUnpack = cms.uint32(1)

# This will actually produce the internal jet collection
process.simGctDigis.writeInternalData = cms.bool(True)

# To pickup new RCT calibrations, we need to remake the regions and pass
# those new regions to the GCT emulator. To rerun the RCT, we need the ECAL
# and HCAL TPs. Unfortunately, there is a bug in the hcalDigis module (until
# 7_3_5?) that doesn't unpack correctly, so you have to remake them.
file_append += "_rerunRCT"

# Remake the HCAL TPs since hcalDigis outputs nothing in CMSSW earlier than 735
# (NOT CHECKED PRECISELY WHICH VERSION, certainly works in 740)
# But make sure you use the unsupressed digis, not the hcalDigis
# process.load('SimCalorimetry.HcalTrigPrimProducers.hcaltpdigi_cff')
# process.simHcalTriggerPrimitiveDigis.inputLabel = cms.VInputTag(
#     cms.InputTag('simHcalUnsuppressedDigis'),
#     cms.InputTag('simHcalUnsuppressedDigis')
# )

# Use this if you want to test a RCTLuts file that isn't in CondDB
# process.load('L1Trigger.L1TCalorimeter.caloStage1RCTLuts_cff')

# Rerun the RCT emulator using the TPs
# If the hcalDigis bug isn't fixed, then instead use:
# process.simRctDigis.hcalDigis = cms.VInputTag(cms.InputTag('simHcalTriggerPrimitiveDigis'))
process.simRctDigis.hcalDigis = cms.VInputTag(cms.InputTag('hcalDigis'))
process.simRctDigis.ecalDigis = cms.VInputTag(cms.InputTag('ecalDigis', 'EcalTriggerPrimitives' ))

# Rerun the GCT emulator using the RCT regions, including intern collections
process.simGctDigisRCT = process.simGctDigis.clone()
process.simGctDigisRCT.inputLabel = cms.InputTag('simRctDigis')

# Alternate GCT emulator, where we just use the regions from the unpacker.
process.simGctDigis.inputLabel = cms.InputTag('gctDigis')

##############################
# New RCT calibs
##############################
print "*** Using new RCT calibs"
from CondCore.DBCommon.CondDBSetup_cfi import CondDBSetup
process.newRCTConfig = cms.ESSource("PoolDBESSource",
    CondDBSetup,
    connect = cms.string('frontier://FrontierPrep/CMS_COND_L1T'),
    DumpStat=cms.untracked.bool(True),
    toGet = cms.VPSet(
        cms.PSet(
           record = cms.string('L1RCTParametersRcd'),
           tag = cms.string('L1RCTParametersRcd_L1TDevelCollisions_ExtendedScaleFactorsV1')
        )
    )
)
process.prefer("newRCTConfig")
file_append += '_newRCT'
process.l1RCTParametersTest = cms.EDAnalyzer("L1RCTParametersTester")  # don't forget to include me in a cms.Path()

process.p = cms.Path(
    # process.RawToDigi
    process.gctDigis # unpack regions, TPs, etc
    +process.ecalDigis
    +process.ecalPreshowerDigis
    +process.scalersRawToDigi
    +process.hcalDigis
    # +process.simHcalTriggerPrimitiveDigis
    +process.simRctDigis
    +process.simGctDigis
    +process.simGctDigisRCT
    +process.l1RCTParametersTest
)


################################
# Job options for filenames, etc
################################

# output file
output_filename = 'L1Tree{0}.root'.format(file_append)
print "*** Writing NTuple to {0}".format(output_filename)

process.TFileService = cms.Service("TFileService",
    fileName = cms.string(output_filename)
)

# process.GlobalTag.globaltag = cms.string('PHYS14_ST_V1::All') # for Phys14 AVE30BX50 sample
process.GlobalTag.globaltag = cms.string('MCRUN2_74_V6::All') # for Spring15 AVE30BX50 sample

SkipEvent = cms.untracked.vstring('ProductNotFound')

process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(1))

# readFiles = cms.untracked.vstring()
process.source = cms.Source ("PoolSource",
                             # fileNames = readFiles,
                            # fileNames = cms.untracked.vstring('root://xrootd.unl.edu//store/mc/Spring14dr/QCD_Pt-15to3000_Tune4C_Flat_13TeV_pythia8/GEN-SIM-RAW/Flat20to50_POSTLS170_V5-v1/00000/02029D87-36DE-E311-B786-20CF3027A56B.root')
                            # fileNames = cms.untracked.vstring('file:QCD_Pt-80to120_Phys14_AVE30BX50.root')
                            # fileNames = cms.untracked.vstring('root://xrootd.unl.edu//store/mc/Phys14DR/QCD_Pt-80to120_Tune4C_13TeV_pythia8/GEN-SIM-RAW/AVE30BX50_tsg_castor_PHYS14_ST_V1-v1/00000/001CB7A6-E28A-E411-B76F-0025905A611C.root')
                            fileNames = cms.untracked.vstring('root://xrootd.unl.edu//store/mc/RunIISpring15Digi74/QCD_Pt_80to120_TuneCUETP8M1_13TeV_pythia8/GEN-SIM-RAW/AVE_30_BX_50ns_tsg_MCRUN2_74_V6-v1/60000/08ABF6F2-C0ED-E411-9597-0025905A60A8.root')
                            )

# The following bits can save the EDM contents output to file as well
# Handy for debugging
edm_filename = 'SimGCTEmulator{0}.root'.format(file_append)
process.output = cms.OutputModule(
    "PoolOutputModule",
    # outputCommands = cms.untracked.vstring('keep *'),
    outputCommands = cms.untracked.vstring(
        'drop *',

        # Keep TPs
        'keep *_simHcalTriggerPrimitiveDigis_*_*',
        'keep *_hcalDigis_*_*',
        'keep *_ecalDigis_*_*',

        # Keep RCT regions
        'keep *_simRctDigis_*_*',

        # Keep GCT jets
        'keep *_gctDigis_*_*',
        'keep *_simGctDigis_*_*',
        'keep *_simGctDigisRCT_*_*',

        # Keep GenJets
        'keep *_ak5GenJets_*_*',
        'keep *_ak4GenJets_*_*'
        ),
    fileName = cms.untracked.string(edm_filename)
    )

process.output_step = cms.EndPath(process.output)

process.schedule = cms.Schedule(process.p)

if save_EDM:
    print "*** Writing EDM to {0}".format(edm_filename)
    process.schedule.append(process.output_step)
