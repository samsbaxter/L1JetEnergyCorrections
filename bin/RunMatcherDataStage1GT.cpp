// STL headers
#include <iostream>
#include <vector>
#include <utility>
#include <stdexcept>
#include <algorithm>

// ROOT headers
#include "TCanvas.h"
#include "TLegend.h"
#include "TChain.h"
#include "TFile.h"
#include "TDirectoryFile.h"
#include "TTree.h"
#include "TROOT.h"
#include "TSystem.h"
#include "TLorentzVector.h"
#include "TRegexp.h"
#include "TString.h"

// BOOST headers
#include <boost/filesystem.hpp>
// #include <boost/algorithm/string.hpp>
#include <boost/bind.hpp>

// Headers from this package
#include "DeltaR_Matcher.h"
#include "commonRootUtils.h"
#include "L1ExtraTree.h"
#include "PileupInfoTree.h"
#include "RunMatcherOpts.h"
#include "JetDrawer.h"
#include "L1Ntuple.h"

// Other CMSSW headers
#include "CondFormats/L1TObjects/interface/L1CaloGeometry.h"

using std::cout;
using std::endl;
namespace fs = boost::filesystem;

// forward declare fns, implementations after main()
TString getSuffixFromDirectory(const TString& dir);

bool checkTriggerFired(std::vector<TString> hlt, const TString& triggerName);

bool checkTriggerFired(std::vector<ULong64_t> tw1, const int triggerBit, const int bx=2);

template<class T>
std::vector<TLorentzVector> makeTLorentzVectors(std::vector<T> et,
                                                std::vector<T> eta,
                                                std::vector<T> phi);
template<class T>
std::vector<TLorentzVector> makeTLorentzVectorsNoTau(std::vector<T> et,
                                                     std::vector<T> eta,
                                                     std::vector<T> phi,
                                                     std::vector<bool> taujet);
float rankToEt(const float& rank);

float ietaToEta(const float& ieta);

float iphiToPhi(const float& iphi);

// From Len:
float convertRegionEta(int iEta) {
    const double rgnEtaValues[11] = {
        0.174, // HB and inner HE bins are 0.348 wide
        0.522,
        0.870,
        1.218,
        1.566,
        1.956, // Last two HE bins are 0.432 and 0.828 wide
        2.586,
        3.250, // HF bins are 0.5 wide
        3.750,
        4.250,
        4.750
        };
    if(iEta < 11) {
        return -rgnEtaValues[-(iEta - 10)]; // 0-10 are negative eta values
    } else if (iEta < 22) {
        return rgnEtaValues[iEta - 11];     // 11-21 are positive eta values
    }
    return -9;
}

float convertRegionPhi(int iPhi) {
    if (iPhi < 10)
        return 2. * TMath::Pi() * iPhi / 18.;
    if (iPhi < 18)
        return -TMath::Pi() + 2. * TMath::Pi() * (iPhi - 9) / 18.;
    return -9;
}

/**
 * @brief This program implements an instance of Matcher to produce a ROOT file
 * with matching jet pairs from a L1NTuple file produced by
 * python/l1Ntuple_cfg.py. Can also optionally apply correction functions, and
 * emulate the GCT/Stage 1 by sorting & keeping top 4 cen & fwd jets.
 *
 * This is a hacky version - the L1 jets are from Stage1, but becasue it was run
 * in parallel with GCT, they are stored in the gt_ collection, not the L1Extra.
 * Reference jets are still in the RecoTree.
 *
 * @author Robin Aggleton, Nov 2014
 */
