// STL headers
#include <iostream>
#include <vector>
#include <utility>
#include <stdexcept>
#include <algorithm>

// ROOT headers
#include "TChain.h"
#include "TFile.h"
#include "TTree.h"
#include "TROOT.h"
#include "TSystem.h"
#include "TLorentzVector.h"
#include "TRegexp.h"
#include "TString.h"

// BOOST headers
#include <boost/filesystem.hpp>
// #include <boost/algorithm/string.hpp>

// Headers from L1TNtuples
#include "L1Trigger/L1TNtuples/interface/L1AnalysisL1ExtraDataFormat.h"
#include "L1Trigger/L1TNtuples/interface/L1AnalysisL1UpgradeDataFormat.h"

// Headers from this package
#include "DeltaR_Matcher.h"
#include "commonRootUtils.h"
#include "L1GenericTree.h"
#include "PileupInfoTree.h"
#include "RunMatcherOpts.h"
#include "JetDrawer.h"

using std::cout;
using std::endl;
using L1Analysis::L1AnalysisL1ExtraDataFormat;
using L1Analysis::L1AnalysisL1UpgradeDataFormat;

namespace fs = boost::filesystem;

// forward declare fns, implementations after main()
TString getSuffixFromDirectory(const TString& dir);
std::vector<TLorentzVector> makeTLorentzVectors(std::vector<double> et,
                                                std::vector<double> eta,
                                                std::vector<double> phi);
std::vector<TLorentzVector> makeTLorentzVectors(std::vector<double> et,
                                                std::vector<double> eta,
                                                std::vector<double> phi,
                                                std::vector<int> bx);


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
    outTree.Branch("pt",     &out_pt,     "pt/Float_t");
    outTree.Branch("eta",    &out_eta,    "eta/Float_t");
    outTree.Branch("phi",    &out_phi,    "phi/Float_t");
    // Quantities for reference jets (GenJet, etc):
    float out_ptRef(-1.), out_etaRef(99.), out_phiRef(99.);
    outTree.Branch("ptRef",  &out_ptRef, "ptRef/Float_t");
    outTree.Branch("etaRef", &out_etaRef, "etaRef/Float_t");
    outTree.Branch("phiRef", &out_phiRef, "phiRef/Float_t");
    // Quantities to describe relationship between the two:
    float out_rsp(-1.), out_rsp_inv(-1.);
    float out_dr(99.), out_deta(99.), out_dphi(99.);
    float out_ptDiff(99999.), out_resL1(99.), out_resRef(99.);
    outTree.Branch("ptDiff", &out_ptDiff, "ptDiff/Float_t"); // L1 - Ref
    outTree.Branch("rsp",    &out_rsp,    "rsp/Float_t"); // response = l1 pT/ ref jet pT
    outTree.Branch("rsp_inv",   &out_rsp_inv,   "rsp_inv/Float_t"); // response = ref pT/ l1 jet pT
    outTree.Branch("dr",     &out_dr,     "dr/Float_t");
    outTree.Branch("deta",   &out_deta,   "deta/Float_t");
    outTree.Branch("dphi",   &out_dphi,   "dphi/Float_t");
    outTree.Branch("resL1", &out_resL1, "resL1/Float_t"); // resolution = L1 - Ref / L1
    outTree.Branch("resRef", &out_resRef, "resRef/Float_t"); // resolution = L1 - Ref / Ref
    // PU quantities
    float out_trueNumInteractions(-1.), out_numPUVertices(-1.);
    outTree.Branch("trueNumInteractions", &out_trueNumInteractions, "trueNumInteractions/Float_t");
    outTree.Branch("numPUVertices", &out_numPUVertices, "numPUVertices/Float_t");
    // Event number
    // int out_event(0);
    // outTree.Branch("event", &out_event, "event/Int_t");

    // check # events in boths trees is same
    Long64_t nEntriesRef = refJetTree.getEntries();
    Long64_t nEntriesL1  = l1JetTree.getEntries();
    Long64_t nEntries(0);
    if (nEntriesRef != nEntriesL1) {
        throw range_error("Different number of events in L1 & ref trees");
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

    //////////////////////
    // LOOP OVER EVENTS //
    //////////////////////
    // produce matching pairs and store
    Long64_t drawCounter = 0;
    for (Long64_t iEntry = 0; iEntry < nEntries; ++iEntry) {
        if (iEntry % 10000 == 0) {
            cout << "Entry: " << iEntry << endl;
        }
        if (refJetTree.getEntry(iEntry) < 1 || l1JetTree.getEntry(iEntry) < 1) break;

        // get pileup quantities
        // note these get stored once per pair of matched jets NOT once per event
        puInfoTree.GetEntry(iEntry);
        out_trueNumInteractions = puInfoTree.trueNumInteractions();
        out_numPUVertices = puInfoTree.numPUVertices();

        // Get vectors of ref & L1 jets from trees
        std::vector<TLorentzVector> refJets = makeTLorentzVectors(refData->cenJetEt, refData->cenJetEta, refData->cenJetPhi);
        std::vector<TLorentzVector> l1Jets = makeTLorentzVectors(l1Data->jetEt, l1Data->jetEta, l1Data->jetPhi);

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
 * @brief Make a std::vector of TLorentzVectors out of input vectors of et, eta, phi.
 *
 * @param et [description]
 * @param eta [description]
 * @param phi [description]
 * @return [description]
 */
std::vector<TLorentzVector> makeTLorentzVectors(std::vector<double> et,
                                                std::vector<double> eta,
                                                std::vector<double> phi) {
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
 * Also includes requirement that BX = 0.
 *
 * @param et [description]
 * @param eta [description]
 * @param phi [description]
 * @param bx [description]
 * @return [description]
 */
std::vector<TLorentzVector> makeTLorentzVectors(std::vector<double> et,
                                                std::vector<double> eta,
                                                std::vector<double> phi,
                                                std::vector<int> bx) {
    // check all same size
    if (et.size() != eta.size() || et.size() != phi.size()) {
        throw range_error("Eta/eta/phi vectors different sizes, cannot make TLorentzVectors");
    }
    std::vector<TLorentzVector> vecs;
    for (unsigned i = 0; i < et.size(); i++) {
        if (bx.at(i) == 0) {
            TLorentzVector v;
            v.SetPtEtaPhiM(et.at(i), eta.at(i), phi.at(i), 0);
            vecs.push_back(v);
        }
    }
    return vecs;
}
