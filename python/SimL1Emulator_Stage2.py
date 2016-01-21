"""
Config file to run the Stage 2 emulator to make Ntuples.

Stores L1 jets, as well as ak4 GenJets
"""

import FWCore.ParameterSet.Config as cms

# To save the EDM content as well:
# (WARNING: DON'T do this for big production - will be HUGE)
save_EDM = False

# Global tag (note, you must ensure it matches input file)
# You don't need the "::All"!
# gt = 'MCRUN2_74_V9'  # for Spring15 AVE20BX25
# gt = 'MCRUN2_75_V5'  # for Spring15 AVE20BX25 in 75X
gt = '76X_mcRun2_asymptotic_v5'  # for 76X MC

# Things to append to L1Ntuple/EDM filename
file_append = "_Stage2_22Nov"

# Add in a filename appendix here for your GlobalTag.
file_append += "_" + gt

###################################################################
process = cms.Process('L1NTUPLE')

process.load('Configuration.StandardSequences.Services_cff')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load("Configuration.StandardSequences.RawToDigi_cff")
process.RawToDigi.remove(process.caloStage2Digis)
process.RawToDigi_noTk.remove(process.caloStage2Digis)
process.load('Configuration.StandardSequences.L1Reco_cff')
process.load('Configuration.StandardSequences.Reconstruction_cff')
process.load('Configuration/StandardSequences/MagneticField_cff')
process.load('Configuration/StandardSequences/EndOfProcess_cff')
# process.load("JetMETCorrections.Configuration.DefaultJEC_cff")
process.load('Configuration/StandardSequences/SimL1Emulator_cff')
process.load('Configuration/StandardSequences/FrontierConditions_GlobalTag_condDBv2_cff')
from Configuration.AlCa.GlobalTag_condDBv2 import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, gt)

# Select the Message Logger output you would like to see:
process.load('FWCore.MessageService.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 200
process.MessageLogger.suppressWarning = cms.untracked.vstring(
    "l1ExtraTreeGenAk4",
    "l1UpgradeTree",
    "l1UpgradeTreeMP",
    "l1UpgradeSimTree",
    "l1UpgradeSimTreeMP",
    "csctfDigis"
)

##############################
# Load up Stage 2 emulator
##############################
process.load('L1Trigger.L1TCalorimeter.caloStage2Params_cfi')
process.load('L1Trigger.L1TCalorimeter.simCaloStage2Layer1Digis_cfi')
process.load('L1Trigger.L1TCalorimeter.simCaloStage2Digis_cfi')

process.simCaloStage2Layer1Digis.ecalToken = cms.InputTag('ecalDigis', 'EcalTriggerPrimitives')
process.simCaloStage2Layer1Digis.hcalToken = cms.InputTag('hcalDigis')

# Change jet seed to 1.5 GeV
process.caloStage2Params.jetSeedThreshold = cms.double(1.5)
file_append += "_jetSeed1p5"

# My new calibs
process.caloStage2Params.jetCalibrationType = cms.string("function6PtParams22EtaBins")
# Vector with 6 parameters for eta bin, from low eta to high
# 1,0,1,0,1,1 gives no correction
# must be in this form as may require > 255 arguments
jetCalibParamsVector = cms.vdouble()
jetCalibParamsVector.extend([
    1,0,1,0,1,1, # No calibrations in HF bins
    1,0,1,0,1,1,
    1,0,1,0,1,1,
    1,0,1,0,1,1,
    5.24246537,6.60700156,1.22785564,-13.69502129,0.00196905,-20.27233882,
    0.90833682,6.50791252,0.61922676,-209.49688550,0.01329731,-18.51593877,
    5.79849519,12.80862387,1.33405525,-25.10166231,0.00275828,-20.04923840,
    6.78385680,23.01868950,2.25627456,-39.95709157,0.00390259,-17.70111029,
    3.48234814,13.34746568,1.48348018,-46.10680359,0.00447602,-20.97512052,
    4.45650191,16.52912233,1.97499544,-41.54895663,0.00394956,-20.44045700,
    3.18556244,25.56760298,2.51677342,-103.26529010,0.00678420,-18.73657857,
    3.18556244,25.56760298,2.51677342,-103.26529010,0.00678420,-18.73657857,
    4.45650191,16.52912233,1.97499544,-41.54895663,0.00394956,-20.44045700,
    3.48234814,13.34746568,1.48348018,-46.10680359,0.00447602,-20.97512052,
    6.78385680,23.01868950,2.25627456,-39.95709157,0.00390259,-17.70111029,
    5.79849519,12.80862387,1.33405525,-25.10166231,0.00275828,-20.04923840,
    0.90833682,6.50791252,0.61922676,-209.49688550,0.01329731,-18.51593877,
    5.24246537,6.60700156,1.22785564,-13.69502129,0.00196905,-20.27233882,
    1,0,1,0,1,1, # No calibrations in HF bins
    1,0,1,0,1,1,
    1,0,1,0,1,1,
    1,0,1,0,1,1
])
process.caloStage2Params.jetCalibrationParams  = jetCalibParamsVector
file_append += "_newJec22Nov_calibMin1p5"

# Turn off calibrations
# process.caloStage2Params.jetCalibrationType = cms.string("None")
# file_append += "_noJec"

process.load('L1Trigger.L1TNtuples.L1NtupleRAW_cff')
process.l1CaloTowerSimTree.ecalToken = cms.untracked.InputTag("ecalDigis", "EcalTriggerPrimitives")
process.l1CaloTowerSimTree.hcalToken = cms.untracked.InputTag("hcalDigis")

process.L1NtupleRAW.remove(process.l1CaloTowerTree)  # remove HW trees
process.L1NtupleRAW.remove(process.l1UpgradeTree)

# Add in tree for MP jets (before demuxing)
process.l1UpgradeSimTreeMP = process.l1UpgradeSimTree.clone()
process.l1UpgradeSimTreeMP.jetToken = cms.untracked.InputTag('simCaloStage2Digis', 'MP')

##############################
# Do ak4 GenJets
##############################
# Convert ak4 genjets to L1JetParticle objects
process.genJetToL1JetAk4 = cms.EDProducer("GenJetToL1Jet",
    genJetSource = cms.InputTag("ak4GenJets")
)

# Put in another L1ExtraTree as cenJets
process.load("L1Trigger.L1TNtuples.l1ExtraTree_cfi")
process.l1ExtraTreeGenAk4 = process.l1ExtraTree.clone()
process.l1ExtraTreeGenAk4.nonIsoEmToken = cms.untracked.InputTag("")
process.l1ExtraTreeGenAk4.isoEmToken = cms.untracked.InputTag("")
process.l1ExtraTreeGenAk4.tauJetToken = cms.untracked.InputTag("")
process.l1ExtraTreeGenAk4.isoTauJetToken = cms.untracked.InputTag("")
process.l1ExtraTreeGenAk4.cenJetToken = cms.untracked.InputTag("genJetToL1JetAk4:GenJets")
process.l1ExtraTreeGenAk4.fwdJetToken = cms.untracked.InputTag("")
process.l1ExtraTreeGenAk4.muonToken = cms.untracked.InputTag("")
process.l1ExtraTreeGenAk4.metToken = cms.untracked.InputTag("")
process.l1ExtraTreeGenAk4.mhtToken = cms.untracked.InputTag("")
process.l1ExtraTreeGenAk4.hfRingsToken = cms.untracked.InputTag("")
process.l1ExtraTreeGenAk4.maxL1Extra = cms.uint32(50)

##############################
# Store PU info (nvtx, etc)
##############################
process.puInfo = cms.EDAnalyzer("PileupInfo",
    pileupInfoSource = cms.InputTag("addPileupInfo")
)

##############################
# Overall path
##############################

process.p = cms.Path(
    process.ecalDigis # ecal unpacker
    *process.hcalDigis # hcal unpacker
    *process.simCaloStage2Layer1Digis
    *process.simCaloStage2Digis
    *process.L1NtupleRAW
    *process.l1UpgradeSimTreeMP
    *process.genJetToL1JetAk4 # convert ak4GenJets to L1Jet objs
    *process.l1ExtraTreeGenAk4 # ak4GenJets in cenJet branch
    *process.puInfo # store nVtx info
    )

##############################
# Input/output & standard stuff
##############################
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(100))

