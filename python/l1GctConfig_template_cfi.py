"""
l1GctConfigProducers setup.

Based on L1TriggerConfig/GctConfigProducers/python/l1GctConfig_cfi.py

The settings here are for Global Tag PHYS14_ST_V1::All, made with CMSSW 7_2_0,
for central eta bins only

If you want to change the JEC, plug your own into PFCoefficients arg below.
(Conveniently, the bin/correction_LUT_plot.py script outputs in a nice format
so you can just copy and paste)

IMPORTANT: If you are using a different Global Tag, YOU WILL NEED TO CHANGE THIS
(well, at least check it)

To check the GCT configuration, use the checkGctConfig_cfg script.

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
        nonTauJetCalib0 = cms.vdouble(3.018,104.054,4.377,-511.101,0.010,-17.195),
        nonTauJetCalib1 = cms.vdouble(6.515,55.134,4.429,-75.990,0.006,-16.071),
        nonTauJetCalib2 = cms.vdouble(2.666,59.403,3.645,-458.280,0.009,-19.257),
        nonTauJetCalib3 = cms.vdouble(0.716,54.716,2.720,-9009.001,0.010,-24.075),
        nonTauJetCalib4 = cms.vdouble(1.391,31.512,2.494,-533.649,0.011,-18.943),
        nonTauJetCalib5 = cms.vdouble(1.569,10.197,1.616,-37.032,0.008,-17.153),
        nonTauJetCalib6 = cms.vdouble(1.580,9.645,1.844,-53.545,0.008,-18.042),
        nonTauJetCalib7 = cms.vdouble(1.000,0.000,0.000,0.000,0.000,0.000),
        nonTauJetCalib8 = cms.vdouble(1.000,0.000,0.000,0.000,0.000,0.000),
        nonTauJetCalib9 = cms.vdouble(1.000,0.000,0.000,0.000,0.000,0.000),
        nonTauJetCalib10 = cms.vdouble(1.000,0.000,0.000,0.000,0.000,0.000),
        tauJetCalib0 = cms.vdouble(3.018,104.054,4.377,-511.101,0.010,-17.195),
        tauJetCalib1 = cms.vdouble(6.515,55.134,4.429,-75.990,0.006,-16.071),
        tauJetCalib2 = cms.vdouble(2.666,59.403,3.645,-458.280,0.009,-19.257),
        tauJetCalib3 = cms.vdouble(0.716,54.716,2.720,-9009.001,0.010,-24.075),
        tauJetCalib4 = cms.vdouble(1.391,31.512,2.494,-533.649,0.011,-18.943),
        tauJetCalib5 = cms.vdouble(1.569,10.197,1.616,-37.032,0.008,-17.153),
        tauJetCalib6 = cms.vdouble(1.580,9.645,1.844,-53.545,0.008,-18.042)
    )
)
