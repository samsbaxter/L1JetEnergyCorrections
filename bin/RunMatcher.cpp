// ROOT headers
#include "TChain.h"
#include "TFile.h"
#include "TTree.h"
#include "TROOT.h"
#include "TSystem.h"

// BOOST headers
#include <boost/filesystem.hpp>
#include <boost/algorithm/string.hpp>

// Headers from L1TNtuples
#include "L1Trigger/L1TNtuples/interface/L1AnalysisL1ExtraDataFormat.h"
// #include "L1Trigger/L1TNtuples/interface/L1AnalysisEventDataFormat.h"

// Headers from this package
#include "DeltaR_Matcher.h"
#include "commonRootUtils.h"
#include "L1GenericTree.h"
#include "PileupInfoTree.h"
#include "RunMatcherOpts.h"
#include "JetDrawer.h"
#include "SortFilterEmulator.h"
#include "runMatcherUtils.h"

using std::cout;
using std::endl;
using L1Analysis::L1AnalysisL1ExtraDataFormat;
// using L1Analysis::L1AnalysisEventDataFormat;

namespace fs = boost::filesystem;

// forward declare fns, implementations after main()
std::vector<TLorentzVector> makeTLorentzVectors(std::vector<std::string> branchNames,
                                                L1AnalysisL1ExtraDataFormat * l1Extra);


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
    // Reference jets
    TString refJetDirectory = opts.refJetDirectory();
    std::vector<std::string> refJetBranches = opts.refJetBranchNames();
    L1GenericTree<L1AnalysisL1ExtraDataFormat> refJetTree(opts.inputFilename(),
                                                          refJetDirectory+"/L1ExtraTree",
                                                          "L1Extra");
    L1AnalysisL1ExtraDataFormat * refData = refJetTree.getData();

    TString l1JetDirectory = opts.l1JetDirectory();
    std::vector<std::string> l1JetBranches = opts.l1JetBranchNames();
    L1GenericTree<L1AnalysisL1ExtraDataFormat> l1JetTree(opts.inputFilename(),
                                                         l1JetDirectory+"/L1ExtraTree",
                                                         "L1Extra");
    L1AnalysisL1ExtraDataFormat * l1Data = l1JetTree.getData();

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
        if (iEntry % 10000 == 0) {
            cout << "Entry: " << iEntry << endl;
        }
        if (refJetTree.getEntry(iEntry) < 1 || l1JetTree.getEntry(iEntry) < 1) break;

        // store event info
        // eventChain->GetEntry(iEntry);
        // out_event = eventTree->event;

        // get pileup quantities
        // note these get stored once per pair of matched jets NOT once per event
        puInfoTree.GetEntry(iEntry);
        out_trueNumInteractions = puInfoTree.trueNumInteractions();
        out_numPUVertices = puInfoTree.numPUVertices();

        // Get vectors of ref & L1 jets from trees
        auto refJets = makeTLorentzVectors(refJetBranches, refData);
        auto l1Jets  = makeTLorentzVectors(l1JetBranches, l1Data);

        if (refJets.size() == 0 || l1Jets.size() == 0) continue;

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
    } // end of event loop

    // save tree to new file and cleanup
    outTree.Write("", TObject::kOverwrite);
    outFile->Close();
}


/**
 * @brief Make a std::vector of TLorentxVectors out of jets stored in a
 * L1ExtradataFormat matching branchNames.
 * @details Not a very smart implementation. Manually implement a mapping between
 * branchName and actual fields in the L1Extra format. Smarter way?
 *
 * @param branchNames Vector of branch names. Currently supports "cenJet" and "fwdJet"
 * @param l1Extra Pointer to L1AnalysisL1ExtraDataFormat object to get collections from.
 *
 * @return [description]
 */
std::vector<TLorentzVector> makeTLorentzVectors(std::vector<std::string> branchNames,
                                                L1AnalysisL1ExtraDataFormat * l1Extra) {
    std::vector<TLorentzVector> jets;
    for (auto &itr : branchNames) {
        boost::algorithm::to_lower(itr);
        if (itr == "cenjet") {
            auto tmp = makeTLorentzVectors(l1Extra->cenJetEt, l1Extra->cenJetEta, l1Extra->cenJetPhi);
            jets.insert(jets.end(), tmp.begin(), tmp.end());
        }
        if (itr == "fwdjet") {
            auto tmp = makeTLorentzVectors(l1Extra->fwdJetEt, l1Extra->fwdJetEta, l1Extra->fwdJetPhi);
            jets.insert(jets.end(), tmp.begin(), tmp.end());
        }
    }
    return jets;
}
