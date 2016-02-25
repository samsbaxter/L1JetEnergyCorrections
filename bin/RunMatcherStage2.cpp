#include <fstream>
#include <map>
#include <algorithm>

// ROOT headers
#include "TChain.h"
#include "TFile.h"
#include "TTree.h"
#include "TROOT.h"
#include "TSystem.h"
#include "TMath.h"

// BOOST headers
#include <boost/filesystem.hpp>
#include <boost/algorithm/string.hpp>
#include <boost/algorithm/string/predicate.hpp>
#include <boost/lexical_cast.hpp>

// Headers from L1TNtuples
#include "L1Trigger/L1TNtuples/interface/L1AnalysisEventDataFormat.h"
#include "L1Trigger/L1TNtuples/interface/L1AnalysisL1ExtraDataFormat.h"
#include "L1Trigger/L1TNtuples/interface/L1AnalysisL1UpgradeDataFormat.h"

// Headers from this package
#include "DeltaR_Matcher.h"
#include "commonRootUtils.h"
#include "L1GenericTree.h"
#include "PileupInfoTree.h"
#include "RunMatcherOpts.h"
#include "JetDrawer.h"
#include "runMatcherUtils.h"

using std::cout;
using std::endl;
using L1Analysis::L1AnalysisEventDataFormat;
using L1Analysis::L1AnalysisL1ExtraDataFormat;
using L1Analysis::L1AnalysisL1UpgradeDataFormat;
using boost::lexical_cast;

namespace fs = boost::filesystem;

std::map<int, int> load_lut(std::string filename);
int getAbsIEta(float eta);
int getAddress(int iet, int ieta);
float getCorrectedEt(std::map<int, int> & pt_lut, std::map<int, int> & corr_lut,
                     float et, float eta);
float iPhiToPhi(int iphi);
std::vector<TLorentzVector> getJetsForHTT(std::vector<TLorentzVector> jets);
bool passHTTCut(TLorentzVector jet);
float scalarSumPt(std::vector<TLorentzVector> jets);

/**
 * @brief This program implements an instance of Matcher to produce a ROOT file
 * with matching jet pairs from a L1NTuple file produced by
 * python/SimL1Emulator_Stage2.py.
 *
 * @author Robin Aggleton, Nov 2014
 */
