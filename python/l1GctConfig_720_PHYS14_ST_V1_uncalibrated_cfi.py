"""
l1GctConfigProducers setup.

Based on L1TriggerConfig/GctConfigProducers/python/l1GctConfig_cfi.py

For Global Tag PHYS14_ST_V1::All.

*** REMOVES ANY CALIBRATION.***

"""

import FWCore.ParameterSet.Config as cms

L1GctConfigProducers = cms.ESProducer("L1GctConfigProducers",
    JetFinderCentralJetSeed = cms.double(5.0),
    JetFinderForwardJetSeed = cms.double(5.0),
    TauIsoEtThreshold = cms.double(2.0),
    HtJetEtThreshold = cms.double(10.0),
    MHtJetEtThreshold = cms.double(10.0),
    RctRegionEtLSB = cms.double(0.5),
    GctHtLSB = cms.double(0.5),
    ConvertEtValuesToEnergy = cms.bool(False),

    # energy sum eta ranges
    MEtEtaMask = cms.uint32(0x3c000f),
    TEtEtaMask = cms.uint32(0x3c000f),
    MHtEtaMask = cms.uint32(0x3c000f),
    HtEtaMask = cms.uint32(0x3c000f),

    # The CalibrationStyle should be "None", "PiecewiseCubic", "Simple" or "PF"
    # "PowerSeries", "ORCAStyle" are also available, but not recommended
    CalibrationStyle = cms.string('PF'),
    PFCoefficients = cms.PSet(
        nonTauJetCalib0 = cms.vdouble(1.000,0.000,0.000,0.000,0.000,0.000),
        nonTauJetCalib1 = cms.vdouble(1.000,0.000,0.000,0.000,0.000,0.000),
        nonTauJetCalib2 = cms.vdouble(1.000,0.000,0.000,0.000,0.000,0.000),
        nonTauJetCalib3 = cms.vdouble(1.000,0.000,0.000,0.000,0.000,0.000),
        nonTauJetCalib4 = cms.vdouble(1.000,0.000,0.000,0.000,0.000,0.000),
        nonTauJetCalib5 = cms.vdouble(1.000,0.000,0.000,0.000,0.000,0.000),
        nonTauJetCalib6 = cms.vdouble(1.000,0.000,0.000,0.000,0.000,0.000),
        nonTauJetCalib7 = cms.vdouble(1.000,0.000,0.000,0.000,0.000,0.000),
        nonTauJetCalib8 = cms.vdouble(1.000,0.000,0.000,0.000,0.000,0.000),
        nonTauJetCalib9 = cms.vdouble(1.000,0.000,0.000,0.000,0.000,0.000),
        nonTauJetCalib10 = cms.vdouble(1.000,0.000,0.000,0.000,0.000,0.000),
        tauJetCalib0 = cms.vdouble(1.000,0.000,0.000,0.000,0.000,0.000),
        tauJetCalib1 = cms.vdouble(1.000,0.000,0.000,0.000,0.000,0.000),
        tauJetCalib2 = cms.vdouble(1.000,0.000,0.000,0.000,0.000,0.000),
        tauJetCalib3 = cms.vdouble(1.000,0.000,0.000,0.000,0.000,0.000),
        tauJetCalib4 = cms.vdouble(1.000,0.000,0.000,0.000,0.000,0.000),
        tauJetCalib5 = cms.vdouble(1.000,0.000,0.000,0.000,0.000,0.000),
        tauJetCalib6 = cms.vdouble(1.000,0.000,0.000,0.000,0.000,0.000)
    )
)