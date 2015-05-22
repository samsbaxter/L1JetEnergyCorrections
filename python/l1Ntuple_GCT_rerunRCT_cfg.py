import FWCore.ParameterSet.Config as cms

"""
Make L1Ntuples from RAW, for use in L1JetEnergyCorrections.

Legacy GCT setup, with option to re-run the RCT to include new RCT calibs.
Produces GCT internal jet collection with finer granularity & no filtering
to do calibrations properly.

Note that there are several hacks in here, after much discussion with HCAL/RCT
people.

YOU MUST RUN WITH CMSSW 742 OR NEWER TO PICK UP THE NEW RCT CALIBS.
"""

##############################
# Some handy options
##############################
# To remake the RCT regions:
rerun_RCT = True

# To use new RCT calibrations (auto enable rerun_RCT):
new_RCT_calibs = True
rerun_RCT = rerun_RCT | new_RCT_calibs

# To dump RCT parameters for testing purposes:
dump_RCT = True

# To use new set of GCT calibs
# new_GCT_calibs = False

# To save the EDM content as well:
# (WARNING: DON'T do this for big production - will be HUGE)
save_EDM = True

# Global tag (note, you must ensure it matches input file)
# gt = 'MCRUN2_74_V6'  # for Spring15 AVE30BX50 sample
gt = 'PHYS14_ST_V1'  # for Phys14 AVE30BX50 sample

# Things to append to L1Ntuple/EDM filename
file_append = "_Spring15"

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
# Rerun the GCT for internal jet collection
##############################
process.gctDigis.numberOfGctSamplesToUnpack = cms.uint32(1)
# This will actually produce the internal jet collection
process.simGctDigis.writeInternalData = cms.bool(True)

if rerun_RCT:
    # To pickup new RCT calibrations, we need to remake the regions and pass
    # those new regions to the GCT emulator. To rerun the RCT, we need the ECAL
    # and HCAL TPs. Unfortunately, there is a bug in the hcalDigis module (until
    # 7_3_5?) that doesn't unpack correctly, so you may have to remake them.
    # print "*** Re-running RCT"
    file_append += "_rerunRCT"

    # Remake the HCAL TPs since hcalDigis outputs nothing in CMSSW earlier than 735
    # (NOT CHECKED PRECISELY WHICH VERSION, cerntainly works in 740)
    # But make sure you use the unsupressed digis, not the hcalDigis
    # process.load('SimCalorimetry.HcalTrigPrimProducers.hcaltpdigi_cff')
    # process.simHcalTriggerPrimitiveDigis.inputLabel = cms.VInputTag(
    #     cms.InputTag('simHcalUnsuppressedDigis'),
    #     cms.InputTag('simHcalUnsuppressedDigis')
    # )

    # Rerun the RCT emulator using the TPs
    # If the hcalDigis is empty (pre 740), then instead use:
    # process.simRctDigis.hcalDigis = cms.VInputTag(cms.InputTag('simHcalTriggerPrimitiveDigis'))
    process.simRctDigis.hcalDigis = cms.VInputTag(cms.InputTag('hcalDigis'))
    process.simRctDigis.ecalDigis = cms.VInputTag(cms.InputTag('ecalDigis', 'EcalTriggerPrimitives' ))

    # Rerun the GCT emulator using the RCT regions, including intern collections
    process.simGctDigisRCT = process.simGctDigis.clone()
    process.simGctDigisRCT.inputLabel = cms.InputTag('simRctDigis')
else:
    # If we don't want to re-run the RCT (i.e use whatever calibs the sample
    # was made with), we can just take the regions from the unpacker, and feed
    # them into the GCT.
    print "*** Not re-running RCT, using regions from the unpacker"
process.simGctDigis.inputLabel = cms.InputTag('gctDigis')

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
# Need to make ak5, not included in GEN-SIM-RAW for Spring15 or later
process.load('RecoJets.Configuration.GenJetParticles_cff')
process.load('RecoJets.Configuration.RecoGenJets_cff')
process.antiktGenJets = cms.Sequence(process.genJetParticles * process.ak5GenJets)

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
# Need to make ak4, not included in GEN-SIM-RAW for earlier than Phys14
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
if new_RCT_calibs:
    print "*** Using new RCT calibs"
    process.load('Configuration/StandardSequences/FrontierConditions_GlobalTag_condDBv2_cff')
    from Configuration.AlCa.GlobalTag_condDBv2 import GlobalTag
    # Format: map{(record,label):(tag,connection),...}
    recordOverrides = { ('L1RCTParametersRcd', None) : ('L1RCTParametersRcd_L1TDevelCollisions_ExtendedScaleFactorsV2', None) }
    process.GlobalTag = GlobalTag(process.GlobalTag, gt, recordOverrides)
    file_append += '_newnewRCT'
