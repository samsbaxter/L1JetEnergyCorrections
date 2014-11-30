import FWCore.ParameterSet.Config as cms

# make L1 ntuples from RAW+RECO

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
# process.load("JetMETCorrections.Configuration.DefaultJEC_cff")
process.load('Configuration/StandardSequences/FrontierConditions_GlobalTag_cff')

# process.MessageLogger = cms.Service("MessageLogger",
#                     # suppressWarning=cms.untracked.vstring('l1ExtraTreeProducerGenAk4')
# )
process.MessageLogger.cerr.FwkReport.reportEvery = 200
# process.MessageLogger.debugModules = cms.untracked.vstring("l1extraParticles")
# process.MessageLogger.cout.threshold = cms.untracked.string("DEBUG")
# process.MessageLogger.cerr.threshold = cms.untracked.string("DEBUG")


# output file
process.TFileService = cms.Service("TFileService",
    fileName = cms.string('L1Tree_Fall13_TTbar_PU20bx25.root')
    # fileName = cms.string('L1Tree_Fall13_QCD_Pt80to120_1000.root')
    # fileName = cms.string('L1Tree_Spring14_QCD_Pt-15to3000.root')
)

# L1 raw to digi options
process.gctDigis.numberOfGctSamplesToUnpack = cms.uint32(5)
process.l1extraParticles.centralBxOnly = cms.bool(False)

# L1 ntuple producers
## process.load("L1TriggerDPG.L1Ntuples.l1NtupleProducer_cfi")
import L1TriggerDPG.L1Ntuples.l1NtupleProducer_cfi 
process.l1NtupleProducer = L1TriggerDPG.L1Ntuples.l1NtupleProducer_cfi.l1NtupleProducer.clone()

import L1TriggerDPG.L1Ntuples.l1NtupleProducer_Stage1Layer2_cfi 
process.l1NtupleProducerStage1Layer2 = L1TriggerDPG.L1Ntuples.l1NtupleProducer_Stage1Layer2_cfi.l1NtupleProducer.clone()

process.load("L1TriggerDPG.L1Ntuples.l1RecoTreeProducer_cfi")
process.load("L1TriggerDPG.L1Ntuples.l1ExtraTreeProducer_cfi")
process.load("L1TriggerDPG.L1Ntuples.l1MenuTreeProducer_cfi")
process.load("L1TriggerDPG.L1Ntuples.l1MuonRecoTreeProducer_cfi")
process.load("EventFilter.L1GlobalTriggerRawToDigi.l1GtTriggerMenuLite_cfi")

#####
# GCT internal jet collection
#####
process.simGctDigis.inputLabel = cms.InputTag('gctDigis')
process.simGctDigis.writeInternalData = cms.bool(True)
# process.simGctDigis.useImprovedTauAlgorithm = cms.bool(False)
# process.simGctDigis.preSamples = cms.uint32(0)
# process.simGctDigis.postSamples = cms.uint32(0)

# Convert Gct Internal jets to L1Extra objects
process.gctInternJetToL1Extra = cms.EDProducer('L1GctInternJetToL1Extra',
    gctInternJetSource=cms.InputTag("simGctDigis")
)
# Uses modified l1extraParticles (l1ExtraParticleProd.cc) module
# Not super happy with it, but will do (for now)
process.l1extraParticles.gctInternJetSource = cms.InputTag("simGctDigis")
process.l1extraParticles.genJetSource = cms.InputTag("ak5GenJets")

process.l1ExtraTreeProducerGctIntern = process.l1ExtraTreeProducer.clone()
process.l1ExtraTreeProducerGctIntern.cenJetLabel = cms.untracked.InputTag("gctInternJetToL1Extra:GctInternalJets")
process.l1ExtraTreeProducerGctIntern.maxL1Extra = cms.uint32(50)

#####
# Make ak4 GenJets
#####
process.load('RecoJets.Configuration.GenJetParticles_cff')
process.load('RecoJets.Configuration.RecoGenJets_cff')
process.antiktGenJets = cms.Sequence(process.genJetParticles*process.ak4GenJets)

