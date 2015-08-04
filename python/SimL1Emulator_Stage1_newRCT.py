"""
Config file to run the Stage 1 emulator to make Ntuples.

Stores internal jets, as well as ak5 and ak4 GenJets

YOU MUST RUN WITH CMSSW 742 OR NEWER TO PICK UP THE NEW RCT CALIBS.

"""

import FWCore.ParameterSet.Config as cms

# To use new RCT calibrations (default in MC is 2012):
new_RCT_calibs = True

# To dump RCT parameters for testing purposes:
dump_RCT = False

# To save the EDM content as well:
# (WARNING: DON'T do this for big production - will be HUGE)
save_EDM = False

# Global tag (note, you must ensure it matches input file)
# You don't need the "::All"!
gt = 'MCRUN2_74_V9' # for Spring15 AVE20BX25

# Things to append to L1Ntuple/EDM filename
# (if using new RCT calibs, this gets auto added)
file_append = "_Stage1_calibrated"

# Add in a filename appendix here for your GlobalTag.
file_append += "_" + gt

###################################################################
process = cms.Process('L1NTUPLE')

process.load('Configuration.StandardSequences.Services_cff')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.StandardSequences.GeometryDB_cff')
process.load("Configuration.StandardSequences.RawToDigi_Data_cff")
process.load('Configuration.StandardSequences.L1Reco_cff')
process.load('Configuration.StandardSequences.Reconstruction_cff')
process.load('Configuration/StandardSequences/EndOfProcess_cff')
process.load('Configuration/StandardSequences/MagneticField_AutoFromDBCurrent_cff')
process.load("JetMETCorrections.Configuration.DefaultJEC_cff")
process.load('Configuration/StandardSequences/SimL1Emulator_cff')
process.load('Configuration/StandardSequences/FrontierConditions_GlobalTag_condDBv2_cff')
from Configuration.AlCa.GlobalTag_condDBv2 import GlobalTag

