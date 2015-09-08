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

// Headers from L1Ntuples
#include "L1TriggerDPG/L1Ntuples/interface/L1AnalysisL1ExtraDataFormat.h"
#include "L1TriggerDPG/L1Ntuples/interface/L1AnalysisEventDataFormat.h"

// Headers from this package
#include "DeltaR_Matcher.h"
#include "commonRootUtils.h"
#include "L1ExtraTree.h"
#include "PileupInfoTree.h"
#include "RunMatcherOpts.h"
#include "JetDrawer.h"
#include "SortFilterEmulator.h"

using std::cout;
using std::endl;
using L1Analysis::L1AnalysisL1ExtraDataFormat;
using L1Analysis::L1AnalysisEventDataFormat;

namespace fs = boost::filesystem;

// forward declare fns, implementations after main()
TString getSuffixFromDirectory(const TString& dir);
void loadCorrectionFunctions(const TString& filename,
                             std::vector<TF1>& corrFns,
                             const std::vector<float>& etaBins);
void correctJets(std::vector<TLorentzVector>& jets,
                 std::vector<TF1>& corrFns,
                 std::vector<float>& etaBins,
                 float minPt);
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
 * python/l1Ntuple_cfg.py. Can also optionally apply correction functions, and
 * emulate the GCT/Stage 1 by sorting & keeping top 4 cen & fwd jets.
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

    // get input L1Extra TDirectories/TTrees
    // assumes TTree named "L1ExtraTree", but can specify in ctor of L1ExtraTree
    TString refJetDirectory                 = opts.refJetDirectory();
    TString refJetSuffix                    = getSuffixFromDirectory(refJetDirectory);
    std::vector<std::string> refJetBranches = opts.refJetBranchNames();

    TString l1JetDirectory                  = opts.l1JetDirectory();
    TString l1JetSuffix                     = getSuffixFromDirectory(l1JetDirectory);
    std::vector<std::string> l1JetBranches  = opts.l1JetBranchNames();

    // also specify which branches jets are stored in
    // for genJets & gctIntern, it's just cenJet branch,
    // for gctDigis, it's cen/fwd/tau
    L1ExtraTree refJetExtraTree(opts.inputFilename(), refJetDirectory);
    L1ExtraTree l1JetExtraTree(opts.inputFilename(), l1JetDirectory);

    // std::unique_ptr<TChain> eventChain(new TChain("l1NtupleProducer/L1Tree"));
    // std::unique_ptr<L1AnalysisEventDataFormat> eventTree(new L1AnalysisEventDataFormat());
    // int addResult = eventChain->Add(opts.inputFilename().c_str(), -1);
    // if (addResult == 0) {
    //     throw runtime_error(("No L1Tree!"));
    // }
    // eventChain->SetBranchAddress("Event", &eventTree);

    // Map L1Analysis::L1AnalysisL1ExtraDataFormat structs to the desired
    // directories in the TFile.
    // std::unique_ptr<TChain> refChain(new TChain(refJetDirectory+"/L1ExtraTree"));
    // std::unique_ptr<L1AnalysisL1ExtraDataFormat> refJetTree(new L1AnalysisL1ExtraDataFormat());
    // Add file to TChain. Note netries = -1. This is potentially slower, but has
    // the advantage of actually checking that the file and tree exist, rather
    // than waiting until later (when it could be forgotten)
    // Int_t addResult = refChain->Add(opts.inputFilename().c_str(), -1);
    // if (addResult == 0) {
    //     throw runtime_error(("Couldn't open "+opts.inputFilename()+":/"+refJetDirectory).Data()) ;
    // }
    // refChain->SetBranchAddress("L1Extra", &refJetTree);

    // std::unique_ptr<TChain> l1Chain(new TChain(l1JetDirectory+"/L1ExtraTree"));
    // std::unique_ptr<L1AnalysisL1ExtraDataFormat> l1JetTree(new L1AnalysisL1ExtraDataFormat());
    // addResult = l1Chain->Add(opts.inputFilename().c_str(), -1);
    // if (addResult == 0) {
    //     throw runtime_error(("Couldn't open "+opts.inputFilename()+":/"+l1JetDirectory).Data()) ;
    // }
    // l1Chain->SetBranchAddress("L1Extra", &l1JetTree);

    // Long64_t nentries = refChain->GetEntries();
    // cout << nentries << endl;
    // nentries = 100;
    // for (Long64_t jentry=0; jentry < nentries; jentry++) {
    //     Long64_t ientry = refChain->LoadTree(jentry);
    //     Long64_t ientry2 = l1Chain->LoadTree(jentry);
    //     if (ientry < 0 || ientry2 < 0) break;
    //     refChain->GetEntry(jentry);
    //     l1Chain->GetEntry(jentry);
    //     cout << refJetTree->nCenJets << endl;
    //     cout << l1JetTree->nCenJets << endl;
    // }

    // TTree that holds PileupInfo
    PileupInfoTree puInfoTree(opts.inputFilename());

    // input filename stem (no .root)
    fs::path inPath(opts.inputFilename());
    TString inStem(inPath.stem().c_str());

    //////////////////////////////////////////////////////////////
    // GET CORRECTION FUNCTIONS, SETUP SORT & FILTER (optional) //
    //////////////////////////////////////////////////////////////
    // N.B do this *before* opening output file below.
    // Otherwise, you'll have to add in a outFile->cd() to save ttree to file.
    bool doCorrections = false;
    std::vector<float> etaBins = {0.0, 0.348, 0.695, 1.044, 1.392, 1.74, 2.172, 3.0, 3.5, 4.0, 4.5, 5.001};
    std::vector<TF1> correctionFunctions;
    unsigned nTop = 4;
    std::unique_ptr<SortFilterEmulator> emu(new SortFilterEmulator(nTop));
    if (opts.correctionFilename() != "") {
        doCorrections = true;
        loadCorrectionFunctions(opts.correctionFilename(), correctionFunctions, etaBins);
    }

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
    Long64_t nEntriesRef = refJetExtraTree.fChain->GetEntriesFast();
    Long64_t nEntriesL1  = l1JetExtraTree.fChain->GetEntriesFast();
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
    double maxDeltaR(opts.deltaR()), minRefJetPt(opts.refJetMinPt()), maxRefJetPt(1000.);
    double minL1JetPt(0.), maxL1JetPt(500.), maxJetEta(5);
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

        // jentry is the entry # in the current Tree
        Long64_t jentry = refJetExtraTree.LoadTree(iEntry);
        Long64_t jentry2 = l1JetExtraTree.LoadTree(iEntry);
        // Long64_t jentry3 = eventChain->LoadTree(iEntry);
        if (jentry < 0) break;
        if (jentry2 < 0) break;
        if (iEntry % 10000 == 0) {
            cout << "Entry: " << iEntry << endl;
        }
        refJetExtraTree.GetEntry(iEntry);
        l1JetExtraTree.GetEntry(iEntry);

        // store event info
        // eventChain->GetEntry(iEntry);
        // out_event = eventTree->event;

        // get pileup quantities
        // note these get stored once per pair of matched jets NOT once per event
        puInfoTree.GetEntry(iEntry);
        out_trueNumInteractions = puInfoTree.trueNumInteractions();
        out_numPUVertices = puInfoTree.numPUVertices();

        // Get vectors of ref & L1 jets from trees
        std::vector<TLorentzVector> refJets = refJetExtraTree.makeTLorentzVectors(refJetBranches);
        std::vector<TLorentzVector> l1Jets  = l1JetExtraTree.makeTLorentzVectors(l1JetBranches);

        // If doing corrections, split into cen & fwd jets, sort & filter
        // - do it here before matching
        if (doCorrections) {
            correctJets(l1Jets, correctionFunctions, etaBins, opts.correctionMinPt());
            emu->setJets(l1Jets);
            l1Jets = emu->getAllJets();
        }

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

    }

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
 * @brief Get correction functions from file, and load into vector.
 * @details Note that correction functions have names
 * "fitfcneta_<etaMin>_<etaMax>", where etaMin/Max denote eta bin limits.
 *
 * @param filename  Name of file with correction functions.
 * @param corrFns   Vector of TF1s in which functions are stored.
 */