int main(int argc, char* argv[]) {

    cout << "Running Matcher" << std::endl;

    // deal with user args
    RunMatcherOpts opts(argc, argv);

    ///////////////////////
    // SETUP INPUT FILES //
    ///////////////////////

    // get input TTrees
    // Reference jets
    TString refJetDirectory = opts.refJetDirectory();
    L1GenericTree<L1AnalysisL1ExtraDataFormat> refJetTree(opts.inputFilename(), 
                                                          refJetDirectory+"/L1ExtraTree", 
                                                          "L1Extra");
    L1AnalysisL1ExtraDataFormat * refData = refJetTree.getData();

    // L1 jets
    TString l1JetDirectory = opts.l1JetDirectory();
    L1GenericTree<L1AnalysisL1UpgradeDataFormat> l1JetTree(opts.inputFilename(), 
                                                           l1JetDirectory+"/L1UpgradeTree", 
                                                           "L1Upgrade");
    L1AnalysisL1UpgradeDataFormat * l1Data = l1JetTree.getData();

    // TTree that holds PileupInfo
    PileupInfoTree puInfoTree(opts.inputFilename());

    // hold Event tree
    L1GenericTree<L1AnalysisEventDataFormat> eventTree(opts.inputFilename(),
                                                         "l1EventTree/L1EventTree",
                                                         "Event");
    L1AnalysisEventDataFormat * eventData = eventTree.getData();

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
    fs::path outPath(opts.outputFilename());
    TString outDir(outPath.parent_path().c_str());
    if (outDir != "") {
        outDir += "/";
    }

    // setup output tree to store raw variable for quick plotting/debugging
    TTree outTree("valid", "valid");

    // Quantities for L1 jets:
    float out_pt(-1.), out_eta(99.), out_phi(99.);
    int out_nL1(-1); // number of jets in the event,
    int out_ind(-1); // index of this jet in the collection (ordered by descending pT)
    outTree.Branch("pt", &out_pt, "pt/Float_t");
    outTree.Branch("eta", &out_eta, "eta/Float_t");
    outTree.Branch("phi", &out_phi, "phi/Float_t");
    outTree.Branch("nL1", &out_nL1, "nL1/Int_t");
    outTree.Branch("indL1", &out_ind, "indL1/Int_t");
    // Quantities for reference jets (GenJet, etc):
    float out_ptRef(-1.), out_etaRef(99.), out_phiRef(99.);
    int out_nRef(-1), out_indRef;
    outTree.Branch("ptRef", &out_ptRef, "ptRef/Float_t");
    outTree.Branch("etaRef", &out_etaRef, "etaRef/Float_t");
    outTree.Branch("phiRef", &out_phiRef, "phiRef/Float_t");
    outTree.Branch("nRef", &out_nRef, "nRef/Int_t");
    outTree.Branch("inRef", &out_indRef, "indRef/Int_t");
    // Quantities to describe relationship between the two:
    float out_rsp(-1.);
    float out_dr(99.), out_deta(99.), out_dphi(99.);
    float out_ptDiff(99999.), out_resL1(99.), out_resRef(99.);
    int out_nMatches(0);
    outTree.Branch("ptDiff", &out_ptDiff, "ptDiff/Float_t"); // L1 - Ref
    outTree.Branch("rsp", &out_rsp, "rsp/Float_t"); // response = l1 pT/ ref jet pT
    outTree.Branch("dr", &out_dr, "dr/Float_t");
    outTree.Branch("deta", &out_deta, "deta/Float_t");
    outTree.Branch("dphi", &out_dphi, "dphi/Float_t");
    outTree.Branch("resL1", &out_resL1, "resL1/Float_t"); // resolution = L1 - Ref / L1
    outTree.Branch("resRef", &out_resRef, "resRef/Float_t"); // resolution = L1 - Ref / Ref
    outTree.Branch("nMatches", &out_nMatches, "nMatches/Int_t");
    // PU quantities
    float out_trueNumInteractions(-1.), out_numPUVertices(-1.);
    outTree.Branch("trueNumInteractions", &out_trueNumInteractions, "trueNumInteractions/Float_t");
    outTree.Branch("numPUVertices", &out_numPUVertices, "numPUVertices/Float_t");
    // Event number
    int out_event(0);
    outTree.Branch("event", &out_event, "event/Int_t");

    // L1 sums
    int out_nL1JetsSum(0);
    float out_httL1(0.);
    outTree.Branch("nL1JetsSum", &out_nL1JetsSum);
    outTree.Branch("httL1", &out_httL1);

    // GenJet Sums
    int out_nRefJetsSum(0);
    float out_httRef(0.);
    outTree.Branch("nRefJetsSum", &out_nRefJetsSum);
    outTree.Branch("httRef", &out_httRef);

    // check # events in boths trees is same
    Long64_t nEntriesRef = refJetTree.getEntries();
    Long64_t nEntriesL1  = l1JetTree.getEntries();
    Long64_t nEntries(0);
    if (nEntriesRef != nEntriesL1) {
        throw std::range_error("Different number of events in L1 & ref trees");
    } else {
        nEntries = (opts.nEvents() > 0) ? opts.nEvents() : nEntriesL1;
        cout << "Running over " << nEntries << " events." << endl;
    }

    ///////////////////////
    // SETUP JET MATCHER //
    ///////////////////////
    double maxDeltaR(opts.deltaR()), minRefJetPt(opts.refJetMinPt()), maxRefJetPt(5000.);
    double minL1JetPt(0.1), maxL1JetPt(5000.), maxJetEta(5);
    // use base class smart pointer for ease of swapping in/out different
    //  matchers if so desired
    std::unique_ptr<Matcher> matcher(new DeltaR_Matcher(maxDeltaR, minRefJetPt, maxRefJetPt, minL1JetPt, maxL1JetPt, maxJetEta));
    std::cout << *matcher << std::endl;

    ////////////////
    // SETUP LUTS //
    ////////////////
    // to convert pt,eta to index (compressed)
    // std::map<int, int> pt_lut = load_lut("/users/ra12451/L1JEC/CMSSW_7_6_0_pre7/src/L1Trigger/L1JetEnergyCorrections/Stage2_QCDFlatSpring15BX25HCALFix_26Nov_76X_mcRun2_asymptotic_v5_jetSeed1p5_noJec_v2/output/stage2_lut_pu15to25/stage2_lut_pu15to25_pt.txt");
    std::map<int, int> pt_lut;
    // to map index : hw correction factor
    // std::map<int, int> corr_lut = load_lut("/users/ra12451/L1JEC/CMSSW_7_6_0_pre7/src/L1Trigger/L1JetEnergyCorrections/Stage2_QCDFlatSpring15BX25HCALFix_26Nov_76X_mcRun2_asymptotic_v5_jetSeed1p5_noJec_v2/output/stage2_lut_pu15to25/stage2_lut_pu15to25_corr.txt");
    std::map<int, int> corr_lut;
    if (opts.correctionFilename() != "") {
        pt_lut = load_lut("stage2_lut_pu15to25_pt.txt");
        corr_lut = load_lut("stage2_lut_pu15to25_corr.txt");
    }
    //////////////////////
    // LOOP OVER EVENTS //
    //////////////////////
    // produce matching pairs and store
    Long64_t drawCounter = 0;
    for (Long64_t iEntry = 0; iEntry < nEntries; ++iEntry) {
        if (iEntry % 10000 == 0) {
            cout << "Entry: " << iEntry << " at " << getCurrentTime() << endl;
        }

        if (refJetTree.getEntry(iEntry) < 1 ||
            l1JetTree.getEntry(iEntry) < 1 ||
            eventTree.getEntry(iEntry) < 1)
            break;

        // event number
        out_event = eventData->event;

        // get pileup quantities
        // note these get stored once per pair of matched jets NOT once per event
        puInfoTree.GetEntry(iEntry);
        out_trueNumInteractions = puInfoTree.trueNumInteractions();
        out_numPUVertices = puInfoTree.numPUVertices();

        // Get vectors of ref & L1 jets from trees
        std::vector<TLorentzVector> refJets = makeTLorentzVectors(refData->cenJetEt, refData->cenJetEta, refData->cenJetPhi);
        std::vector<TLorentzVector> l1Jets = makeTLorentzVectors(l1Data->jetEt, l1Data->jetEta, l1Data->jetPhi);

        out_nL1 = l1Jets.size();
        out_nRef = refJets.size();

        if (out_nL1 == 0 || out_nRef == 0) continue;

        // Store sums
        std::vector<TLorentzVector> httL1Jets = getJetsForHTT(l1Jets);
        out_nL1JetsSum = httL1Jets.size();
        out_httL1 = l1Data->sumEt[2];
        float httL1_check = scalarSumPt(httL1Jets);

        if (fabs(out_httL1 - httL1_check) > 0.01 && out_httL1 < 2047.5) {
            cout << "HTT L1 not agreeing with calculation: " + lexical_cast<std::string>(out_httL1) + " vs " + lexical_cast<std::string>(httL1_check) << endl;
            for (const auto& itr: l1Jets) {
                cout << itr.Pt() << " " << itr.Eta() << endl;
            }
        }

        std::vector<TLorentzVector> httRefJets = getJetsForHTT(refJets);
        out_nRefJetsSum = httRefJets.size();
        out_httRef = scalarSumPt(httRefJets);
        // Pass jets to matcher, do matching
        matcher->setRefJets(refJets);
        matcher->setL1Jets(l1Jets);
        std::vector<MatchedPair> matchResults = matcher->getMatchingPairs();
        // matcher->printMatches(); // for debugging

        // store L1 & ref jet variables in tree
        out_nMatches = matchResults.size();
        for (const auto &it: matchResults) {
            // std::cout << it << std::endl;
            if (opts.correctionFilename() != "") {
                out_pt = getCorrectedEt(pt_lut, corr_lut, it.l1Jet().Et(), it.l1Jet().Eta());
            } else {
                out_pt = it.l1Jet().Et();
            }
            // cout << it.l1Jet().Et() << " -> " << out_pt << " eta: " << it.l1Jet().Eta() << " ieta: " << getAbsIEta(it.l1Jet().Eta()) << endl;
            out_eta = it.l1Jet().Eta();
            out_phi = it.l1Jet().Phi();
            out_dr = it.refJet().DeltaR(it.l1Jet());
            out_deta = it.refJet().Eta() - it.l1Jet().Eta();
            out_dphi = it.refJet().DeltaPhi(it.l1Jet());
            out_ptRef = it.refJet().Pt();
            out_etaRef = it.refJet().Eta();
            out_phiRef = it.refJet().Phi();
            out_ptDiff = out_pt - out_ptRef;
            out_rsp = out_pt/out_ptRef;
            out_rsp_inv =  1./out_rsp;
            out_resL1 = out_ptDiff/out_pt;
            out_resRef = out_ptDiff/out_ptRef;
            outTree.Fill();
        }

        // debugging plot - plots eta vs phi of jets
        if (drawCounter < opts.drawNumber()) {
            if (matchResults.size() > 0) {
                TString label = TString::Format(
                    "%.1f < E^{gen}_{T} < %.1f GeV, " \
                    "L1 jet %.1f < E^{L1}_{T} < %.1f GeV, |#eta_{jet}| < %.1f",
                    minRefJetPt, maxRefJetPt, minL1JetPt, maxL1JetPt, maxJetEta);
                // get jets post pT, eta cuts
                JetDrawer drawer(matcher->getRefJets(), matcher->getL1Jets(), matchResults, label);

                TString pdfname = TString::Format("%splots_%s_%s_%s/jets_%lld.pdf",
                    outDir.Data(), inStem.Data(), "gen", "l1", iEntry);
                drawer.drawAndSave(pdfname);

                drawCounter++;
            }
        }
    } // end of loop over entries

    // save tree to new file and cleanup
    outTree.Write("", TObject::kOverwrite);
    outFile->Close();
    return 0;
}


