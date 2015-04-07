import FWCore.ParameterSet.Config as cms

"""
Make L1Ntuples from RAW, for use in L1JetEnergyCorrections

Legacy GCT setup
"""

process = cms.Process("L1NTUPLE")

# import of standard configurations
process.load('Configuration/StandardSequences/Services_cff')
process.load('FWCore/MessageService/MessageLogger_cfi')
process.load('Configuration/StandardSequences/SimL1Emulator_cff')
process.load("Configuration.StandardSequences.RawToDigi_Data_cff")
# process.load("Configuration.StandardSequences.RawToDigi_cff")
process.load('Configuration.StandardSequences.L1Reco_cff')
process.load('Configuration.StandardSequences.Reconstruction_cff')
process.load('Configuration/StandardSequences/EndOfProcess_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration/StandardSequences/MagneticField_AutoFromDBCurrent_cff')
process.load('Configuration/StandardSequences/FrontierConditions_GlobalTag_cff')
# process.load("JetMETCorrections.Configuration.DefaultJEC_cff")

process.MessageLogger.cerr.FwkReport.reportEvery = 200
process.MessageLogger.suppressWarning = cms.untracked.vstring(
    "l1ExtraTreeProducer",
    "l1ExtraTreeProducerGctIntern",
    "l1ExtraTreeProducerGenAk5",
    "l1ExtraTreeProducerGenAk4",
    "csctfDigis"
    )

# L1 raw to digi options
process.gctDigis.numberOfGctSamplesToUnpack = cms.uint32(5)
process.l1extraParticles.centralBxOnly = cms.bool(False)

# L1 ntuple producers
import L1TriggerDPG.L1Ntuples.l1NtupleProducer_cfi 
# process.load("L1TriggerDPG.L1Ntuples.l1NtupleProducer_cfi")

process.load("L1TriggerDPG.L1Ntuples.l1ExtraTreeProducer_cfi")
process.load("L1TriggerDPG.L1Ntuples.l1RecoTreeProducer_cfi")
process.load("L1TriggerDPG.L1Ntuples.l1MenuTreeProducer_cfi")
process.load("L1TriggerDPG.L1Ntuples.l1MuonRecoTreeProducer_cfi")
process.load("EventFilter.L1GlobalTriggerRawToDigi.l1GtTriggerMenuLite_cfi")

##############################
# GCT internal jet collection
##############################
# Make GCT internal jet collection
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

###########################################################
# Load new GCT jet calibration coefficients - edit the l1GctConfig file
# accordingly.
# Since it's an ESProducer, no need to put it in process.p
###########################################################
# TODO: check against GlobalTag
# process.load("L1Trigger.L1JetEnergyCorrections.l1GctConfig_POSTLS162_V2_cfi")

######################################
# To check GCT config
# Need to enable in process.p as well
######################################
# process.load("L1TriggerConfig.GctConfigProducers.l1GctConfigDump_cfi")
# process.MessageLogger.cout.placeholder = cms.untracked.bool(False)
# process.MessageLogger.cout.threshold = cms.untracked.string('DEBUG')
# process.MessageLogger.cerr.threshold = cms.untracked.string('DEBUG')
# process.MessageLogger.debugModules = cms.untracked.vstring('l1GctConfigDump')

