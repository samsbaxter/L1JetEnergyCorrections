"""
l1GctConfigProducers setup.

Based on L1TriggerConfig/GctConfigProducers/python/l1GctConfig_cfi.py

For Global Tag PHYS14_ST_V1::All, made with CMSSW 7_2_0, for central eta bins only

If you want to change the JEC, plug your own into PFCoefficients arg below.
(Conveniently, the bin/correction_LUT_plot.py script outputs in a nice format
so you can just copy and paste)

IMPORTANT: If you are using a different Global Tag, YOU WILL NEED TO CHANGE THIS
(well, at least check it)

Note: PF coefficient precision is important, particularly if [3] is large,
then precision of [4] is crucial.
The difference between quoting coefficients to 3dp and 6dp can change the
correction factor between -1.27 to 2.15 for example!
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
        nonTauJetCalib0 = cms.vdouble(3.01791485,104.05404643,4.37671951,-511.10059192,0.00975609,-17.19462193),
        nonTauJetCalib1 = cms.vdouble(6.51467316,55.13357477,4.42877284,-75.99041992,0.00574098,-16.07076961),
        nonTauJetCalib2 = cms.vdouble(2.66631385,59.40320962,3.64453392,-458.28002325,0.00869394,-19.25715247),
        nonTauJetCalib3 = cms.vdouble(0.71562578,54.71640347,2.72016310,-9009.00062999,0.01044813,-24.07475734),
        nonTauJetCalib4 = cms.vdouble(1.39149927,31.51196317,2.49437717,-533.64858609,0.01071669,-18.94264462),
        nonTauJetCalib5 = cms.vdouble(1.56945764,10.19680631,1.61637149,-37.03219196,0.00785145,-17.15336214),
        nonTauJetCalib6 = cms.vdouble(1.57965654,9.64485987,1.84352989,-53.54520963,0.00818620,-18.04202617),
        nonTauJetCalib7 = cms.vdouble(1.000,0.000,0.000,0.000,0.000,0.000),
        nonTauJetCalib8 = cms.vdouble(1.000,0.000,0.000,0.000,0.000,0.000),
        nonTauJetCalib9 = cms.vdouble(1.000,0.000,0.000,0.000,0.000,0.000),
        nonTauJetCalib10 = cms.vdouble(1.000,0.000,0.000,0.000,0.000,0.000),
        tauJetCalib0 = cms.vdouble(3.01791485,104.05404643,4.37671951,-511.10059192,0.00975609,-17.19462193),
        tauJetCalib1 = cms.vdouble(6.51467316,55.13357477,4.42877284,-75.99041992,0.00574098,-16.07076961),
        tauJetCalib2 = cms.vdouble(2.66631385,59.40320962,3.64453392,-458.28002325,0.00869394,-19.25715247),
        tauJetCalib3 = cms.vdouble(0.71562578,54.71640347,2.72016310,-9009.00062999,0.01044813,-24.07475734),
        tauJetCalib4 = cms.vdouble(1.39149927,31.51196317,2.49437717,-533.64858609,0.01071669,-18.94264462),
        tauJetCalib5 = cms.vdouble(1.56945764,10.19680631,1.61637149,-37.03219196,0.00785145,-17.15336214),
        tauJetCalib6 = cms.vdouble(1.57965654,9.64485987,1.84352989,-53.54520963,0.00818620,-18.04202617)
    )
)