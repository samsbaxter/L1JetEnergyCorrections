// STL headers
#include <iostream>
#include <vector>
#include <utility>
#include <stdexcept>

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

// Headers from this package
#include "DeltaR_Matcher.h"
#include "commonRootUtils.h"
#include "L1ExtraTree.h"
#include "RunMatcherOpts.h"
#include "JetDrawer.h"

using std::cout;
using std::endl;
namespace fs = boost::filesystem;

// forward declare fns, implementations after main()
TString getSuffixFromDirectory(const TString& dir);


/**
 * @brief This program implements an instance of Matcher to produce a ROOT file
 * with matching jet pairs from a L1NTuple file produced by python/l1Ntuple_cfg.py.
 * @details READ BEFORE RUNNING: To get this to work, you first need to build
 * the dictionaries ROOT needs to store vectors/pairs in TTree. See READEM or
 * interface/LinkDef.h for instructions.
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

    // input filename stem (no .root)
    fs::path inPath(opts.inputFilename());
    TString inStem(inPath.stem().c_str());

    ////////////////////////
    // SETUP OUTPUT FILES //
    ////////////////////////

    // setup output file to store results
    TFile * outFile = openFile(opts.outputFilename(), "RECREATE");

    // setup output tree to store matched pairs (keep all info)
    TString outTreeName = TString::Format("MatchedPairs_%s_%s",
        refJetSuffix.Data(), l1JetSuffix.Data());
    TTree * outTree = new TTree(outTreeName, outTreeName);
    std::vector<std::pair<TLorentzVector, TLorentzVector>> matchResults; // holds results from one event
    outTree->Branch("MatchedPairs", &matchResults);

    // setup output tree to store raw variable for quick plotting/debugging
    TTree * outTree2 = new TTree("valid", "valid");
    // pt/eta/phi are for l1 jets
    float out_pt(-1.), out_eta(99.), out_phi(99.), out_rsp(-1.), out_rsp2(-1.);
    float out_dr(99.), out_deta(99.), out_dphi(99.), out_etaRef(99.), out_phiRef(99.);
    outTree2->Branch("pt"   ,&out_pt ,"pt/Float_t");
    outTree2->Branch("eta"  ,&out_eta,"eta/Float_t");
    outTree2->Branch("phi"  ,&out_phi,"phi/Float_t");
    outTree2->Branch("rsp"  ,&out_rsp,"rsp/Float_t"); // response = refJet pT/ l1 jet pT
    outTree2->Branch("rsp2"  ,&out_rsp2,"rsp2/Float_t"); // response = refJet pT/ l1 jet pT
    outTree2->Branch("dr"   ,&out_dr,"dr/Float_t");
    outTree2->Branch("deta" ,&out_deta,"deta/Float_t");
    outTree2->Branch("dphi" ,&out_dphi,"dphi/Float_t");
    outTree2->Branch("etaRef" ,&out_etaRef,"etaRef/Float_t");
    outTree2->Branch("phiRef" ,&out_phiRef,"phiRef/Float_t");

    // check # events in boths trees is same
    // - if not then throw exception?
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
    double maxDeltaR(0.7), minRefJetPt(14.), maxRefJetPt(250.);
    double minL1JetPt(0.), maxL1JetPt(250.), maxJetEta(5);
    std::unique_ptr<Matcher> matcher(new DeltaR_Matcher(maxDeltaR, minRefJetPt, maxRefJetPt, minL1JetPt, maxL1JetPt, maxJetEta));
    matcher->printName();

    //////////////////////
    // LOOP OVER EVENTS //
    //////////////////////
    // produce matching pairs and store
    for (Long64_t iEntry = 0; iEntry < nEntries; ++iEntry) {

        Long64_t jentry = refJetExtraTree.LoadTree(iEntry); // jentry is the entry # in the current Tree
        if (jentry < 0) break;
        refJetExtraTree.fChain->GetEntry(iEntry);
        l1JetExtraTree.fChain->GetEntry(iEntry);

        // Get vectors of ref & L1 jets from trees
        std::vector<TLorentzVector> refJets = refJetExtraTree.makeTLorentzVectors(refJetBranches);
        std::vector<TLorentzVector> l1Jets  = l1JetExtraTree.makeTLorentzVectors(l1JetBranches);

        // Pass jets to matcher, do matching, store output in tree
        matchResults.clear();
        matcher->setRefJets(refJets);
        matcher->setL1Jets(l1Jets);
        matchResults = matcher->getMatchingPairs();
        // matcher->printMatches();

        // store L1 & ref jet variables
        for (const auto &it: matchResults) {
            out_pt = it.second.Et();
            out_eta = it.second.Eta();
            out_phi = it.second.Phi();
            out_rsp = it.first.Et()/it.second.Et();
            out_rsp2 = it.second.Et()/it.first.Et();
            out_dr = it.first.DeltaR(it.second);
            out_deta = it.first.Eta() - it.second.Eta();
            out_dphi = it.first.DeltaPhi(it.second);
            out_etaRef = it.first.Eta();
            out_phiRef = it.first.Phi();
            outTree2->Fill();
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
                inStem.Data(), refJetSuffix.Data(), l1JetSuffix.Data(), iEntry);
            drawer.drawAndSave(pdfname);
        }

        outTree->Fill();
    }

    // save tree to new file and cleanup
    outTree->Write("", TObject::kOverwrite);
    outTree2->Write("", TObject::kOverwrite);

    // cleanup
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