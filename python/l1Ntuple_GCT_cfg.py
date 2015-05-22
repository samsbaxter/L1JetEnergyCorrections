import FWCore.ParameterSet.Config as cms

"""
Make L1Ntuples from RAW, for use in L1JetEnergyCorrections

Legacy GCT setup, using regions from the unpacker
See other configs if you want to re-run the RCT!
"""

process = cms.Process("L1NTUPLE")

# import of standard configurations
process.load('Configuration/StandardSequences/Services_cff')
process.load('FWCore/MessageService/MessageLogger_cfi')
process.load('Configuration/StandardSequences/SimL1Emulator_cff')
process.load("Configuration.StandardSequences.RawToDigi_Data_cff")
process.load('Configuration.StandardSequences.L1Reco_cff')  # l1extraParticles from here
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


# L1 ntuple producers
import L1TriggerDPG.L1Ntuples.l1NtupleProducer_cfi 
process.load("L1TriggerDPG.L1Ntuples.l1ExtraTreeProducer_cfi")

##############################
# Put correct GCT jet collection in L1Extra to ensure it picks up any new calibs
##############################
process.l1extraParticles.centralBxOnly = cms.bool(True)
process.l1extraParticles.tauJetSource = cms.InputTag("simGctDigis","tauJets")
process.l1extraParticles.etTotalSource = cms.InputTag("simGctDigis")
process.l1extraParticles.nonIsolatedEmSource = cms.InputTag("simGctDigis","nonIsoEm")
process.l1extraParticles.htMissSource = cms.InputTag("simGctDigis")
process.l1extraParticles.etMissSource = cms.InputTag("simGctDigis")
process.l1extraParticles.produceMuonParticles = cms.bool(False)
process.l1extraParticles.hfRingEtSumsSource = cms.InputTag("simGctDigis")
process.l1extraParticles.forwardJetSource = cms.InputTag("simGctDigis","forJets")
process.l1extraParticles.ignoreHtMiss = cms.bool(False)
process.l1extraParticles.centralJetSource = cms.InputTag("simGctDigis","cenJets")
process.l1extraParticles.produceCaloParticles = cms.bool(True)
process.l1extraParticles.muonSource = cms.InputTag("gtDigis")
process.l1extraParticles.isolatedEmSource = cms.InputTag("simGctDigis","isoEm")
process.l1extraParticles.etHadSource = cms.InputTag("simGctDigis")
process.l1extraParticles.hfRingBitCountsSource = cms.InputTag("simGctDigis")

##############################
# GCT internal jet collection
##############################
# Make GCT internal jet collection using regions from unpacker
process.gctDigis.numberOfGctSamplesToUnpack = cms.uint32(1)
process.simGctDigis.inputLabel = cms.InputTag('gctDigis')
process.simGctDigis.writeInternalData = cms.bool(True)

# Convert Gct Internal jets to L1JetParticles
process.gctInternJetToL1Jet = cms.EDProducer('L1GctInternJetToL1Jet',
    gctInternJetSource = cms.InputTag("simGctDigis")
)
# Store in another L1ExtraTree as cenJets
process.l1ExtraTreeProducerGctIntern = process.l1ExtraTreeProducer.clone()
process.l1ExtraTreeProducerGctIntern.nonIsoEmLabel = cms.untracked.InputTag("")
process.l1ExtraTreeProducerGctIntern.isoEmLabel = cms.untracked.InputTag("")
process.l1ExtraTreeProducerGctIntern.tauJetLabel = cms.untracked.InputTag("")
process.l1ExtraTreeProducerGctIntern.isoTauJetLabel = cms.untracked.InputTag("")
process.l1ExtraTreeProducerGctIntern.fwdJetLabel = cms.untracked.InputTag("")
process.l1ExtraTreeProducerGctIntern.muonLabel = cms.untracked.InputTag("")
process.l1ExtraTreeProducerGctIntern.metLabel = cms.untracked.InputTag("")
process.l1ExtraTreeProducerGctIntern.mhtLabel = cms.untracked.InputTag("")
process.l1ExtraTreeProducerGctIntern.hfRingsLabel = cms.untracked.InputTag("")
process.l1ExtraTreeProducerGctIntern.cenJetLabel = cms.untracked.InputTag("gctInternJetToL1Jet:GctInternalJets")
process.l1ExtraTreeProducerGctIntern.maxL1Extra = cms.uint32(50)

##############################
# Do ak5 GenJets
##############################
# Convert ak5 genjets to L1JetParticle objects, store in another L1ExtraTree as cenJets
process.genJetToL1JetAk5 = cms.EDProducer("GenJetToL1Jet",
    genJetSource = cms.InputTag("ak5GenJets")
)
process.l1ExtraTreeProducerGenAk5 = process.l1ExtraTreeProducerGctIntern.clone()
process.l1ExtraTreeProducerGenAk5.cenJetLabel = cms.untracked.InputTag("genJetToL1JetAk5:GenJets")
process.l1ExtraTreeProducerGenAk5.maxL1Extra = cms.uint32(50)