/**
 * @brief Load a LUT from file into map.
 * @details Ignores any lines starting with a #.
 *
 * @param filename filename of LUT
 * @return std::map<int, int> with LUT contents.
 */
std::map<int, int> load_lut(std::string filename) {
    cout << "Loading LUT " << filename << endl;
    std::map<int, int> lut;
    std::ifstream infile(filename);
    std::string line = "";
    while (std::getline(infile, line)) {
        if (boost::starts_with(line, "#")) {
            continue;
        }
        std::vector<std::string> parts;
        boost::split(parts, line, boost::is_any_of(" "), boost::token_compress_on);
        int key = lexical_cast<int>(parts[0]);
        int value = lexical_cast<int>(parts[1]);
        lut.insert(std::make_pair(key, value));
    }
    return lut;
}

/**
 * @brief Convert physical eta to ieta using the absolute value of eta.
 *
 * @param eta Physical eta
 * @return HW Eta
 */
int getAbsIEta(float eta) {
    std::vector<float> eta_bins = {0.0, 0.348, 0.695, 1.044, 1.392, 1.74, 2.172, 3.0, 3.5, 4.0, 4.5, 5};
    float absEta = fabs(eta);
    for (unsigned i = 0; i < eta_bins.size()-1; i++) {
        if ((eta_bins[i] < absEta) && (absEta < eta_bins[i+1])) {
            return i;
        }
    }
    return eta_bins.size();
}

