import FWCore.ParameterSet.Config as cms

process = cms.Process('L1TEMULATION')

process.load('Configuration.StandardSequences.Services_cff')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration/StandardSequences/FrontierConditions_GlobalTag_cff')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.Geometry.GeometryIdeal_cff')

# Select the Message Logger output you would like to see:
process.load('FWCore.MessageService.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 200
process.MessageLogger.suppressWarning = cms.untracked.vstring(
                                            "l1ExtraTreeProducerGenAk4",
                                            "l1ExtraTreeProducerGenAk5",
                                            "l1ExtraTreeProducerIntern"
                                            )

##############################
# Input/output & standard stuff
##############################
process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1)
    )

# Input source
readFiles = cms.untracked.vstring()
process.source = cms.Source("PoolSource",
    # secondaryFileNames = cms.untracked.vstring(),
    # fileNames = cms.untracked.vstring("root://xrootd.unl.edu//store/mc/Fall13dr/Neutrino_Pt-2to20_gun/GEN-SIM-RAW/tsg_PU40bx25_POSTLS162_V2-v1/00005/02B79593-F47F-E311-8FF6-003048FFD796.root")
    # fileNames = cms.untracked.vstring("root://xrootd.unl.edu//store/mc/Spring14dr/QCD_Pt-15to3000_Tune4C_Flat_13TeV_pythia8/GEN-SIM-RAW/Flat20to50_POSTLS170_V5-v1/00000/008B2415-EBDD-E311-B807-20CF3027A564.root")
    # fileNames = cms.untracked.vstring('file:/afs/cern.ch/work/r/raggleto/L1JEC/CMSSW_7_2_0_pre7/src/L1TriggerDPG/L1Ntuples/test/QCD_GEN_SIM_RAW.root')
    # fileNames = cms.untracked.vstring('file:/afs/cern.ch/work/r/raggleto/L1JEC/CMSSW_7_2_0_pre7/src/L1TriggerDPG/L1Ntuples/test/QCD_GEN_SIM_RAW.root')
    # fileNames = cms.untracked.vstring('root://xrootd.unl.edu//store/mc/Phys14DR/QCD_Pt-80to120_Tune4C_13TeV_pythia8/GEN-SIM-RAW/AVE20BX25_tsg_castor_PHYS14_25_V3-v1/00000/00679EAE-098E-E411-9AFC-0025905A6104.root')
    fileNames = cms.untracked.vstring('root://xrootd.unl.edu//store/mc/Phys14DR/QCD_Pt-1400to1800_Tune4C_13TeV_pythia8/GEN-SIM-RAW/AVE20BX25_tsg_castor_PHYS14_25_V3-v1/00000/0047F5E2-848E-E411-B993-0025905A6076.root')
    # fileNames = readFiles
    )

# readFiles.extend( [
#   "root://xrootd.unl.edu//store/relval/CMSSW_7_3_0/RelValTTbar_13/GEN-SIM-DIGI-RAW-HLTDEBUG/PU50ns_MCRUN2_73_V9_71XGENSIM_FIXGT-v1/00000/52957EA0-2AA2-E411-908B-002618FDA265.root"
# ])

process.output = cms.OutputModule(
    "PoolOutputModule",
    splitLevel = cms.untracked.int32(0),
    eventAutoFlushCompressedSize = cms.untracked.int32(5242880),
    outputCommands = cms.untracked.vstring('keep *',
                                           'keep *_ak5GenJets_*_*',
                                           'keep *_ak4GenJets_*_*',
                                           # 'keep *_*_*_L1TEMULATION',
                                           'keep l1tJetBXVector_*_*_*',
                                           'keep L1GctJetCands_*_*_*',
                                           'keep l1extraL1JetParticles_*_*_*'
                                           ),
    fileName = cms.untracked.string('SimL1Emulator_Stage1_PP.root'),
    dataset = cms.untracked.PSet(
        filterName = cms.untracked.string(''),
        dataTier = cms.untracked.string('')
    )
                                           )

process.TFileService = cms.Service("TFileService",
    fileName = cms.string('L1Tree.root')
    # fileName = cms.string('L1Tree_RelVal_Stage1_newRCT.root')
    # fileName = cms.string('L1Tree_RelVal_Stage1.root')
)


# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag.connect = cms.string('frontier://FrontierProd/CMS_COND_31X_GLOBALTAG')
# process.GlobalTag.globaltag = cms.string('POSTLS162_V2::All')
process.GlobalTag.globaltag = cms.string('PHYS14_25_V3::All') # for Phys14 AVE20BX25
# process.GlobalTag.globaltag = cms.string('MCRUN2_73_V9::All')

##############################
# Load up Stage 1 emulator
##############################
process.load('L1Trigger.L1TCalorimeter.L1TCaloStage1_PPFromRaw_cff')

# GT
from L1Trigger.Configuration.SimL1Emulator_cff import simGtDigis
process.simGtDigis = simGtDigis.clone()
process.simGtDigis.GmtInputTag = 'simGmtDigis'
process.simGtDigis.GctInputTag = 'caloStage1LegacyFormatDigis'
process.simGtDigis.TechnicalTriggersInputTags = cms.VInputTag( )

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