int main(int argc, char* argv[]) {

    cout << "Running Matcher for data, Stage 1 special run - getting L1 jets from GT collection" << std::endl;

    // deal with user args
    RunMatcherOpts opts(argc, argv);

    ///////////////////////
    // SETUP INPUT FILES //
    ///////////////////////
    L1Ntuple ntuple(opts.inputFilename());
    L1Analysis::L1AnalysisEventDataFormat * event = ntuple.event_;
    L1Analysis::L1AnalysisGTDataFormat * gt = ntuple.gt_;
    L1Analysis::L1AnalysisRecoJetDataFormat * recoJet = ntuple.recoJet_;
    L1Analysis::L1AnalysisRecoVertexDataFormat * recoVertex = ntuple.recoVertex_;
    // input filename stem (no .root)
    fs::path inPath(opts.inputFilename());
    TString inStem(inPath.stem().c_str());

    ////////////////////////
    // SETUP OUTPUT FILES //
    ////////////////////////

    // setup output file to store results
    // check that we're not overwriting the input file!
    if (opts.outputFilename() == opts.inputFilename()) {
        throw std::runtime_error("Cannot use input filename as output filename!");
    }
    TFile * outFile = openFile(opts.outputFilename(), "RECREATE");

    // setup output tree to store raw variable for quick plotting/debugging
    TTree * outTree = new TTree("valid", "valid");
    // pt/eta/phi are for l1 jets, ptRef, etc are for ref jets
    float out_pt(-1.), out_eta(99.), out_phi(99.), out_rsp(-1.), out_rsp_inv(-1.);
    float out_dr(99.), out_deta(99.), out_dphi(99.);
    float out_ptRef(-1.), out_etaRef(99.), out_phiRef(99.);
    float out_ptDiff(99999.), out_resL1(99.), out_resRef(99.);
    float out_trueNumInteractions(-1.), out_numPUVertices(-1.);
    int out_event(0);

    outTree->Branch("pt", &out_pt, "pt/Float_t");
    outTree->Branch("eta", &out_eta, "eta/Float_t");
    outTree->Branch("phi", &out_phi, "phi/Float_t");
    outTree->Branch("rsp", &out_rsp, "rsp/Float_t"); // response = l1 pT/ ref jet pT
    outTree->Branch("rsp_inv", &out_rsp_inv, "rsp_inv/Float_t"); // response_inverse = ref pT/ l1 jet pT
    outTree->Branch("dr", &out_dr, "dr/Float_t");
    outTree->Branch("deta", &out_deta, "deta/Float_t");
    outTree->Branch("dphi", &out_dphi, "dphi/Float_t");
    outTree->Branch("ptRef", &out_ptRef, "ptRef/Float_t");
    outTree->Branch("etaRef", &out_etaRef, "etaRef/Float_t");
    outTree->Branch("phiRef", &out_phiRef, "phiRef/Float_t");
    outTree->Branch("ptDiff", &out_ptDiff, "ptDiff/Float_t"); // L1 - Ref
    outTree->Branch("resL1", &out_resL1, "resL1/Float_t"); // resolution = L1 - Ref / L1
    outTree->Branch("resRef", &out_resRef, "resRef/Float_t"); // resolution = L1 - Ref / Ref
    outTree->Branch("trueNumInteractions", &out_trueNumInteractions, "trueNumInteractions/Float_t");
    outTree->Branch("numPUVertices", &out_numPUVertices, "numPUVertices/Float_t");
    outTree->Branch("event", &out_event, "event/Int_t");

    Long64_t nEntries = ntuple.GetEntries();
    if (opts.nEvents() > 0 && opts.nEvents() <= nEntries) {
        nEntries = opts.nEvents();
    }
    cout << "Running over " << nEntries << " events." << endl;

    ///////////////////////
    // SETUP JET MATCHER //
    ///////////////////////
    double maxDeltaR(0.7), minRefJetPt(14.), maxRefJetPt(1000.);
    double minL1JetPt(0.), maxL1JetPt(500.), maxJetEta(5);
    std::unique_ptr<Matcher> matcher(new DeltaR_Matcher(maxDeltaR, minRefJetPt, maxRefJetPt, minL1JetPt, maxL1JetPt, maxJetEta));
    std::cout << *matcher << std::endl;

    //////////////////////////////////////////////////
    // SETUP L1CaloGemoetry OBJECT                  //
    // Help convert ieta, iphi to physical eta, phi //
    //////////////////////////////////////////////////
    static const unsigned int numberGctEmJetPhiBins = 18 ;
    static const double gctEmJetPhiBinOffset = -0.5;
    static const unsigned int numberGctEtSumPhiBins = 72 ;
    static const double gctEtSumPhiBinOffset = 0.;
    static const unsigned int numberGctHtSumPhiBins = 0;  // no idea what this should be, doesn't get used
    static const double gctHtSumPhiBinOffset = 0.;
    static const unsigned int numberGctCentralEtaBinsPerHalf = 7 ;
    static const unsigned int numberGctForwardEtaBinsPerHalf = 4 ;
    static const unsigned int etaSignBitOffset = 8 ; // calo sign bit is the 4th bit
    static const std::vector<double> gctEtaBinBoundaries = {0.0000, 0.3480, 0.6950, 1.0440, 1.3920, 1.7400, 2.1720, 3.0000, 3.5000, 4.0000, 4.5000, 5.0000 };
    L1CaloGeometry geometry(numberGctEmJetPhiBins, gctEmJetPhiBinOffset,
                            numberGctEtSumPhiBins, gctEtSumPhiBinOffset,
                            numberGctHtSumPhiBins, gctHtSumPhiBinOffset,
                            numberGctCentralEtaBinsPerHalf, numberGctForwardEtaBinsPerHalf,
                            etaSignBitOffset, gctEtaBinBoundaries);
    // printout regions
    for (unsigned i = 0; i < 2*(numberGctCentralEtaBinsPerHalf + numberGctForwardEtaBinsPerHalf); i ++) {
        cout << i << " : " << geometry.globalEtaBinCenter(i) << " : " << convertRegionEta(i) << endl;
    }
    for (unsigned i = 0; i < numberGctEmJetPhiBins; i ++) {
        cout << i << " : " << geometry.emJetPhiBinCenter(i)  << " : " << convertRegionPhi(i) <<endl;
    }
    // printout towers
    // for (unsigned i = 0; i < numberGctEtSumPhiBins; i ++) {
    //     cout << i << " : " << geometry.etSumPhiBinLowEdge(i) << endl;
    // }
    // cout << numberGctEtSumPhiBins << " : " << geometry.etSumPhiBinHighEdge(numberGctEtSumPhiBins-1) << endl;


    //////////////////////
    // LOOP OVER EVENTS //
    //////////////////////
    // produce matching pairs and store
    for (Long64_t iEntry = 0; iEntry < nEntries; ++iEntry) {

        if (ntuple.GetEntry(iEntry) == 0) {
            break;
        }

        if (iEntry % 10000 == 0) {
            cout << "Entry: " << iEntry << endl;
        }

        // Check HLT bit
        if (!checkTriggerFired(gt->tw1, 56, 2)) {
            continue;
        }

        out_event = event->event;

        // Get vectors of ref & L1 jets from trees
        std::vector<TLorentzVector> refJets = makeTLorentzVectors<double>(recoJet->etCorr, recoJet->eta, recoJet->phi);
        // Need to convert jet rank/ieta/iphi to physical values. Use std::transform to copy
        // gt_ contents to new vector, which we then convert to physical values
        // using the unary operator in std::transform.
        // std::back_inserter is needed in case the original vector is empty - see
        // https://stackoverflow.com/questions/3336198/segfault-on-using-transform-on-a-vector-of-pointers-to-an-abstract-class
        // The boost::bind here is needed becasue we want to use the L1CaloGeometry
        // method from a class instance (geometry).
        // The static_cast is because the emJetPhiBinCenter is overloaded,
        // so we have to tell bind which one we want.
        std::vector<float> jetEt, jetEta, jetPhi;
        std::transform(gt->Rankjet.begin(), gt->Rankjet.end(), std::back_inserter(jetEt), rankToEt);
        std::transform(gt->Etajet.begin(), gt->Etajet.end(), std::back_inserter(jetEta), boost::bind(&L1CaloGeometry::globalEtaBinCenter, geometry, _1));
        // std::transform(gt->Phijet.begin(), gt->Phijet.end(), std::back_inserter(jetPhi), boost::bind(static_cast<double (L1CaloGeometry::*) (unsigned int) const> (&L1CaloGeometry::emJetPhiBinCenter), geometry, _1));
        std::transform(gt->Phijet.begin(), gt->Phijet.end(), std::back_inserter(jetPhi), convertRegionPhi);
        std::vector<TLorentzVector> l1Jets  = makeTLorentzVectorsNoTau<float>(jetEt, jetEta, jetPhi, gt->Taujet);
        // cout << "# refJets: " << refJets.size() << endl;
        // cout << "# l1Jets: " << l1Jets.size() << endl;

        // Pass jets to matcher, do matching
        matcher->setRefJets(refJets);
        matcher->setL1Jets(l1Jets);
        std::vector<MatchedPair> matchResults = matcher->getMatchingPairs();
        // matcher->printMatches(); // for debugging

        // store L1 & ref jet variables in tree
        for (const auto &it: matchResults) {
            // std::cout << it << std::endl;
            out_pt = it.l1Jet().Et();
            out_eta = it.l1Jet().Eta();
            out_phi = it.l1Jet().Phi();
            out_rsp = it.l1Jet().Et()/it.refJet().Et();
            out_rsp_inv =  it.refJet().Et()/it.l1Jet().Et();
            out_dr = it.refJet().DeltaR(it.l1Jet());
            out_deta = it.refJet().Eta() - it.l1Jet().Eta();
            out_dphi = it.refJet().DeltaPhi(it.l1Jet());
            out_ptRef = it.refJet().Pt();
            out_etaRef = it.refJet().Eta();
            out_phiRef = it.refJet().Phi();
            out_ptDiff = it.l1Jet().Et() - it.refJet().Et();
            out_resL1 = out_ptDiff/it.l1Jet().Et();
            out_resRef = out_ptDiff/it.refJet().Et();
            out_numPUVertices = recoVertex->nVtx;
            outTree->Fill();
        }


        // debugging plot - plots eta vs phi of jets
        if (iEntry < opts.drawNumber()) {
            TString label = TString::Format(
                "%.1f < E^{gen}_{T} < %.1f GeV, " \
                "L1 jet %.1f < E^{L1}_{T} < %.1f GeV, |#eta_{jet}| < %.1f",
                minRefJetPt, maxRefJetPt, minL1JetPt, maxL1JetPt, maxJetEta);

            // get jets post pT, eta cuts
            JetDrawer drawer(matcher->getRefJets(), matcher->getL1Jets(), matchResults, label);

            TString pdfname = TString::Format("plots_%s_%s_%s/jets_%lld.pdf",
                inStem.Data(), "reco", "l1", iEntry);
            drawer.drawAndSave(pdfname);
        }

    }

    outTree->Write("", TObject::kOverwrite);

    outFile->Close();

}