#####
# Keep GenJets
#####
# Convert ak5 genjets to L1Extra objects
# can use the l1extraParticles module above, which produces L1JetParticleCollection from ak5GenJets
process.l1ExtraTreeProducerGenAk5 = process.l1ExtraTreeProducer.clone()
process.l1ExtraTreeProducerGenAk5.cenJetLabel = cms.untracked.InputTag("l1extraParticles:GenJets")
process.l1ExtraTreeProducerGenAk5.maxL1Extra = cms.uint32(50)

# Convert ak4 genjets to L1Extra objects
# Need to clone the l1extraParticles module and set ak4GenJets as input,
# then feed that into copy of l1ExtraTreeProducer
# process.l1extraParticlesAk4 = process.l1extraParticles.clone()
# process.l1extraParticlesAk4.genJetSource = cms.InputTag("ak4GenJets")
# process.l1ExtraTreeProducerGenAk4 = process.l1ExtraTreeProducer.clone()
# process.l1ExtraTreeProducerGenAk4.cenJetLabel = cms.untracked.InputTag("l1extraParticlesAk4:GenJets")
# process.l1ExtraTreeProducerGenAk4.maxL1Extra = cms.uint32(50)


process.p = cms.Path(
    process.RawToDigi
    # +process.antiktGenJets  # for GenJet
    +process.simGctDigis
    # +process.l1NtupleProducer
    +process.l1extraParticles
    +process.gctInternJetToL1Extra
    # +process.l1extraParticlesAk4
    +process.l1ExtraTreeProducer # gctDigis in cenJet coll
    +process.l1ExtraTreeProducerGctIntern # gctInternal jets in cenJet coll
    +process.l1ExtraTreeProducerGenAk5 # ak5GenJets in cenJet coll
    # +process.l1ExtraTreeProducerGenAk4
    # +process.l1GtTriggerMenuLite
    # +process.l1MenuTreeProducer
    # +process.l1RecoTreeProducer
    # +process.l1MuonRecoTreeProducer
)




# job options
# process.GlobalTag.globaltag = 'GR_R_52_V7::All'
process.GlobalTag.globaltag = cms.string('POSTLS162_V2::All')

SkipEvent = cms.untracked.vstring('ProductNotFound')

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

readFiles = cms.untracked.vstring()
# readFiles = cms.untracked.vstring('file:/afs/cern.ch/work/r/raggleto/L1JEC/CMSSW_7_2_0_pre7/src/L1TriggerDPG/L1Ntuples/test/QCD_GEN_SIM_RAW.root')
secFiles = cms.untracked.vstring()
process.source = cms.Source ("PoolSource",
                             fileNames = readFiles,
                             # fileNames = cms.untracked.vstring('root://xrootd.unl.edu//store/mc/Fall13dr/QCD_Pt-80to120_Tune4C_13TeV_pythia8/GEN-SIM-RAW/castor_tsg_PU40bx50_POSTLS162_V2-v1/00000/000AE06B-22A7-E311-BE0F-0025905A6138.root'),
                             secondaryFileNames = secFiles
                             )

# local testing file

## TTbar samples (server error)
# readFiles.extend( [
#     'root://xrootd.unl.edu//store/mc/Fall13dr/TT_Tune4C_13TeV-pythia8-tauola/GEN-SIM-RAW/tsg_PU40bx50_POSTLS162_V2-v1/00000/040974D0-3A75-E311-B258-002590596484.root',
#     'root://xrootd.unl.edu//store/mc/Fall13dr/TT_Tune4C_13TeV-pythia8-tauola/GEN-SIM-RAW/tsg_PU40bx50_POSTLS162_V2-v1/00000/04A84408-3975-E311-9724-002618943856.root',
#     'root://xrootd.unl.edu//store/mc/Fall13dr/TT_Tune4C_13TeV-pythia8-tauola/GEN-SIM-RAW/tsg_PU40bx50_POSTLS162_V2-v1/00000/0636E18D-5975-E311-85AB-00261894386A.root',
#     'root://xrootd.unl.edu//store/mc/Fall13dr/TT_Tune4C_13TeV-pythia8-tauola/GEN-SIM-RAW/tsg_PU40bx50_POSTLS162_V2-v1/00000/02ECF824-4E75-E311-BB0F-0026189438CE.root'
#     ])