process.p = cms.Path(
    process.RawToDigi
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
    # +process.l1GctConfigDump # for print GCT config - not needed for production normally
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
process.GlobalTag.globaltag = cms.string('PHYS14_ST_V1::All') # for Phys14 AVE30BX50 sample

SkipEvent = cms.untracked.vstring('ProductNotFound')

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

# readFiles = cms.untracked.vstring()
# readFiles = cms.untracked.vstring('file:/afs/cern.ch/work/r/raggleto/L1JEC/CMSSW_7_2_0_pre7/src/L1TriggerDPG/L1Ntuples/test/QCD_GEN_SIM_RAW.root')
process.source = cms.Source ("PoolSource",
                             # fileNames = readFiles,
                            fileNames = cms.untracked.vstring('root://xrootd.unl.edu//store/mc/Spring14dr/QCD_Pt-15to3000_Tune4C_Flat_13TeV_pythia8/GEN-SIM-RAW/Flat20to50_POSTLS170_V5-v1/00000/02029D87-36DE-E311-B786-20CF3027A56B.root')
                            # fileNames = cms.untracked.vstring('root://xrootd.unl.edu//store/mc/Phys14DR/QCD_Pt-170to300_Tune4C_13TeV_pythia8/GEN-SIM-RAW/AVE30BX50_tsg_castor_PHYS14_ST_V1-v1/00000/025271B2-DAA8-E411-BB6E-002590D94F8E.root')
                             # fileNames = cms.untracked.vstring('root://xrootd.unl.edu//store/mc/Fall13dr/QCD_Pt-80to120_Tune4C_13TeV_pythia8/GEN-SIM-RAW/castor_tsg_PU40bx50_POSTLS162_V2-v1/00000/000AE06B-22A7-E311-BE0F-0025905A6138.root'),
                            )


## TTbar samples (server error)
# readFiles.extend( [
#     'root://xrootd.unl.edu//store/mc/Fall13dr/TT_Tune4C_13TeV-pythia8-tauola/GEN-SIM-RAW/tsg_PU40bx50_POSTLS162_V2-v1/00000/040974D0-3A75-E311-B258-002590596484.root',
#     'root://xrootd.unl.edu//store/mc/Fall13dr/TT_Tune4C_13TeV-pythia8-tauola/GEN-SIM-RAW/tsg_PU40bx50_POSTLS162_V2-v1/00000/04A84408-3975-E311-9724-002618943856.root',
#     'root://xrootd.unl.edu//store/mc/Fall13dr/TT_Tune4C_13TeV-pythia8-tauola/GEN-SIM-RAW/tsg_PU40bx50_POSTLS162_V2-v1/00000/0636E18D-5975-E311-85AB-00261894386A.root',
#     'root://xrootd.unl.edu//store/mc/Fall13dr/TT_Tune4C_13TeV-pythia8-tauola/GEN-SIM-RAW/tsg_PU40bx50_POSTLS162_V2-v1/00000/02ECF824-4E75-E311-BB0F-0026189438CE.root'
#     ])

# readFiles.extend( [
#     'root://xrootd.unl.edu//store/mc/Fall13dr/TT_Tune4C_13TeV-pythia8-tauola/GEN-SIM-RAW/tsg_PU20bx25_POSTLS162_V2-v1/00000/00D33AA9-326D-E311-AB31-003048678E92.root',
#     'root://xrootd.unl.edu//store/mc/Fall13dr/TT_Tune4C_13TeV-pythia8-tauola/GEN-SIM-RAW/tsg_PU20bx25_POSTLS162_V2-v1/00000/00E2DAC5-8A6C-E311-A2F6-0025905A610C.root',
#     'root://xrootd.unl.edu//store/mc/Fall13dr/TT_Tune4C_13TeV-pythia8-tauola/GEN-SIM-RAW/tsg_PU20bx25_POSTLS162_V2-v1/00000/00FE3096-476D-E311-8608-0026189437FD.root',
#     'root://xrootd.unl.edu//store/mc/Fall13dr/TT_Tune4C_13TeV-pythia8-tauola/GEN-SIM-RAW/tsg_PU20bx25_POSTLS162_V2-v1/00000/0239DBE7-0D91-E311-A208-003048FFCB96.root'
#     ])

# QCD flat samples
# readFiles.extend( [
#     'root://xrootd.unl.edu//store/mc/Spring14dr/QCD_Pt-15to3000_Tune4C_Flat_13TeV_pythia8/GEN-SIM-RAW/Flat20to50_POSTLS170_V5-v1/00000/02029D87-36DE-E311-B786-20CF3027A56B.root',
#     'root://xrootd.unl.edu//store/mc/Spring14dr/QCD_Pt-15to3000_Tune4C_Flat_13TeV_pythia8/GEN-SIM-RAW/Flat20to50_POSTLS170_V5-v1/00000/0238CDC9-7FDD-E311-97F9-002590D0B0AC.root',
#     'root://xrootd.unl.edu//store/mc/Spring14dr/QCD_Pt-15to3000_Tune4C_Flat_13TeV_pythia8/GEN-SIM-RAW/Flat20to50_POSTLS170_V5-v1/00000/023975FD-EDDD-E311-BB09-E0CB4E19F9AC.root',
#     'root://xrootd.unl.edu//store/mc/Spring14dr/QCD_Pt-15to3000_Tune4C_Flat_13TeV_pythia8/GEN-SIM-RAW/Flat20to50_POSTLS170_V5-v1/00000/023B6D4D-D1DD-E311-8DA2-90E6BA19A20B.root'
#     ])

## QCD samples
# readFiles.extend( [
#     'root://xrootd.unl.edu//store/mc/Fall13dr/QCD_Pt-80to120_Tune4C_13TeV_pythia8/GEN-SIM-RAW/castor_tsg_PU40bx50_POSTLS162_V2-v1/00000/04351463-4AA7-E311-A764-002618943845.root',
#     'root://xrootd.unl.edu//store/mc/Fall13dr/QCD_Pt-80to120_Tune4C_13TeV_pythia8/GEN-SIM-RAW/castor_tsg_PU40bx50_POSTLS162_V2-v1/00000/046A411C-25A7-E311-9B65-00304867C1BA.root',
#     'root://xrootd.unl.edu//store/mc/Fall13dr/QCD_Pt-80to120_Tune4C_13TeV_pythia8/GEN-SIM-RAW/castor_tsg_PU40bx50_POSTLS162_V2-v1/00000/049CCC9A-4DA7-E311-BFC4-0025905A610A.root',
#     'root://xrootd.unl.edu//store/mc/Fall13dr/QCD_Pt-80to120_Tune4C_13TeV_pythia8/GEN-SIM-RAW/castor_tsg_PU40bx50_POSTLS162_V2-v1/00000/04A666AD-41A7-E311-AF99-0025905A60DE.root'
#     ])

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