# Select the Message Logger output you would like to see:
process.load('FWCore.MessageService.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 200
process.MessageLogger.suppressWarning = cms.untracked.vstring(
    "l1ExtraTreeProducerGenAk4",
    "l1ExtraTreeProducerGenAk5",
    "l1ExtraTreeProducerIntern",
    "l1NtupleProducer",
    "csctfDigis"
)

process.gctDigis.numberOfGctSamplesToUnpack = cms.uint32(1)

##############################
# Load up Stage 1 emulator
##############################

# This is messy, because the standard sequence
# process.load('L1Trigger.L1TCalorimeter.L1TCaloStage1_PPFromRaw_cff')
# overrides whatever new RCT calibrations you want to use
# (from L1Trigger.L1TCalorimeter.caloStage1RCTLuts_cff import * is the offending line)
# So we have to:
# - remake HCAL TPs due to it being broken in MC older than Spring15
# - rerun RCT with the regions
# - pass the regions to Stage 1 and run that

process.load('L1Trigger.L1TCalorimeter.caloStage1Params_cfi')

# Remake the HCAL TPs since hcalDigis outputs nothing in MC made with CMSSW
# earlier than 735 (not sure exactly which version, certainly works in Spring15)
# But make sure you use the unsupressed digis, not the hcalDigis
# process.load('SimCalorimetry.HcalTrigPrimProducers.hcaltpdigi_cff')
# process.simHcalTriggerPrimitiveDigis.inputLabel = cms.VInputTag(
#     cms.InputTag('simHcalUnsuppressedDigis'),
#     cms.InputTag('simHcalUnsuppressedDigis')
# )

# Rerun the RCT emulator using the TPs
# from Configuration.StandardSequences.SimL1Emulator_cff import simRctDigis
# process.simRctDigis = simRctDigis.clone()
# If the hcalDigis is empty (MC made pre 740), then use:
# process.simRctDigis.hcalDigis = cms.VInputTag(cms.InputTag('simHcalTriggerPrimitiveDigis'))
# If it's fixed, use:
process.simRctDigis.hcalDigis = cms.VInputTag(cms.InputTag('hcalDigis'))
process.simRctDigis.ecalDigis = cms.VInputTag(cms.InputTag('ecalDigis', 'EcalTriggerPrimitives' ))

# Load up the Stage 1 parts
process.load('L1Trigger.L1TCalorimeter.L1TCaloStage1_cff')

import L1Trigger.Configuration.L1Extra_cff
process.l1ExtraLayer2 = L1Trigger.Configuration.L1Extra_cff.l1extraParticles.clone()
process.l1ExtraLayer2.isolatedEmSource    = cms.InputTag("simCaloStage1LegacyFormatDigis","isoEm")
process.l1ExtraLayer2.nonIsolatedEmSource = cms.InputTag("simCaloStage1LegacyFormatDigis","nonIsoEm")
process.l1ExtraLayer2.forwardJetSource = cms.InputTag("simCaloStage1LegacyFormatDigis","forJets")
process.l1ExtraLayer2.centralJetSource = cms.InputTag("simCaloStage1LegacyFormatDigis","cenJets")
process.l1ExtraLayer2.tauJetSource     = cms.InputTag("simCaloStage1LegacyFormatDigis","tauJets")
process.l1ExtraLayer2.isoTauJetSource  = cms.InputTag("simCaloStage1LegacyFormatDigis","isoTauJets")
process.l1ExtraLayer2.etTotalSource = cms.InputTag("simCaloStage1LegacyFormatDigis")
process.l1ExtraLayer2.etHadSource   = cms.InputTag("simCaloStage1LegacyFormatDigis")
process.l1ExtraLayer2.etMissSource  = cms.InputTag("simCaloStage1LegacyFormatDigis")
process.l1ExtraLayer2.htMissSource  = cms.InputTag("simCaloStage1LegacyFormatDigis")
process.l1ExtraLayer2.hfRingEtSumsSource    = cms.InputTag("simCaloStage1LegacyFormatDigis")
process.l1ExtraLayer2.hfRingBitCountsSource = cms.InputTag("simCaloStage1LegacyFormatDigis")
process.l1ExtraLayer2.muonSource = cms.InputTag("simGmtDigis")

# Turn off any existing stage 1 calibrations
# process.caloStage1Params.jetCalibrationType = cms.string("None")
process.caloStage1Params.jetCalibrationType = cms.string("Stage1JEC")
process.caloStage1Params.jetCalibrationLUTFile = cms.FileInPath("L1Trigger/L1JetEnergyCorrections/data/jetCalibrationLUT_stage1_symmetric_Spring15_newRCTv2.txt")

##############################
# Put normal Stage 1 collections into L1ExtraTree
##############################
process.load("L1TriggerDPG.L1Ntuples.l1ExtraTreeProducer_cfi")
# process.load("L1Trigger.L1TNtuples.l1ExtraTreeProducer_cfi")
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

##############################
# Alternate way of getting Stage 1 preGtJet collection using new NTuples
# But still need a L1UpgradeTree to access it afterwards
##############################
# process.load("L1Trigger.L1TNtuples.l1UpgradeTreeProducer_cfi")
# process.l1UpgradeTreeProducer.egLabel = cms.untracked.InputTag("")
# process.l1UpgradeTreeProducer.tauLabel = cms.untracked.InputTag("")
# process.l1UpgradeTreeProducer.muonLabel = cms.untracked.InputTag("")
# process.l1UpgradeTreeProducer.jetLabel = cms.untracked.InputTag("simCaloStage1FinalDigis:preGtJets")

##############################
# Do ak5 GenJets
##############################
# Need to make ak5, not included in GEN-SIM-RAW for Spring15 onwards
process.load('RecoJets.Configuration.GenJetParticles_cff')
process.load('RecoJets.Configuration.RecoGenJets_cff')
process.antiktGenJets = cms.Sequence(process.genJetParticles*process.ak5GenJets)

# Convert ak5 genjets to L1JetParticle objects, store in another L1ExtraTree as cenJets
process.genJetToL1JetAk5 = cms.EDProducer("GenJetToL1Jet",
    genJetSource = cms.InputTag("ak5GenJets", "", "L1NTUPLE")
)
process.l1ExtraTreeProducerGenAk5 = process.l1ExtraTreeProducerIntern.clone()
process.l1ExtraTreeProducerGenAk5.cenJetLabel = cms.untracked.InputTag("genJetToL1JetAk5:GenJets")
process.l1ExtraTreeProducerGenAk5.maxL1Extra = cms.uint32(50)

##############################
# Do ak4 GenJets
##############################
# Need to make ak4, not included in GEN-SIM-RAW before Phys14
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

##############################
# New RCT calibs - GlobalTag is set here
##############################
if new_RCT_calibs:
    print "*** Using new RCT calibs"
    # Format: map{(record,label):(tag,connection),...}
    recordOverrides = { ('L1RCTParametersRcd', None) : ('L1RCTParametersRcd_L1TDevelCollisions_ExtendedScaleFactorsV2', None) }
    process.GlobalTag = GlobalTag(process.GlobalTag, gt, recordOverrides)
    file_append += '_newRCTv2'
else:
    print "*** Using whatever RCT calibs the sample was made with"
    process.GlobalTag.globaltag = cms.string(gt)

##############################
# L1Ntuple producer
##############################
process.load("L1TriggerDPG.L1Ntuples.l1NtupleProducer_cfi")
process.l1NtupleProducer.gctCentralJetsSource = cms.InputTag("simCaloStage1LegacyFormatDigis","cenJets")
process.l1NtupleProducer.gctNonIsoEmSource    = cms.InputTag("simCaloStage1LegacyFormatDigis","nonIsoEm")
process.l1NtupleProducer.gctForwardJetsSource = cms.InputTag("simCaloStage1LegacyFormatDigis","forJets")
process.l1NtupleProducer.gctIsoEmSource       = cms.InputTag("simCaloStage1LegacyFormatDigis","isoEm")
process.l1NtupleProducer.gctEnergySumsSource  = cms.InputTag("simCaloStage1LegacyFormatDigis","")
process.l1NtupleProducer.gctTauJetsSource     = cms.InputTag("simCaloStage1LegacyFormatDigis","tauJets")
process.l1NtupleProducer.gctIsoTauJetsSource  = cms.InputTag("simCaloStage1LegacyFormatDigis","isoTauJets")

##############################
# Overall path
##############################

process.p = cms.Path(
    # process.L1TCaloStage1_PPFromRaw
    # process.ecalDigis # ecal unpacker
    # *process.hcalDigis # hcal unpacker
    # *process.gctDigis # gct unpacker
    # *process.simHcalTriggerPrimitiveDigis # remake hcal TPs
    # *process.simRctDigis # remake regions
    process.RawToDigi
    *process.simRctDigis
    *process.L1TCaloStage1 # run Stage1
    *process.l1ExtraLayer2
    *process.preGtJetToL1Jet # convert preGtJets into L1Jet objs
    *process.antiktGenJets # make ak5GenJets
    *process.genJetToL1JetAk5 # convert ak5GenJets to L1Jet objs
    *process.genJetToL1JetAk4 # convert ak4GenJets to L1Jet objs
    *process.l1ExtraTreeProducer # normal Stage 1 stuff in L1ExtraTree
    *process.l1ExtraTreeProducerIntern # ditto but with preGtJets in cenJet branch
    *process.l1ExtraTreeProducerGenAk5 # ak5GenJets in cenJet branch
    *process.l1ExtraTreeProducerGenAk4 # ak4GenJets in cenJet branch
    *process.puInfo # store nVtx info
    # *process.l1UpgradeTreeProducer
    *process.l1NtupleProducer
    )

if dump_RCT:
    process.l1RCTParametersTest = cms.EDAnalyzer("L1RCTParametersTester")  # don't forget to include me in a cms.Path()
    process.p *= process.l1RCTParametersTest

##############################
# Input/output & standard stuff
##############################
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(20))