else:
    process.GlobalTag.globaltag = cms.string(gt+'::All')

###########################################################
# Load new GCT jet calibration coefficients - edit the l1GctConfig file
# accordingly.
# Since it's an ESProducer, no need to put it in process.p
###########################################################
# if new_GCT_calibs:
#     print "*** Using new GCT calibs"
#     file_append += "_newGCT"
#     process.load('L1Trigger.L1JetEnergyCorrections.l1GctConfig_720_PHYS14_ST_V1_central_cfi')


process.p = cms.Path(
    # process.RawToDigi
    process.gctDigis # unpack regions, TPs, etc
    +process.ecalDigis
    +process.ecalPreshowerDigis
    +process.scalersRawToDigi
    +process.hcalDigis
    # +process.simHcalTriggerPrimitiveDigis
    +process.simRctDigis
    +process.simGctDigis
    +process.simGctDigisRCT
    # +process.l1extraParticles
    # +process.gctInternJetToL1Jet
    # +process.antiktGenJets  # for AK5 GenJet - not needed in Phys14 samples
    # +process.genJetToL1JetAk5
    # +process.genJetToL1JetAk4
    # +process.l1ExtraTreeProducer # standard gctDigis in cenJet coll
    # +process.l1ExtraTreeProducerGctIntern # gctInternal jets in cenJet coll
    # +process.l1ExtraTreeProducerGenAk5 # ak5GenJets in cenJet coll
    # +process.l1ExtraTreeProducerGenAk4 # ak4GenJets in cenJet coll
    # +process.puInfo # store nVtx info
)

if dump_RCT:
    process.l1RCTParametersTest = cms.EDAnalyzer("L1RCTParametersTester")  # don't forget to include me in a cms.Path()
    process.p += process.l1RCTParametersTest

################################
# Job options for filenames, etc
################################

# output file
output_filename = 'L1Tree{0}.root'.format(file_append)
print "*** Writing NTuple to {0}".format(output_filename)

process.TFileService = cms.Service("TFileService",
    fileName = cms.string(output_filename)
)

# SkipEvent = cms.untracked.vstring('ProductNotFound')

process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(1))

# readFiles = cms.untracked.vstring()
process.source = cms.Source ("PoolSource",
                             # fileNames = readFiles,
                            # fileNames = cms.untracked.vstring('root://xrootd.unl.edu//store/mc/Spring14dr/QCD_Pt-15to3000_Tune4C_Flat_13TeV_pythia8/GEN-SIM-RAW/Flat20to50_POSTLS170_V5-v1/00000/02029D87-36DE-E311-B786-20CF3027A56B.root')
                            # fileNames = cms.untracked.vstring('file:QCD_Pt-80to120_Phys14_AVE30BX50.root')
                            # fileNames = cms.untracked.vstring('root://xrootd.unl.edu//store/mc/Phys14DR/QCD_Pt-80to120_Tune4C_13TeV_pythia8/GEN-SIM-RAW/AVE30BX50_tsg_castor_PHYS14_ST_V1-v1/00000/001CB7A6-E28A-E411-B76F-0025905A611C.root')
                            fileNames = cms.untracked.vstring('root://xrootd.unl.edu//store/mc/Phys14DR/QCD_Pt-120to170_Tune4C_13TeV_pythia8/GEN-SIM-RAW/AVE30BX50_tsg_castor_PHYS14_ST_V1-v1/00000/008671F0-508B-E411-8D9D-003048FFCC2C.root')
                            # fileNames = cms.untracked.vstring('root://xrootd.unl.edu//store/mc/RunIISpring15Digi74/QCD_Pt_170to300_TuneCUETP8M1_13TeV_pythia8/GEN-SIM-RAW/AVE_30_BX_50ns_tsg_MCRUN2_74_V6-v1/00000/00D772EF-41F3-E411-90EF-0025907FD242.root')
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
