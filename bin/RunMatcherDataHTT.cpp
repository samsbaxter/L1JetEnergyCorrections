#include <fstream>

// ROOT headers
#include "TChain.h"
#include "TFile.h"
#include "TTree.h"
#include "TROOT.h"
#include "TSystem.h"

// BOOST headers
#include <boost/filesystem.hpp>
#include <boost/lexical_cast.hpp>
#include <boost/algorithm/string.hpp>
#include <boost/algorithm/string/predicate.hpp>

// Headers from L1TNtuples
#include "L1Trigger/L1TNtuples/interface/L1AnalysisEventDataFormat.h"
#include "L1Trigger/L1TNtuples/interface/L1AnalysisRecoJetDataFormat.h"
#include "L1Trigger/L1TNtuples/interface/L1AnalysisRecoMetDataFormat.h"
#include "L1Trigger/L1TNtuples/interface/L1AnalysisL1UpgradeDataFormat.h"
#include "L1Trigger/L1TNtuples/interface/L1AnalysisL1ExtraDataFormat.h"
#include "L1Trigger/L1TNtuples/interface/L1AnalysisRecoMetFilterDataFormat.h"

// Headers from this package
#include "DeltaR_Matcher.h"
#include "commonRootUtils.h"
#include "RunMatcherOpts.h"
#include "JetDrawer.h"
#include "L1GenericTree.h"
#include "runMatcherUtils.h"

using std::cout;
using std::endl;
using L1Analysis::L1AnalysisEventDataFormat;
using L1Analysis::L1AnalysisRecoMetDataFormat;
using L1Analysis::L1AnalysisL1UpgradeDataFormat;
using L1Analysis::L1AnalysisL1ExtraDataFormat;
using L1Analysis::L1AnalysisRecoMetFilterDataFormat;
using boost::lexical_cast;
namespace fs = boost::filesystem;

// forward declare fns, implementations after main()
std::vector<TLorentzVector> makeRecoTLorentzVectorsCleaned(const L1AnalysisRecoMetDataFormat & jets, std::string quality);


/**
 * @brief
 * This version is for running on data, when you want to take L1 jets from the
 * L1Upgrade collection, and reference jets from the RecoTree.
 *
 * @author Robin Aggleton, Nov 2015
 */