/**
 * @brief Convert iet, ieta into an address
 * @details [long description]
 *
 * @param iet HW et
 * @param ieta HW eta
 *
 * @return Address
 */
int getAddress(int iet, int ieta) {
    return (iet<<4) + ieta;
}


float getCorrectedEt(std::map<int, int> & pt_lut, std::map<int, int> & corr_lut,
                     float et, float eta) {
    unsigned int iet = (unsigned int) et * 2;
    unsigned int ieta = abs(getAbsIEta(eta));
    int address = getAddress(iet, ieta);
    int index = pt_lut[address];
    int corr_factor = corr_lut[index];
    int corrected_iet = (corr_factor*iet)>>7;
    corrected_iet += iet;
    return corrected_iet * 0.5;
}


/**
 * @brief Convert iPhi to phi as workaround for bug in ntuples
 * @details l1UpgradeEMuTree/jetPhi not correct - use iPhi + this fn instead,
 *
 * @param iphi HW phi
 * @return Physical phi (in radians)
 */
const float towerSizeDegrees = 5.;
float iPhiToPhi(int iphi) {
    if (iphi > 72)
        throw std::range_error("iPhi > 72");
    if (iphi < 1)
        throw std::range_error("iPhi < 1");
    float eta = (iphi * towerSizeDegrees) - (0.5 * towerSizeDegrees);
    if (iphi > 36)
        eta -= 360.;
    return eta * TMath::Pi() / 180.;
}


/**
 * @brief Create vector of objects that go into calcualting HTT
 * @details [long description]
 *
 * @param jets [description]
 * @return [description]
 */
std::vector<TLorentzVector> getJetsForHTT(std::vector<TLorentzVector> jets) {
    std::vector<TLorentzVector> outputJets;
    for (const auto& itr: jets) {
        if (passHTTCut(itr))
            outputJets.push_back(itr);
    }
    return outputJets;
}


/**
 * @brief Cut for jets to go into HTT calculation
 * @details [long description]
 *
 * @param jet [description]
 * @return [description]
 */
bool passHTTCut(TLorentzVector jet) {
    return (jet.Pt() > 30.01 && fabs(jet.Eta()) <= 3);
}


/**
 * @brief Scalar sum TLorentzVector pTs
 *
 * @param jets [description]
 * @return [description]
 */
float scalarSumPt(std::vector<TLorentzVector> jets) {
    float sum = 0.;
    for (const auto& itr: jets) {
        sum += itr.Pt();
    }
    return sum;
}