##############################
# Put normal Stage 1 collections into L1ExtraTree
##############################
process.load("L1TriggerDPG.L1Ntuples.l1ExtraTreeProducer_cfi")
process.l1ExtraTreeProducer.nonIsoEmLabel = cms.untracked.InputTag("l1ExtraLayer2:NonIsolated")
process.l1ExtraTreeProducer.isoEmLabel = cms.untracked.InputTag("l1ExtraLayer2:Isolated")
process.l1ExtraTreeProducer.tauJetLabel = cms.untracked.InputTag("l1ExtraLayer2:Tau")
process.l1ExtraTreeProducer.isoTauJetLabel = cms.untracked.InputTag("l1ExtraLayer2:IsoTau")
process.l1ExtraTreeProducer.cenJetLabel = cms.untracked.InputTag("l1ExtraLayer2:Central")
process.l1ExtraTreeProducer.fwdJetLabel = cms.untracked.InputTag("l1ExtraLayer2:Forward")
process.l1ExtraTreeProducer.muonLabel = cms.untracked.InputTag("l1ExtraLayer2")
process.l1ExtraTreeProducer.metLabel = cms.untracked.InputTag("l1ExtraLayer2:MET")
process.l1ExtraTreeProducer.mhtLabel = cms.untracked.InputTag("l1ExtraLayer2:MHT")
process.l1ExtraTreeProducer.hfRingsLabel = cms.untracked.InputTag("l1ExtraLayer2")


##############################
# Do Stage 1 internal jet collection (preGtJets)
##############################
# Conversion from JetBxCollection to L1JetParticles
process.preGtJetToL1Jet = cms.EDProducer('PreGtJetToL1Jet',
    preGtJetSource = cms.InputTag("simCaloStage1FinalDigis:preGtJets")
)

# L1Extra TTree - put preGtJets in "cenJet" branch
process.l1ExtraTreeProducerIntern = process.l1ExtraTreeProducer.clone()
process.l1ExtraTreeProducerIntern.nonIsoEmLabel = cms.untracked.InputTag("")
process.l1ExtraTreeProducerIntern.isoEmLabel = cms.untracked.InputTag("")
process.l1ExtraTreeProducerIntern.tauJetLabel = cms.untracked.InputTag("")
process.l1ExtraTreeProducerIntern.isoTauJetLabel = cms.untracked.InputTag("")
process.l1ExtraTreeProducerIntern.fwdJetLabel = cms.untracked.InputTag("")
process.l1ExtraTreeProducerIntern.muonLabel = cms.untracked.InputTag("")
process.l1ExtraTreeProducerIntern.metLabel = cms.untracked.InputTag("")
process.l1ExtraTreeProducerIntern.mhtLabel = cms.untracked.InputTag("")
process.l1ExtraTreeProducerIntern.hfRingsLabel = cms.untracked.InputTag("")
process.l1ExtraTreeProducerIntern.cenJetLabel = cms.untracked.InputTag("preGtJetToL1Jet:PreGtJets")
process.l1ExtraTreeProducerIntern.maxL1Extra = cms.uint32(50)

# Turn off any existing stage 1 calibrations
process.caloStage1Params.jetCalibrationType = cms.string("None")

##############################
# Do ak5 GenJets
##############################
# Convert ak5 genjets to L1JetParticle objects, store in another L1ExtraTree as cenJets
process.genJetToL1JetAk5 = cms.EDProducer("GenJetToL1Jet",
    genJetSource = cms.InputTag("ak5GenJets")
)
process.l1ExtraTreeProducerGenAk5 = process.l1ExtraTreeProducerIntern.clone()
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
process.l1ExtraTreeProducerGenAk4 = process.l1ExtraTreeProducerIntern.clone()
process.l1ExtraTreeProducerGenAk4.cenJetLabel = cms.untracked.InputTag("genJetToL1JetAk4:GenJets")
process.l1ExtraTreeProducerGenAk4.maxL1Extra = cms.uint32(50)


##############################
# Store PU info (nvtx, etc)
##############################
process.puInfo = cms.EDAnalyzer("PileupInfo",
    pileupInfoSource = cms.InputTag("addPileupInfo")
)


process.p1 = cms.Path(
    process.L1TCaloStage1_PPFromRaw
    # +process.simGtDigis
    +process.l1ExtraLayer2
    +process.preGtJetToL1Jet # convert preGtJets into L1Jet objs
    # +process.antiktGenJets # make ak4GenJets
    +process.genJetToL1JetAk5 # convert ak5GenJets to L1Jet objs
    +process.genJetToL1JetAk4 # convert ak4GenJets to L1Jet objs
    +process.l1ExtraTreeProducer # normal Stage 1 stuff in L1ExtraTree
    +process.l1ExtraTreeProducerIntern # ditto but with preGtJets in cenJet branch
    +process.l1ExtraTreeProducerGenAk5 # ak5GenJets in cenJet branch
    +process.l1ExtraTreeProducerGenAk4 # ak4GenJets in cenJet branch
    +process.puInfo # store nVtx info
    )

# process.output_step = cms.EndPath(process.output)

process.schedule = cms.Schedule(
    process.p1
    # process.output_step
    )

# Spit out filter efficiency at the end.
process.options = cms.untracked.PSet(wantSummary = cms.untracked.bool(True))
