"""
Config file to run the Stage 2 emulator to make Ntuples.

Now comes with HF!

Stores L1 jets, as well as ak4 GenJets
"""

# Auto generated configuration file
# using: 
# Revision: 1.19 
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v 
# with command line options: l1Ntuple -s RAW2DIGI --era=Run2_2016 --customise=L1Trigger/Configuration/customise_Stage2Calo.Stage2CaloFromRaw --customise=L1Trigger/L1TNtuples/customiseL1Ntuple.L1NtupleEMU --conditions=auto:run2_mc -n 10 --mc --filein=/store/mc/RunIISpring15DR74/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/GEN-SIM-RAW/NhcalZSHFscaleFlat10to30Asympt25ns_MCRUN2_74_V9-v1/00000/003BEF9B-C24E-E511-B4B7-0025905A609E.root --geometry=Extended2016,Extended2016Reco
import FWCore.ParameterSet.Config as cms

from Configuration.StandardSequences.Eras import eras

#############################################################################
# COMMON FLAGS:
#
# To save the EDM content as well:
# (WARNING: DON'T do this for big production - will be HUGE)
save_EDM = False

# Things to append to L1Ntuple/EDM filename (globalTag added later)
file_append = "_Stage2_Spring15MC_HF_10Feb_"

#############################################################################

process = cms.Process('L1Reco',eras.Run2_2016)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.Geometry.GeometryExtended2016Reco_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.StandardSequences.RawToDigi_Data_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.MessageLogger.cerr.FwkReport.reportEvery = 200
process.MessageLogger.suppressWarning = cms.untracked.vstring(
    "l1UpgradeEmuTree",
    # "l1CaloTowerTree",
    # "gtStage2Digis",
    # "gmtStage2Digis",
    'l1ExtraTreeGenAk4'
)

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(1000)
)

# Input source
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring('root://xrootd.unl.edu//store/mc/RunIISpring15DR74/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/GEN-SIM-RAW/NhcalZSHFscaleFlat10to30Asympt25ns_MCRUN2_74_V9-v1/00000/003BEF9B-C24E-E511-B4B7-0025905A609E.root'),
    # fileNames = cms.untracked.vstring('root://xrootd.unl.edu//store/mc/RunIIFall15DR76/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/GEN-SIM-RAW/25nsFlat0to50NzshcalRaw_76X_mcRun2_asymptotic_v12-v1/20000/002DE782-FFA9-E511-9BBB-0025905964A6.root'),
    secondaryFileNames = cms.untracked.vstring()
)

process.options = cms.untracked.PSet(
    wantSummary = cms.untracked.bool(True)
)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('l1Ntuple nevts:10'),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Output definition

process.RECOSIMoutput = cms.OutputModule("PoolOutputModule",
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string(''),
        filterName = cms.untracked.string('')
    ),
    eventAutoFlushCompressedSize = cms.untracked.int32(5242880),
    fileName = cms.untracked.string('l1Ntuple_RAW2DIGI_%s.root' % file_append),
    outputCommands = process.RECOSIMEventContent.outputCommands,
    splitLevel = cms.untracked.int32(0),
)

# Additional output definition

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_mc', '')
# process.GlobalTag = GlobalTag(process.GlobalTag, '76X_mcRun2_asymptotic_v12')
file_append += '_' + process.GlobalTag.globaltag.value()

# Path and EndPath definitions
process.raw2digi_step = cms.Path(process.RawToDigi)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.RECOSIMoutput_step = cms.EndPath(process.RECOSIMoutput)

# Schedule definition
process.schedule = cms.Schedule(process.raw2digi_step,process.endjob_step)
if save_EDM:
    process.schedule.append(process.RECOSIMoutput_step)

# customisation of the process.

# Automatic addition of the customisation function from L1Trigger.Configuration.customise_Stage2Calo
from L1Trigger.Configuration.customise_Stage2Calo import Stage2CaloFromRaw 

# call to customisation function Stage2CaloFromRaw imported from L1Trigger.Configuration.customise_Stage2Calo
process = Stage2CaloFromRaw(process)

# Automatic addition of the customisation function from L1Trigger.L1TNtuples.customiseL1Ntuple
from L1Trigger.L1TNtuples.customiseL1Ntuple import L1NtupleEMU

# call to customisation function L1NtupleRAWEMU imported from L1Trigger.L1TNtuples.customiseL1Ntuple
process = L1NtupleEMU(process)

# End of customisation functions

# Get rid of unnecessary Stage 1 modules
remove_modules = [
    process.L1TRawToDigi,
    process.siPixelDigis,
    process.siStripDigis,
    process.muonCSCDigis,
    process.muonDTDigis,
    process.muonRPCDigis,
    process.castorDigis
]
for mod in remove_modules:
    result = process.RawToDigi.remove(mod)
    if not result:
        raise RuntimeError('Could not remove %s' % mod.label())

# Add L1Tree
process.load('L1Trigger.L1TNtuples.l1Tree_cfi')

# Do ak4 GenJets
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

# Store PU info (nvtx, etc)
process.puInfo = cms.EDAnalyzer("PileupInfo",
    pileupInfoSource = cms.InputTag("addPileupInfo")
)

# Add both GenJets and PU to process path
add_modules = [
    process.genJetToL1JetAk4,
    process.l1ExtraTreeGenAk4,
    process.puInfo,
    process.l1Tree
]

for mod in add_modules:
    process.l1ntuplesim.insert(len(process.l1ntuplesim.moduleNames()), mod)

# Set the right ECAL input for TPs
process.l1CaloTowerEmuTree.ecalToken = cms.untracked.InputTag("ecalDigis", "EcalTriggerPrimitives")

# Use MP jets
process.l1UpgradeEmuTree.jetToken = cms.untracked.InputTag("simCaloStage2Digis", "MP")

# Turn off L1JEC
process.caloStage2Params.jetCalibrationType = cms.string("None")
file_append += "_noJec"

# Set the NTuple filename
process.TFileService.fileName = cms.string("L1Ntuple%s.root" % file_append)
