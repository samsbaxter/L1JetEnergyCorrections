import FWCore.ParameterSet.Config as cms

"""
Minimal working example of RawToDigi to compare the output from
the unpacker (gctDigis), and the TPs + RCT emulator + GCT emulator chain.
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
process.load('Configuration/StandardSequences/FrontierConditions_GlobalTag_cff')

process.MessageLogger.cerr.FwkReport.reportEvery = 200
process.MessageLogger.suppressWarning = cms.untracked.vstring(
    "csctfDigis",
    "l1ExtraTreeProducerRCT",
    "l1ExtraTreeProducer"
    )

process.gctDigis.numberOfGctSamplesToUnpack = cms.uint32(1)

# GCT emulator run from unpacker
process.simGctDigis.inputLabel = cms.InputTag('gctDigis')

# GCT emulator run from RCT emulator

# HACK NUMBER 1 & 2 (a la Mambo no. 5)
# Remake the HCAL TPs since hcalDigis outputs nothing
# But make sure you use the unsupressed digis, not the hcalDigis
process.load('SimCalorimetry.HcalTrigPrimProducers.hcaltpdigi_cff')
process.simHcalTriggerPrimitiveDigis.inputLabel = cms.VInputTag(
    cms.InputTag('simHcalUnsuppressedDigis'),
    cms.InputTag('simHcalUnsuppressedDigis')
)
# Rerun the RCT emulator using the TPs
process.simRctDigis.hcalDigis = cms.VInputTag(cms.InputTag('simHcalTriggerPrimitiveDigis'))
process.simRctDigis.ecalDigis = cms.VInputTag(cms.InputTag('ecalDigis', 'EcalTriggerPrimitives' ))
# HACK NUMBER 3: setup the RCT config properly.
# The GlobalTag DOES NOT setup the RCT params - you have to load the cff *manually*
# At least, as of 23/4/15 this is the case. Check with Maria Cepeda/Mike Mulhearn
process.load('L1Trigger.L1TCalorimeter.caloStage1RCTLuts_cff')
# Incase you want to test how the RCT is configured
# (may need L1TriggerConfig/RCTConfigProducers)
process.l1RCTParametersTest = cms.EDAnalyzer('L1RCTParametersTester')
# process.l1RCTChannelMaskTest = cms.EDAnalyzer('L1RCTChannelMaskTester')
# process.l1RCTOutputScalesTest = cms.EDAnalyzer('L1ScalesTester')
# process.printGlobalTagL1Rct = cms.Sequence(process.l1RCTParametersTest*process.l1RCTChannelMaskTest*process.l1RCTOutputScalesTest)

# Now rerun the GCT emulator using those re-made regions
# Wahey, no haxs here.
process.simGctDigisRCT = process.simGctDigis.clone()
process.simGctDigisRCT.inputLabel = cms.InputTag('simRctDigis')


# L1 ntuple producers
process.load("L1TriggerDPG.L1Ntuples.l1ExtraTreeProducer_cfi")
# from the unpacker
process.l1extraParticles.centralBxOnly = cms.bool(True)
process.l1ExtraTreeProducerRCT = process.l1ExtraTreeProducer.clone()
# from the TP->RCT->GCT chain
process.l1extraParticlesRCT = process.l1extraParticles.clone()
process.l1extraParticlesRCT.centralJetSource = cms.InputTag("simGctDigisRCT","cenJets")
process.l1extraParticlesRCT.forwardJetSource = cms.InputTag("simGctDigisRCT","fwdJets")
process.l1ExtraTreeProducerRCT.cenJetLabel = cms.untracked.InputTag("l1extraParticlesRCT:Central")
process.l1ExtraTreeProducerRCT.fwdJetLabel = cms.untracked.InputTag("l1extraParticlesRCT:Forward")

##############################
# New RCT calibs
##############################
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


process.p = cms.Path(
    process.RawToDigi
    +process.simHcalTriggerPrimitiveDigis
    +process.simGctDigis
    +process.l1extraParticles
    +process.l1ExtraTreeProducer
    +process.simRctDigis
    +process.simGctDigisRCT
    +process.l1extraParticlesRCT
    +process.l1ExtraTreeProducerRCT
    +process.l1RCTParametersTest
    # +process.printGlobalTagL1Rct
)


################################
# Job options for filenames, etc
################################

# output file
process.TFileService = cms.Service("TFileService",
    fileName = cms.string('L1Tree_test.root')
)

process.GlobalTag.globaltag = cms.string('PHYS14_ST_V1::All') # for Phys14 AVE30BX50 sample

SkipEvent = cms.untracked.vstring('ProductNotFound')

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(1) )

process.source = cms.Source ("PoolSource",
                            fileNames = cms.untracked.vstring('root://xrootd.unl.edu//store/mc/Phys14DR/QCD_Pt-80to120_Tune4C_13TeV_pythia8/GEN-SIM-RAW/AVE30BX50_tsg_castor_PHYS14_ST_V1-v1/00000/001CB7A6-E28A-E411-B76F-0025905A611C.root')
                            )
# Only use the following bits if you want the EDM contents output to file as well
# Handy for debugging
process.output = cms.OutputModule(
    "PoolOutputModule",
    outputCommands = cms.untracked.vstring(
        # 'keep *'
        'drop *',
        'keep *_gctDigis_*_*',
        'keep *_simGctDigis_*_*',
        'keep *_simRctDigis_*_*',
        'keep *_simGctDigisRCT_*_*',
        'keep *_hcalDigis_*_*',
        'keep *_ecalDigis_*_*',
        'keep *_simHcalUnsuppressedDigis_*_*'
        ),
    fileName = cms.untracked.string('SimGCTEmulator_test.root')
    )

process.output_step = cms.EndPath(process.output)

process.schedule = cms.Schedule(
    process.p,
    process.output_step
    )