int main(int argc, char* argv[]) {

    cout << "Running Matcher for data HTT studies" << std::endl;

    // deal with user args
    RunMatcherOpts opts(argc, argv);

    ///////////////////////
    // SETUP INPUT FILES //
    ///////////////////////
    // get input TTrees
    // Reco jets
    TString refJetDirectory = opts.refJetDirectory();
    L1GenericTree<L1AnalysisRecoMetDataFormat> refJetTree(opts.inputFilename(),
                                                          refJetDirectory+"/JetRecoTree",
                                                          "Sums");
    L1AnalysisRecoMetDataFormat * refData = refJetTree.getData();

    // L1 jets
    TString l1JetDirectory = opts.l1JetDirectory();
    L1GenericTree<L1AnalysisL1UpgradeDataFormat> l1JetTree(opts.inputFilename(),
                                                           l1JetDirectory+"/L1UpgradeTree",
                                                           "L1Upgrade");
    L1AnalysisL1UpgradeDataFormat * l1Data = l1JetTree.getData();

    // hold Event tree
    L1GenericTree<L1AnalysisEventDataFormat> eventTree(opts.inputFilename(),
                                                       "l1EventTree/L1EventTree",
                                                       "Event");
    L1AnalysisEventDataFormat * eventData = eventTree.getData();

    // hold met filter info
    L1GenericTree<L1AnalysisRecoMetFilterDataFormat> metFilterTree(opts.inputFilename(),
                                                                   "l1MetFilterRecoTree/MetFilterRecoTree",
                                                                   "MetFilters");
    L1AnalysisRecoMetFilterDataFormat * metFilterData = metFilterTree.getData();


    // Get L1 HTT jets
    TFile * f = TFile::Open(opts.inputFilename().c_str());
    TTree * httTree = (TTree*) f->Get("simCaloStage2Digis/Layer2SumTree");
    if (!httTree) throw std::runtime_error("NO TREE");
    std::vector<float> * httJetEt = new std::vector<float>;
    std::vector<float> * httJetEta = new std::vector<float>;
    std::vector<float> * httJetPhi = new std::vector<float>;  // must be pointer not object
    httTree->SetBranchAddress("httJetEt", &httJetEt);
    httTree->SetBranchAddress("httJetEta", &httJetEta);
    httTree->SetBranchAddress("httJetPhi", &httJetPhi);

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
    if (outDir != "") outDir += "/";

    // setup output tree to store raw variable for quick plotting/debugging
    TTree outTree("valid", "valid");
    // Quantities for L1 jets:
    float out_pt(-1.), out_eta(99.), out_phi(99.);
    int out_nL1(-1); // number of jets in the event,
    outTree.Branch("pt", &out_pt, "pt/F");
    outTree.Branch("eta", &out_eta, "eta/F");
    outTree.Branch("phi", &out_phi, "phi/F");
    outTree.Branch("nL1", &out_nL1, "nL1/I");
    // Quantities for reference jets (GenJet, etc):
    float out_ptRef(-1.), out_etaRef(99.), out_phiRef(99.);
    int out_nRef(-1);
    outTree.Branch("ptRef", &out_ptRef, "ptRef/F");
    outTree.Branch("etaRef", &out_etaRef, "etaRef/F");
    outTree.Branch("phiRef", &out_phiRef, "phiRef/F");
    outTree.Branch("nRef", &out_nRef, "nRef/I");
    // Quantities to describe relationship between the two:
    float out_rsp(-1.), out_rsp_inv(-1.);
    float out_dr(99.), out_deta(99.), out_dphi(99.);
    float out_ptDiff(99999.), out_resL1(99.), out_resRef(99.);
    outTree.Branch("ptDiff", &out_ptDiff, "ptDiff/F"); // L1 - Ref
    outTree.Branch("rsp", &out_rsp, "rsp/F"); // response = l1 pT/ ref jet pT
    outTree.Branch("rsp_inv", &out_rsp_inv, "rsp_inv/F"); // response = ref pT/ l1 jet pT
    outTree.Branch("dr", &out_dr, "dr/F");
    outTree.Branch("deta", &out_deta, "deta/F");
    outTree.Branch("dphi", &out_dphi, "dphi/F");
    outTree.Branch("resL1", &out_resL1, "resL1/F"); // resolution = L1 - Ref / L1
    outTree.Branch("resRef", &out_resRef, "resRef/F"); // resolution = L1 - Ref / Ref

    // Energy sums
    float httL1(0.), httRef(0.);
    outTree.Branch("httL1", &httL1, "httL1/F");
    outTree.Branch("httRef", &httRef, "httRef/F");

    // PU quantities
    float out_trueNumInteractions(-1.), out_numPUVertices(-1.);
    outTree.Branch("trueNumInteractions", &out_trueNumInteractions, "trueNumInteractions/F");
    outTree.Branch("numPUVertices", &out_numPUVertices, "numPUVertices/F");

    // Event info
    ULong64_t out_event(0);
    int out_ls(0);
    outTree.Branch("event", &out_event, "event/l");
    outTree.Branch("LS", &out_ls, "ls/I");

    // MET filters
    bool out_passCSC(true);
    bool out_HBHENoise(true), out_HBHEIsoNoise(true);
    outTree.Branch("passCSC", &out_passCSC, "passCSC/Bool_t");
    outTree.Branch("HBHENoise", &out_HBHENoise, "HBHENoise/Bool_t");
    outTree.Branch("HBHEIsoNoise", &out_HBHEIsoNoise, "HBHEIsoNoise/Bool_t");

    Long64_t nEntriesRef = refJetTree.getEntries();
    Long64_t nEntriesL1  = httTree->GetEntries();
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
    std::unique_ptr<Matcher> matcher(new DeltaR_Matcher(maxDeltaR, minRefJetPt, maxRefJetPt, minL1JetPt, maxL1JetPt, maxJetEta));
    std::cout << *matcher << std::endl;

    ///////////////////////
    // JET CLEANING CUTS //
    ///////////////////////
    bool doCleaningCuts = opts.cleanJets();
    std::string jetId = "MUMULT0";
    // std::string jetId = "TIGHTLEPVETO";
    if (doCleaningCuts) {
        cout << "Applying " << jetId << " jet cleaning cuts" << endl;
    }

    //////////////////////
    // LOOP OVER EVENTS //
    //////////////////////
    // produce matching pairs and store
    Long64_t matchedEvent(0), cscFail(0), counter(0);
    Long64_t noL1Jets(0), noRefJets(0), noJets(0), noMatches(0), bothJets(0);
    for (Long64_t iEntry = 0; counter < nEntries; ++iEntry, ++counter) {

        if (counter % 10000 == 0) {
            cout << "Entry: " << iEntry << " at " << getCurrentTime() << endl;
        }

        // Make sure to add any other Trees here!
        if (refJetTree.getEntry(iEntry) < 1 || eventTree.getEntry(iEntry) < 1 ||
            metFilterTree.getEntry(iEntry) < 1 || l1JetTree.getEntry(iEntry) < 1 ||
            httTree->GetEntry(iEntry) < 1)
            break;

        // event info
        out_event = eventData->event;
        out_ls = (Long64_t) eventData->lumi;

        // MET filter info
        out_passCSC = metFilterData->cscTightHalo2015Filter;
        if (!out_passCSC) cscFail++;
        out_HBHENoise = metFilterData->hbheNoiseFilter;
        out_HBHEIsoNoise = metFilterData->hbheNoiseIsoFilter;

        if (doCleaningCuts && !(out_passCSC && out_HBHENoise && out_HBHEIsoNoise)) {
            continue;
        }

        // Get sums
        httL1 = l1Data->sumEt[2];
        httRef = refData->Ht;

        // Get vectors of ref & L1 jets from trees, only want BX = 0 (the collision)
        std::vector<TLorentzVector> refJets;
        if (doCleaningCuts) {
            refJets = makeRecoTLorentzVectorsCleaned(*refData, jetId); // with JetID filters
        } else {
            refJets = makeTLorentzVectors(refData->httJetEt, refData->httJetEta, refData->httJetPhi);
        }
        std::vector<TLorentzVector> l1Jets  = makeTLorentzVectors(*httJetEt, *httJetEta, *httJetPhi);

        out_nL1 = l1Jets.size();
        out_nRef = refJets.size();

        if (out_nL1 == 0 && out_nRef > 0) noL1Jets++;
        if (out_nRef == 0 && out_nL1 > 0) noRefJets++;
        if (out_nL1 == 0 && out_nRef == 0) noJets++;
        if (out_nL1 > 0 && out_nRef > 0) bothJets++;

        // Pass jets to matcher, do matching
        matcher->setRefJets(refJets);
        matcher->setL1Jets(l1Jets);
        std::vector<MatchedPair> matchResults = matcher->getMatchingPairs();

        if (matchResults.size()>0) matchedEvent++;
        if (out_nL1>0 && out_nRef>0 && matchResults.size() == 0) noMatches++;

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

    }

    // save tree to new file and cleanup
    outTree.Write("", TObject::kOverwrite);
    outFile->Close();
    f->Close();
    cout << matchedEvent << " events had 1+ matches, out of " << nEntries << endl;
    cout << noMatches << " events had 0 matches (with 1+ L1 and 1+ Ref jets)" << endl;
    cout << noL1Jets << " events had 0 L1 jets (>0 ref) to start with" << endl;
    cout << noRefJets << " events had 0 Ref jets (>0 L1) to start with" << endl;
    cout << noJets << " events had 0 jets of either to start with" << endl;
    cout << bothJets << " events had 1+ L1 and 1+ Ref jets" << endl;
    cout << cscFail << " events failed CSC check, out of " << nEntries << endl;
    return 0;
}


/**
 * @brief Make a std::vector of TLorentzVectors out of input vectors of et, eta, phi.
 * Also applies JetID cuts.
 *
 * @param jets [description]
 * @param quality Can be LOOSE, TIGHT or TIGHTLEPVETO
 *
 * @return [description]
 */
std::vector<TLorentzVector> makeRecoTLorentzVectorsCleaned(const L1AnalysisRecoMetDataFormat & jets, std::string quality) {

    std::vector<TLorentzVector> vecs;

    for (int i = 0; i < jets.nJetsInHTT; ++i) {
        if (quality == "MUMULT0") {
            if (!jets.httJetMuMult0[i]) continue;
        } else if (quality == "TIGHTLEPVETO") {
            if (!jets.httJetClean[i]) continue;
        }

        // If got this far, then can add to list.
        TLorentzVector v;
        v.SetPtEtaPhiM(jets.httJetEt[i], jets.httJetEta[i], jets.httJetPhi[i], 0);
        vecs.push_back(v);
    }

    return vecs;
}