# Input source

# Some default testing files
if gt in ['PHYS14_25_V3', 'PHYS14_25_V2', 'MCRUN2_74_V8']:
    fileNames = cms.untracked.vstring('root://xrootd.unl.edu//store/mc/Phys14DR/QCD_Pt-120to170_Tune4C_13TeV_pythia8/GEN-SIM-RAW/AVE20BX25_tsg_castor_PHYS14_25_V3-v1/00000/004DD38A-2B8E-E411-8E4F-003048FFD76E.root')
elif gt in ['MCRUN2_74_V9', 'MCRUN2_74_V7']:
    # fileNames = cms.untracked.vstring('root://xrootd.unl.edu//store/mc/RunIISpring15Digi74/QCD_Pt_80to120_TuneCUETP8M1_13TeV_pythia8/GEN-SIM-RAW/AVE_20_BX_25ns_tsg_MCRUN2_74_V7-v2/80000/0011C312-7701-E511-B156-0025905C94D2.root')
    fileNames = cms.untracked.vstring(
        'root://xrootd.unl.edu//store/mc/RunIISpring15Digi74/QCD_Pt_470to600_TuneCUETP8M1_13TeV_pythia8/GEN-SIM-RAW/AVE_40_BX_25ns_tsg_MCRUN2_74_V7-v1/00000/0C72BDF4-03F4-E411-868F-003048CEFFE4.root'
        # 'root://xrootd.unl.edu//store/mc/RunIISpring15Digi74/QCD_Pt_300to470_TuneCUETP8M1_13TeV_pythia8/GEN-SIM-RAW/AVE_20_BX_25ns_tsg_MCRUN2_74_V7-v1/70000/00EFBCBB-61F0-E411-B56B-00266CF9B254.root',
        # "root://xrootd.unl.edu//store/mc/RunIISpring15Digi74/QCD_Pt_300to470_TuneCUETP8M1_13TeV_pythia8/GEN-SIM-RAW/AVE_20_BX_25ns_tsg_MCRUN2_74_V7-v1/70000/02559CAE-F5EF-E411-AEDC-002590D0AFB4.root",
        # "root://xrootd.unl.edu//store/mc/RunIISpring15Digi74/QCD_Pt_300to470_TuneCUETP8M1_13TeV_pythia8/GEN-SIM-RAW/AVE_20_BX_25ns_tsg_MCRUN2_74_V7-v1/70000/02C5441C-60F0-E411-A6D9-7845C4FC3611.root",
        # "root://xrootd.unl.edu//store/mc/RunIISpring15Digi74/QCD_Pt_300to470_TuneCUETP8M1_13TeV_pythia8/GEN-SIM-RAW/AVE_20_BX_25ns_tsg_MCRUN2_74_V7-v1/70000/0402D5EC-F7EF-E411-86ED-E0CB4E4408F3.root",
        )
