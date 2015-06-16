import FWCore.ParameterSet.Config as cms

"""
Make L1Ntuples from RAW, for use in L1JetEnergyCorrections.

Legacy GCT setup, with option to re-run the RCT to include new RCT calibs.
Produces GCT internal jet collection with finer granularity & no filtering
to do calibrations properly.

Please check the switches below. You can rerun the RCT, add in new RCT or GCT calibs,
save the EDM collections for debugging, and dump RCT params.

YOU MUST RUN WITH CMSSW 742 OR NEWER TO PICK UP THE NEW RCT CALIBS.
"""

##############################
# Some handy options
##############################

# To dump RCT parameters for testing purposes:
dump_RCT = False

# To save the EDM content as well:
# (WARNING: DON'T do this for big production - will be HUGE)
save_EDM = True

# Global tag (note, you must ensure it matches input file)
gt = 'MCRUN2_74_V8'  # for Spring14 NeutrinoGun sample
# gt = 'POSTLS170_V7'

# Things to append to L1Ntuple/EDM filename
# (if using new RCT calibs, this gets auto added)
file_append = "_NeutrinoGun_"+gt

###################################################################
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
##############################
process.gctDigis.numberOfGctSamplesToUnpack = cms.uint32(1)
# This will actually produce the internal jet collection
process.simGctDigis.writeInternalData = cms.bool(True)

# To pickup new RCT calibrations, we need to remake the regions and pass
# those new regions to the GCT emulator. To rerun the RCT, we need the ECAL
# and HCAL TPs. Unfortunately, there is a bug in the hcalDigis module (until
# 7_3_5?) that doesn't unpack correctly, so you may have to remake them.
print "*** Re-running RCT"

# Remake the HCAL TPs since hcalDigis outputs nothing in MC made with CMSSW
# earlier than 735 (not sure exactly which version, certainly works in Spring15)
# But make sure you use the unsupressed digis, not the hcalDigis
process.load('SimCalorimetry.HcalTrigPrimProducers.hcaltpdigi_cff')
process.simHcalTriggerPrimitiveDigis.inputLabel = cms.VInputTag(
    cms.InputTag('simHcalUnsuppressedDigis'),
    cms.InputTag('simHcalUnsuppressedDigis')
)

# Rerun the RCT emulator using the TPs
# If the hcalDigis is empty (MC made pre 740), then instead use:
process.simRctDigis.hcalDigis = cms.VInputTag(cms.InputTag('simHcalTriggerPrimitiveDigis'))
# process.simRctDigis.hcalDigis = cms.VInputTag(cms.InputTag('hcalDigis'))
process.simRctDigis.ecalDigis = cms.VInputTag(cms.InputTag('ecalDigis', 'EcalTriggerPrimitives' ))

# Rerun the GCT emulator using the RCT regions, including intern collections
process.simGctDigisRCT = process.simGctDigis.clone()
process.simGctDigisRCT.inputLabel = cms.InputTag('simRctDigis')

print "*** Using whatever RCT calibs the sample was made with"
process.GlobalTag.globaltag = cms.string(gt+'::All')


process.p = cms.Path(
    # process.RawToDigi
    process.gctDigis # unpack regions, TPs, etc
    *process.ecalDigis
    *process.ecalPreshowerDigis
    *process.scalersRawToDigi
    *process.hcalDigis
    *process.simHcalTriggerPrimitiveDigis
    *process.simRctDigis
)
if dump_RCT:
    process.l1RCTParametersTest = cms.EDAnalyzer("L1RCTParametersTester")  # don't forget to include me in a cms.Path()
    process.p *= process.l1RCTParametersTest

################################
# Job options for filenames, etc
################################

# output file
output_filename = 'L1Tree{0}.root'.format(file_append)
print "*** Writing NTuple to {0}".format(output_filename)

process.TFileService = cms.Service("TFileService",
    fileName = cms.string(output_filename)
)

process.options = cms.untracked.PSet(SkipEvent = cms.untracked.vstring('ProductNotFound'))

process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(1))

fileNames = cms.untracked.vstring('root://xrootd.unl.edu//store/mc/Spring14dr/Neutrino_Pt-2to20_gun/GEN-SIM-RAW/Flat20to50_BX50_POSTLS170_V7-v1/00000/006E14BB-1125-E411-A566-00266CFFA25C.root')

process.source = cms.Source ("PoolSource",
                             fileNames=fileNames
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