readFiles.extend( [
    'root://xrootd.unl.edu//store/mc/Fall13dr/TT_Tune4C_13TeV-pythia8-tauola/GEN-SIM-RAW/tsg_PU20bx25_POSTLS162_V2-v1/00000/00269845-7290-E311-A032-0025905A6056.root',
    'root://xrootd.unl.edu//store/mc/Fall13dr/TT_Tune4C_13TeV-pythia8-tauola/GEN-SIM-RAW/tsg_PU20bx25_POSTLS162_V2-v1/00000/001E7210-126D-E311-8D68-003048679182.root',
    'root://xrootd.unl.edu//store/mc/Fall13dr/TT_Tune4C_13TeV-pythia8-tauola/GEN-SIM-RAW/tsg_PU20bx25_POSTLS162_V2-v1/00000/00280FAA-206E-E311-A12B-0025905AA9CC.root',
    'root://xrootd.unl.edu//store/mc/Fall13dr/TT_Tune4C_13TeV-pythia8-tauola/GEN-SIM-RAW/tsg_PU20bx25_POSTLS162_V2-v1/00000/002AD255-616C-E311-B1D6-0025905A48F2.root',
    'root://xrootd.unl.edu//store/mc/Fall13dr/TT_Tune4C_13TeV-pythia8-tauola/GEN-SIM-RAW/tsg_PU20bx25_POSTLS162_V2-v1/00000/00392F64-8190-E311-ACD1-002618943856.root',
    'root://xrootd.unl.edu//store/mc/Fall13dr/TT_Tune4C_13TeV-pythia8-tauola/GEN-SIM-RAW/tsg_PU20bx25_POSTLS162_V2-v1/00000/00574A70-E186-E311-8BE9-003048678A7E.root',
    'root://xrootd.unl.edu//store/mc/Fall13dr/TT_Tune4C_13TeV-pythia8-tauola/GEN-SIM-RAW/tsg_PU20bx25_POSTLS162_V2-v1/00000/00D33AA9-326D-E311-AB31-003048678E92.root',
    'root://xrootd.unl.edu//store/mc/Fall13dr/TT_Tune4C_13TeV-pythia8-tauola/GEN-SIM-RAW/tsg_PU20bx25_POSTLS162_V2-v1/00000/00E2DAC5-8A6C-E311-A2F6-0025905A610C.root',
    'root://xrootd.unl.edu//store/mc/Fall13dr/TT_Tune4C_13TeV-pythia8-tauola/GEN-SIM-RAW/tsg_PU20bx25_POSTLS162_V2-v1/00000/00FE3096-476D-E311-8608-0026189437FD.root',
    'root://xrootd.unl.edu//store/mc/Fall13dr/TT_Tune4C_13TeV-pythia8-tauola/GEN-SIM-RAW/tsg_PU20bx25_POSTLS162_V2-v1/00000/0239DBE7-0D91-E311-A208-003048FFCB96.root'
    ])