/**
 * @brief Get suffix from TDirectory name
 * @details Assumes it starts with "l1ExtraTreeProducer", so
 * e.g. "l1ExtraTreeProducerGctIntern" produces "gctIntern"
 *
 * @param dir Directory name
 * @return Suitable suffix
 */
TString getSuffixFromDirectory(const TString& dir) {
    TString suffix(dir);
    TRegexp re("l1ExtraTreeProducer");
    suffix(re) = "";
    if (suffix == "") suffix = dir;
    return suffix;
}


/**
 * @brief Check if a certain trigger was fired.
 * @details Note, only checks to see if it was fired,
 * not if it was the *only* trigger that was fired.
 *
 * @param hlt Input vector of TStrings of trigger names fired
 * @param triggerName Trigger name - must be exact, no wildcards!
 *
 * @return [description]
 */
bool checkTriggerFired(std::vector<TString> hlt, const TString& triggerName) {
    return std::find(hlt.begin(), hlt.end(), triggerName) != hlt.end();
}

/**
 * @brief Check if certain trigger was fired.
 * @details This methods uses the tw1[] array from the GT branch of the L1Tree,
 * in conjunction with the trigger bit (as an int) and an optional bunch crossing value.
 *
 * @param tw1 Array of ints
 * @param triggerBit trigger bit to select on.
 * @param bx Optional - bunch crossing. Defaults to 2.
 * @return bool corresponding to if trigger fired or not.
 */