else:
    raise RuntimeError("No file to use with GT: %s" % gt)

process.source = cms.Source("PoolSource",
                            fileNames = fileNames
                            )

edm_filename = 'SimStage1Emulator{0}.root'.format(file_append)
process.output = cms.OutputModule(
    "PoolOutputModule",
    splitLevel = cms.untracked.int32(0),
    eventAutoFlushCompressedSize = cms.untracked.int32(5242880),
    # outputCommands = cms.untracked.vstring('keep *'),
    outputCommands = cms.untracked.vstring(
        'drop *',

        # Keep TPs
        'keep *_simHcalTriggerPrimitiveDigis_*_*',
        'keep *_hcalDigis_*_*',
        'keep *_ecalDigis_*_*',
        'keep *_gctDigis_*_*',

        # Keep RCT regions
        'keep *_simRctDigis_*_*',

        # Keep GenJets
        'keep *_ak5GenJets_*_*',
        'keep *_ak4GenJets_*_*',

        # Keep collections from Stage1
        'keep l1tJetBXVector_*_*_*',
        'keep L1GctJetCands_*_*_*',
        'keep l1extraL1JetParticles_*_*_*',
        'keep *_l1ExtraLayer2_*_*'
    ),
    fileName = cms.untracked.string(edm_filename)
)

# output file
output_filename = 'L1Tree{0}.root'.format(file_append)
print "*** Writing NTuple to {0}".format(output_filename)

process.TFileService = cms.Service("TFileService",
    fileName = cms.string(output_filename)
)

process.output_step = cms.EndPath(process.output)

process.schedule = cms.Schedule(process.p)

if save_EDM:
    print "*** Writing EDM to {0}".format(edm_filename)
    process.schedule.append(process.output_step)

# Spit out filter efficiency at the end.
process.options = cms.untracked.PSet(wantSummary = cms.untracked.bool(True))