# Input source

# Some default testing files
if gt in ['PHYS14_25_V3', 'PHYS14_25_V2', 'MCRUN2_74_V8']:
    fileNames = cms.untracked.vstring(
        'root://xrootd.unl.edu//store/mc/Phys14DR/QCD_Pt-120to170_Tune4C_13TeV_pythia8/GEN-SIM-RAW/AVE20BX25_tsg_castor_PHYS14_25_V3-v1/00000/004DD38A-2B8E-E411-8E4F-003048FFD76E.root'
        )
elif gt in ['76X_mcRun2_asymptotic_v5', 'MCRUN2_75_V5', 'MCRUN2_74_V9']:
    fileNames = cms.untracked.vstring(
        # 'root://xrootd.unl.edu//store/mc/RunIISpring15DR74/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/GEN-SIM-RAW/NhcalZSHFscaleFlat10to30Asympt25ns_MCRUN2_74_V9-v1/00000/00EA9A04-CD4E-E511-8F7B-001517E7410C.root'
        # 'root://xrootd.unl.edu//store/mc/RunIISpring15DR74/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/GEN-SIM-RAW/NhcalZSHFscaleFlat10to30Asympt25ns_MCRUN2_74_V9-v1/00000/003BEF9B-C24E-E511-B4B7-0025905A609E.root'
        'root://xrootd.unl.edu//store/mc/RunIISpring15DR74/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/GEN-SIM-RAW/NhcalZSHFscaleFlat10to30Asympt25ns_MCRUN2_74_V9-v1/00000/00EA9A04-CD4E-E511-8F7B-001517E7410C.root'
        # 'root://xrootd.unl.edu//store/mc/RunIISpring15DR74/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/GEN-SIM-RAW/NhcalZSHFscaleFlat10to30Asympt25ns_MCRUN2_74_V9-v1/00000/000E6EAA-E44E-E511-8C25-0025905A60AA.root'
        )
else:
    raise RuntimeError("No file to use with GT: %s" % gt)

process.source = cms.Source("PoolSource",
                            fileNames = fileNames
                            )

edm_filename = 'SimStage2Emulator{0}.root'.format(file_append)
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

        # Keep GenJets
        'keep *_ak4GenJets_*_*',

        # Keep collections from Stage2
        'keep *_*_*_L1NTUPLE'
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
