"""
l1GctConfigProducers setup.

Based on L1TriggerConfig/GctConfigProducers/python/l1GctConfig_cfi.py

For Global Tag PHYS14_ST_V1::All, made with CMSSW 7_4_2, using QCD Phys14 samples,
using new RCT calibrations L1RCTParametersRcd_L1TDevelCollisions_ExtendedScaleFactorsV2.
For central eta bins only.

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
        nonTauJetCalib0 = cms.vdouble(3.32079045,30.10690152,2.91713150,-206.73606994,0.00701027,-20.22374281),
        nonTauJetCalib1 = cms.vdouble(3.93700194,36.15657315,3.20011833,-152.55844469,0.00730948,-18.18607858),
        nonTauJetCalib2 = cms.vdouble(4.44141804,23.10539131,2.54369409,-70.15055832,0.00637209,-17.15121238),
        nonTauJetCalib3 = cms.vdouble(3.74913089,17.29783839,2.08816697,-62.47699760,0.00647514,-17.46825338),
        nonTauJetCalib4 = cms.vdouble(2.80136367,9.88887837,1.25489177,-47.96012471,0.00635714,-18.26461837),
        nonTauJetCalib5 = cms.vdouble(1.15728445,2.53081427,0.01955215,-25.17356423,0.00756861,-20.27948286),
        nonTauJetCalib6 = cms.vdouble(1.07080569,2.69627596,0.38780290,-22.58360831,0.00770725,-20.49433274),
        nonTauJetCalib7 = cms.vdouble(1.117,2.382,1.769,0.0,-1.306,-0.4741   ), # OLD HF CALIBS!
        nonTauJetCalib8 = cms.vdouble(1.634,-1.01,0.7184,1.639,0.6727,-0.2129),
        nonTauJetCalib9 = cms.vdouble(0.9862,3.138,4.672,2.362,1.55,-0.7154  ),
        nonTauJetCalib10 = cms.vdouble(1.245,1.103,1.919,0.3054,5.745,0.8622 ),
        tauJetCalib0 = cms.vdouble(3.32079045,30.10690152,2.91713150,-206.73606994,0.00701027,-20.22374281),
        tauJetCalib1 = cms.vdouble(3.93700194,36.15657315,3.20011833,-152.55844469,0.00730948,-18.18607858),
        tauJetCalib2 = cms.vdouble(4.44141804,23.10539131,2.54369409,-70.15055832,0.00637209,-17.15121238),
        tauJetCalib3 = cms.vdouble(3.74913089,17.29783839,2.08816697,-62.47699760,0.00647514,-17.46825338),
        tauJetCalib4 = cms.vdouble(2.80136367,9.88887837,1.25489177,-47.96012471,0.00635714,-18.26461837),
        tauJetCalib5 = cms.vdouble(1.15728445,2.53081427,0.01955215,-25.17356423,0.00756861,-20.27948286),
        tauJetCalib6 = cms.vdouble(1.07080569,2.69627596,0.38780290,-22.58360831,0.00770725,-20.49433274)
    )
)