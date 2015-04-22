import FWCore.ParameterSet.Config as cms

"""
Minimal working example of RawToDigi to demostrate that the output from
the GCT emulator is different depending on whether it is fed the output from
the unpacker (gctDigis), or whether you pass the TP digis to the RCT emulator,
and then send the regions it produces to the GCT emulator (simGctDigisRCT)

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
    "csctfDigis"
    )

process.gctDigis.numberOfGctSamplesToUnpack = cms.uint32(1)

# GCT emulator run from unpacker
process.simGctDigis.inputLabel = cms.InputTag('gctDigis')

# GCT emulator run from RCT emulator
process.simRctDigis.hcalDigis = cms.VInputTag(cms.InputTag('hcalDigis'))
process.simRctDigis.ecalDigis = cms.VInputTag(cms.InputTag('ecalDigis', 'EcalTriggerPrimitives' ))
process.simGctDigisRCT = process.simGctDigis.clone()

process.l1extraParticlesRCT = process.l1extraParticles.clone()
process.l1extraParticlesRCT.centralJetSource = cms.InputTag("simGctDigisRCT","cenJets")
process.l1extraParticlesRCT.forwardJetSource = cms.InputTag("simGctDigisRCT","fwdJets")

# L1 ntuple producers
process.load("L1TriggerDPG.L1Ntuples.l1ExtraTreeProducer_cfi")
process.l1extraParticles.centralBxOnly = cms.bool(True)
process.l1ExtraTreeProducerRCT = process.l1ExtraTreeProducer.clone()
process.l1ExtraTreeProducerRCT.cenJetLabel = cms.untracked.InputTag("l1extraParticlesRCT:Central")
process.l1ExtraTreeProducerRCT.fwdJetLabel = cms.untracked.InputTag("l1extraParticlesRCT:Forward")


process.p = cms.Path(
    process.RawToDigi
    +process.simGctDigis
    +process.l1extraParticles
    +process.l1ExtraTreeProducer
    +process.simRctDigis
    +process.simGctDigisRCT
    +process.l1extraParticlesRCT
    +process.l1ExtraTreeProducerRCT
)


################################
# Job options for filenames, etc
################################

# output file
process.TFileService = cms.Service("TFileService",
    fileName = cms.string('L1Tree.root')
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
        'drop *',
        'keep *_gctDigis_*_*',
        'keep *_simGctDigis_*_*',
        'keep *_simRctDigis_*_*',
        'keep *_simGctDigisRCT_*_*',
        'keep *_hcalDigis_*_*',
        'keep *_ecalDigis_*_*'
        ),
    fileName = cms.untracked.string('SimGCTEmulator.root')
    )

process.output_step = cms.EndPath(process.output)

process.schedule = cms.Schedule(
    process.p,
    process.output_step
    )