# QCD flat samples
# readFiles.extend( [
#     'root://xrootd.unl.edu//store/mc/Spring14dr/QCD_Pt-15to3000_Tune4C_Flat_13TeV_pythia8/GEN-SIM-RAW/Flat20to50_POSTLS170_V5-v1/00000/000209D1-A6DD-E311-9EE7-002590D0B000.root',
#     'root://xrootd.unl.edu//store/mc/Spring14dr/QCD_Pt-15to3000_Tune4C_Flat_13TeV_pythia8/GEN-SIM-RAW/Flat20to50_POSTLS170_V5-v1/00000/0008C695-E7DD-E311-85CD-00261834B5D2.root',
#     'root://xrootd.unl.edu//store/mc/Spring14dr/QCD_Pt-15to3000_Tune4C_Flat_13TeV_pythia8/GEN-SIM-RAW/Flat20to50_POSTLS170_V5-v1/00000/0025BAA3-EBDD-E311-8D7F-E0CB4E55368D.root',
#     'root://xrootd.unl.edu//store/mc/Spring14dr/QCD_Pt-15to3000_Tune4C_Flat_13TeV_pythia8/GEN-SIM-RAW/Flat20to50_POSTLS170_V5-v1/00000/0050C2B4-75DD-E311-957B-00259073E3FA.root',
#     'root://xrootd.unl.edu//store/mc/Spring14dr/QCD_Pt-15to3000_Tune4C_Flat_13TeV_pythia8/GEN-SIM-RAW/Flat20to50_POSTLS170_V5-v1/00000/008B2415-EBDD-E311-B807-20CF3027A564.root',
#     'root://xrootd.unl.edu//store/mc/Spring14dr/QCD_Pt-15to3000_Tune4C_Flat_13TeV_pythia8/GEN-SIM-RAW/Flat20to50_POSTLS170_V5-v1/00000/00CFF4B9-2CDE-E311-8A94-90E6BA19A227.root',
#     'root://xrootd.unl.edu//store/mc/Spring14dr/QCD_Pt-15to3000_Tune4C_Flat_13TeV_pythia8/GEN-SIM-RAW/Flat20to50_POSTLS170_V5-v1/00000/02029D87-36DE-E311-B786-20CF3027A56B.root',
#     'root://xrootd.unl.edu//store/mc/Spring14dr/QCD_Pt-15to3000_Tune4C_Flat_13TeV_pythia8/GEN-SIM-RAW/Flat20to50_POSTLS170_V5-v1/00000/0238CDC9-7FDD-E311-97F9-002590D0B0AC.root',
#     'root://xrootd.unl.edu//store/mc/Spring14dr/QCD_Pt-15to3000_Tune4C_Flat_13TeV_pythia8/GEN-SIM-RAW/Flat20to50_POSTLS170_V5-v1/00000/023975FD-EDDD-E311-BB09-E0CB4E19F9AC.root',
#     'root://xrootd.unl.edu//store/mc/Spring14dr/QCD_Pt-15to3000_Tune4C_Flat_13TeV_pythia8/GEN-SIM-RAW/Flat20to50_POSTLS170_V5-v1/00000/023B6D4D-D1DD-E311-8DA2-90E6BA19A20B.root'
#     ])