void loadCorrectionFunctions(const TString& filename,
                             std::vector<TF1>& corrFns,
                             const std::vector<float>& etaBins) {

    TFile * corrFile = openFile(filename, "READ");

    // Loop over eta bins
    for (unsigned ind = 0; ind < etaBins.size()-1; ++ind) {
        float etaMin(etaBins[ind]), etaMax(etaBins[ind+1]);
        TString binName = TString::Format("fitfcneta_%g_%g", etaMin, etaMax);
        TF1 * fit = dynamic_cast<TF1*>(corrFile->Get(binName));
        // Make a copy of function and store in vector
        if (fit) {
            TF1 fitFcn(*fit);
            corrFns.push_back(fitFcn);
        } else {
            // throw invalid_argument(binName.Prepend("No TF1 with name ").Data());
            // load in flat function if no suitable one is in file
            TF1 fitFcn(binName, "1");
            corrFns.push_back(fitFcn);
            cout << "No correction fn found for eta bin ";
            cout << etaMin << " - " << etaMax << endl;
            cout << ": Will not correct jets in this bin" << endl;
        }
    }
    corrFile->Close();
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



/**
 * @brief Apply correction function to collection of jets
 * @details [long description]
 *
 * @param corrFn   Vector of TF1 to be applied, corresponding to eta bins
 * @param etaBins  Eta bin limits
 * @param minPt    Minimum jet pT for correction to be applied. If unspecified,
 * it only applies corrections for jets within the fit range of the function.
 */
void correctJets(std::vector<TLorentzVector>& jets,
                 std::vector<TF1>& corrFns,
                 std::vector<float>& etaBins,
                 float minPt) {
    // NB to future self: tried to make corrFns and etaBins const,
    // but lower_bound doesn't like that

    // check corrFn correct size
    if (corrFns.size() != etaBins.size()-1) {
        throw range_error("Corrections functions don't match eta bins");
    }

    // Loop over jets, get correct function for given |eta| & apply if necessary
    for (auto& jetItr: jets) {
        // Get eta bin limits corresponding to jet |eta|
        float absEta = fabs(jetItr.Eta());
        auto maxItr = std::lower_bound(etaBins.begin(), etaBins.end(), absEta);
        if (maxItr == etaBins.begin()) {
            throw range_error("Max eta != first eta bin");
        }
        auto minItr = maxItr - 1;

        // Get correction fn for this bin
        TF1 corrFn = corrFns[minItr-etaBins.begin()];

        // Get fit range
        double fitMin(0.), fitMax(250.);
        corrFn.GetRange(fitMin, fitMax);

        // Now decide if we should apply corrections
        // Can either use range of fit function, or above some minimum pt
        // Might get rid of former option - get disjoint pt spectrum
        if (((minPt < 0.) && (jetItr.Pt() > fitMin) && (jetItr.Pt() < fitMax))
            || ((minPt >= 0.) && (jetItr.Pt() >= minPt))) {
            // corrFn.Print();
            float newPt = jetItr.Pt() * corrFn.Eval(jetItr.Pt());
            // safeguard against crazy values
            if (newPt < 1000. && newPt > 0.) {
                jetItr.SetPtEtaPhiM(newPt, jetItr.Eta(), jetItr.Phi(), jetItr.M());
            }
        }
    }
}