##############################
# Do ak4 GenJets
##############################
# Need to make ak4, not included in GEN-SIM-RAW
# process.load('RecoJets.Configuration.GenJetParticles_cff')
# process.load('RecoJets.Configuration.RecoGenJets_cff')
# process.antiktGenJets = cms.Sequence(process.genJetParticles*process.ak4GenJets)

# Convert ak4 genjets to L1JetParticle objects
process.genJetToL1JetAk4 = cms.EDProducer("GenJetToL1Jet",
    genJetSource = cms.InputTag("ak4GenJets")
)
# Put in another L1ExtraTree as cenJets
process.l1ExtraTreeProducerGenAk4 = process.l1ExtraTreeProducerGctIntern.clone()
process.l1ExtraTreeProducerGenAk4.cenJetLabel = cms.untracked.InputTag("genJetToL1JetAk4:GenJets")
process.l1ExtraTreeProducerGenAk4.maxL1Extra = cms.uint32(50)

##############################
# Store PU info (nvtx, etc)
##############################
process.puInfo = cms.EDAnalyzer("PileupInfo",
    pileupInfoSource = cms.InputTag("addPileupInfo")
)

###########################################################
# Load new GCT jet calibration coefficients - edit the l1GctConfig file
# accordingly.
# Since it's an ESProducer, no need to put it in process.p
###########################################################
# process.load('L1Trigger.L1JetEnergyCorrections.l1GctConfig_720_PHYS14_ST_V1_central_cfi')

process.p = cms.Path(
    process.gctDigis
    # +process.antiktGenJets  # for AK4 GenJet - not needed in Phys14 samples
    +process.simGctDigis
    +process.l1extraParticles
    +process.gctInternJetToL1Jet
    +process.genJetToL1JetAk5
    +process.genJetToL1JetAk4
    +process.l1ExtraTreeProducer # standard gctDigis in cenJet coll
    +process.l1ExtraTreeProducerGctIntern # gctInternal jets in cenJet coll
    +process.l1ExtraTreeProducerGenAk5 # ak5GenJets in cenJet coll
    +process.l1ExtraTreeProducerGenAk4 # ak4GenJets in cenJet coll
    +process.puInfo # store nVtx info
)


################################
# Job options for filenames, etc
################################

# output file
process.TFileService = cms.Service("TFileService",
    fileName = cms.string('L1Tree.root')
)

# process.GlobalTag.globaltag = cms.string('POSTLS162_V2::All')
# process.GlobalTag.globaltag = cms.string('PRE_LS171V9A::All')
# process.GlobalTag.globaltag = cms.string('PHYS14_ST_V1::All') # for Phys14 AVE30BX50 sample
process.GlobalTag.globaltag = cms.string('MCRUN2_74_V6::All') # for Phys14 AVE30BX50 sample

SkipEvent = cms.untracked.vstring('ProductNotFound')

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(100) )

# readFiles = cms.untracked.vstring()
process.source = cms.Source ("PoolSource",
                             # fileNames = readFiles,
                            # fileNames = cms.untracked.vstring('root://xrootd.unl.edu//store/mc/Spring14dr/QCD_Pt-15to3000_Tune4C_Flat_13TeV_pythia8/GEN-SIM-RAW/Flat20to50_POSTLS170_V5-v1/00000/02029D87-36DE-E311-B786-20CF3027A56B.root')
                            # fileNames = cms.untracked.vstring('file:QCD_Pt-80to120_Phys14_AVE30BX50.root')
                            # fileNames = cms.untracked.vstring('root://xrootd.unl.edu//store/mc/Phys14DR/QCD_Pt-80to120_Tune4C_13TeV_pythia8/GEN-SIM-RAW/AVE30BX50_tsg_castor_PHYS14_ST_V1-v1/00000/001CB7A6-E28A-E411-B76F-0025905A611C.root')
                            fileNames = cms.untracked.vstring('root://xrootd.unl.edu//store/mc/RunIISpring15Digi74/QCD_Pt_50to80_TuneCUETP8M1_13TeV_pythia8/GEN-SIM-RAW/AVE_30_BX_50ns_tsg_MCRUN2_74_V6-v1/00000/0013D0D5-B9EC-E411-983E-0025905A48E4.root')

                            )

# Only use the following bits if you want the EDM contents output to file as well
# Handy for debugging
process.output = cms.OutputModule(
    "PoolOutputModule",
    outputCommands = cms.untracked.vstring('keep *'),
    # outputCommands = cms.untracked.vstring(
    #     'drop *',

    #     # Keep GCT jets
    #     'keep *_gctDigis_*_*',
    #     'keep *_simGctDigis_*_*',

    #     # Keep GenJets
    #     'keep *_ak5GenJets_*_*',
    #     'keep *_ak4GenJets_*_*'
    #     ),
    fileName = cms.untracked.string('SimGCTEmulator.root')
    )

process.output_step = cms.EndPath(process.output)

process.schedule = cms.Schedule(
    process.p
    # process.output_step
    )