## QCD samples
# readFiles.extend( [
#     'root://xrootd.unl.edu//store/mc/Fall13dr/QCD_Pt-80to120_Tune4C_13TeV_pythia8/GEN-SIM-RAW/castor_tsg_PU40bx50_POSTLS162_V2-v1/00000/000AE06B-22A7-E311-BE0F-0025905A6138.root',
#     'root://xrootd.unl.edu//store/mc/Fall13dr/QCD_Pt-80to120_Tune4C_13TeV_pythia8/GEN-SIM-RAW/castor_tsg_PU40bx50_POSTLS162_V2-v1/00000/0036E353-51A7-E311-8429-0025905A610C.root',
#     'root://xrootd.unl.edu//store/mc/Fall13dr/QCD_Pt-80to120_Tune4C_13TeV_pythia8/GEN-SIM-RAW/castor_tsg_PU40bx50_POSTLS162_V2-v1/00000/005BDE0C-46A7-E311-BD52-0025905A60CA.root',
#     'root://xrootd.unl.edu//store/mc/Fall13dr/QCD_Pt-80to120_Tune4C_13TeV_pythia8/GEN-SIM-RAW/castor_tsg_PU40bx50_POSTLS162_V2-v1/00000/009B4961-5FA7-E311-BFC4-003048FFD736.root',
#     'root://xrootd.unl.edu//store/mc/Fall13dr/QCD_Pt-80to120_Tune4C_13TeV_pythia8/GEN-SIM-RAW/castor_tsg_PU40bx50_POSTLS162_V2-v1/00000/02575879-39A7-E311-9E16-0025905AA9CC.root',
#     'root://xrootd.unl.edu//store/mc/Fall13dr/QCD_Pt-80to120_Tune4C_13TeV_pythia8/GEN-SIM-RAW/castor_tsg_PU40bx50_POSTLS162_V2-v1/00000/02578496-59A7-E311-982C-003048678AFA.root',
#     'root://xrootd.unl.edu//store/mc/Fall13dr/QCD_Pt-80to120_Tune4C_13TeV_pythia8/GEN-SIM-RAW/castor_tsg_PU40bx50_POSTLS162_V2-v1/00000/0263A814-2EA7-E311-A1E4-002618943963.root',
#     'root://xrootd.unl.edu//store/mc/Fall13dr/QCD_Pt-80to120_Tune4C_13TeV_pythia8/GEN-SIM-RAW/castor_tsg_PU40bx50_POSTLS162_V2-v1/00000/02880A8E-19A7-E311-8235-0025905A48BA.root',
#     'root://xrootd.unl.edu//store/mc/Fall13dr/QCD_Pt-80to120_Tune4C_13TeV_pythia8/GEN-SIM-RAW/castor_tsg_PU40bx50_POSTLS162_V2-v1/00000/029E91A4-1AA7-E311-99D0-002590596486.root',
#     'root://xrootd.unl.edu//store/mc/Fall13dr/QCD_Pt-80to120_Tune4C_13TeV_pythia8/GEN-SIM-RAW/castor_tsg_PU40bx50_POSTLS162_V2-v1/00000/02B56379-57A7-E311-A0EF-003048FFD744.root',
#     'root://xrootd.unl.edu//store/mc/Fall13dr/QCD_Pt-80to120_Tune4C_13TeV_pythia8/GEN-SIM-RAW/castor_tsg_PU40bx50_POSTLS162_V2-v1/00000/02EAD2C2-3CA7-E311-8EB9-0025905A6110.root',
#     'root://xrootd.unl.edu//store/mc/Fall13dr/QCD_Pt-80to120_Tune4C_13TeV_pythia8/GEN-SIM-RAW/castor_tsg_PU40bx50_POSTLS162_V2-v1/00000/04129CAE-49A7-E311-96F9-00248C0BE018.root',
#     'root://xrootd.unl.edu//store/mc/Fall13dr/QCD_Pt-80to120_Tune4C_13TeV_pythia8/GEN-SIM-RAW/castor_tsg_PU40bx50_POSTLS162_V2-v1/00000/041461CE-44A7-E311-8A35-0026189437F0.root',
#     'root://xrootd.unl.edu//store/mc/Fall13dr/QCD_Pt-80to120_Tune4C_13TeV_pythia8/GEN-SIM-RAW/castor_tsg_PU40bx50_POSTLS162_V2-v1/00000/041C1CBA-3BA7-E311-8999-00259059649C.root',
#     'root://xrootd.unl.edu//store/mc/Fall13dr/QCD_Pt-80to120_Tune4C_13TeV_pythia8/GEN-SIM-RAW/castor_tsg_PU40bx50_POSTLS162_V2-v1/00000/04351463-4AA7-E311-A764-002618943845.root',
#     'root://xrootd.unl.edu//store/mc/Fall13dr/QCD_Pt-80to120_Tune4C_13TeV_pythia8/GEN-SIM-RAW/castor_tsg_PU40bx50_POSTLS162_V2-v1/00000/043F3A65-4AA7-E311-A0FE-0025905A60F2.root',
#     'root://xrootd.unl.edu//store/mc/Fall13dr/QCD_Pt-80to120_Tune4C_13TeV_pythia8/GEN-SIM-RAW/castor_tsg_PU40bx50_POSTLS162_V2-v1/00000/046A411C-25A7-E311-9B65-00304867C1BA.root',
#     'root://xrootd.unl.edu//store/mc/Fall13dr/QCD_Pt-80to120_Tune4C_13TeV_pythia8/GEN-SIM-RAW/castor_tsg_PU40bx50_POSTLS162_V2-v1/00000/049CCC9A-4DA7-E311-BFC4-0025905A610A.root',
#     'root://xrootd.unl.edu//store/mc/Fall13dr/QCD_Pt-80to120_Tune4C_13TeV_pythia8/GEN-SIM-RAW/castor_tsg_PU40bx50_POSTLS162_V2-v1/00000/04A666AD-41A7-E311-AF99-0025905A60DE.root'
#     ])

# process.output = cms.OutputModule(
#     "PoolOutputModule",
#     outputCommands = cms.untracked.vstring('keep *'),
#     # outputCommands = cms.untracked.vstring(
#     #     'drop *',

#     #     # Keep GCT jets
#     #     'keep *_gctDigis_*_*',
#     #     'keep *_simGctDigis_*_*',

#     #     # Keep GenJets
#     #     'keep *_ak5GenJets_*_*'
#     #     ),
#     fileName = cms.untracked.string('SimGCTEmulator.root')
#     )

# process.output_step = cms.EndPath(process.output)

# process.schedule = cms.Schedule(
#     process.p, process.output_step
#     )