bool checkTriggerFired(std::vector<ULong64_t> tw1, const int triggerBit, const int bx) {
    return (tw1[bx]>>triggerBit)&1;
}

/**
 * @brief Make a std::vector of TLorentzVectors out of input vectors of et, eta, phi.
 *
 * @param et [description]
 * @param eta [description]
 * @param phi [description]
 * @return [description]
 */
template<class T>
std::vector<TLorentzVector> makeTLorentzVectors(std::vector<T> et,
                                                std::vector<T> eta,
                                                std::vector<T> phi) {
    // check all same size
    if (et.size() != eta.size() || et.size() != phi.size()) {
        throw range_error("Eta/eta/phi vectors different sizes, cannot make TLorentzVectors");
    }
    std::vector<TLorentzVector> vecs;
    for (unsigned i = 0; i < et.size(); i++) {
        TLorentzVector v;
        v.SetPtEtaPhiM(et.at(i), eta.at(i), phi.at(i), 0);
        vecs.push_back(v);
    }
    return vecs;
}


/**
 * @brief Make a std::vector of TLorentzVectors out of input vectors of et, eta, phi.
 * Also includes requirement that jets are NOT taus
 *
 * @param et [description]
 * @param eta [description]
 * @param phi [description]
 * @param taujet Flag if jet is tau.
 * @return [description]
 */
template <class T>
std::vector<TLorentzVector> makeTLorentzVectorsNoTau(std::vector<T> et,
                                                     std::vector<T> eta,
                                                     std::vector<T> phi,
                                                     std::vector<bool> taujet) {
    // check all same size
    if (et.size() != eta.size() || et.size() != phi.size()) {
        throw range_error("Eta/eta/phi vectors different sizes, cannot make TLorentzVectors");
    }
    std::vector<TLorentzVector> vecs;
    for (unsigned i = 0; i < et.size(); i++) {
        if (!taujet.at(i)) {
            TLorentzVector v;
            v.SetPtEtaPhiM(et.at(i), eta.at(i), phi.at(i), 0);
            vecs.push_back(v);
        }
    }
    return vecs;
}


float rankToEt(const float& rank) {
    return rank * 4.;
}

