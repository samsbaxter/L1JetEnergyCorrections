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
#include "L1Trigger/L1TNtuples/interface/L1AnalysisL1UpgradeDataFormat.h"

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
using L1Analysis::L1AnalysisRecoJetDataFormat;
using L1Analysis::L1AnalysisL1UpgradeDataFormat;
using boost::lexical_cast;
namespace fs = boost::filesystem;

// forward declare fns, implementations after main()
bool checkTriggerFired(const std::vector<TString> & hlt, const std::string& selection);
void rescaleEnergyFractions(L1AnalysisRecoJetDataFormat * jets);
std::vector<TLorentzVector> makeRecoTLorentzVectorsCleaned(const L1AnalysisRecoJetDataFormat & jets, std::string quality);
int findRecoJetIndex(float et, float eta, float phi, const L1AnalysisRecoJetDataFormat & jets);
bool looseCleaning(float eta,
                   float chef, float nhef, float pef, float eef, float mef, float hfhef, float hfemef,
                   short chMult, short nhMult, short phMult, short elMult, short muMult, short hfhMult, short hfemMult);
bool tightCleaning(float eta,
                   float chef, float nhef, float pef, float eef, float mef, float hfhef, float hfemef,
                   short chMult, short nhMult, short phMult, short elMult, short muMult, short hfhMult, short hfemMult);
bool tightLepVetoCleaning(float eta,
                          float chef, float nhef, float pef, float eef, float mef, float hfhef, float hfemef,
                          short chMult, short nhMult, short phMult, short elMult, short muMult, short hfhMult, short hfemMult);
void getCSCList(std::string filename, std::vector<std::string> & lines);

/**
 * @brief
 * This version is for running on data, when you want to take L1 jets from the
 * L1Upgrade collection, and reference jets from the RecoTree.
 *
 * @author Robin Aggleton, Nov 2015
 */
int main(int argc, char* argv[]) {

    cout << "Running Matcher for data" << std::endl;

    // deal with user args
    RunMatcherOpts opts(argc, argv);

    ///////////////////////
    // SETUP INPUT FILES //
    ///////////////////////
    // get input TTrees
    // Reco jets
    TString refJetDirectory = opts.refJetDirectory();
    L1GenericTree<L1AnalysisRecoJetDataFormat> refJetTree(opts.inputFilename(),
                                                          refJetDirectory+"/JetRecoTree",
                                                          "Jet");
    L1AnalysisRecoJetDataFormat * refData = refJetTree.getData();

    // L1 jets
    TString l1JetDirectory = opts.l1JetDirectory();
    L1GenericTree<L1AnalysisL1UpgradeDataFormat> l1JetTree(opts.inputFilename(),
                                                           l1JetDirectory+"/L1UpgradeTree",
                                                           "L1Upgrade");
    L1AnalysisL1UpgradeDataFormat * l1Data = l1JetTree.getData();


    // hold Event tree
    L1GenericTree<L1AnalysisEventDataFormat> eventTree(opts.inputFilename(),
                                                       "l1Tree/L1Tree",
                                                       "Event");
    L1AnalysisEventDataFormat * eventData = eventTree.getData();

    // input filename stem (no .root)
    fs::path inPath(opts.inputFilename());
    TString inStem(inPath.stem().c_str());

    std::vector<std::string> cscList;
    getCSCList("/hdfs/user/ra12451/L1JEC/csc2015_260627.txt", cscList);

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
    int out_ind(-1); // index of this jet in the collection (ordered by descending pT)
    outTree.Branch("pt", &out_pt, "pt/F");
    outTree.Branch("eta", &out_eta, "eta/F");
    outTree.Branch("phi", &out_phi, "phi/F");
    outTree.Branch("nL1", &out_nL1, "nL1/I");
    outTree.Branch("indL1", &out_ind, "indL1/I");
    // Quantities for reference jets (GenJet, etc):
    float out_ptRef(-1.), out_etaRef(99.), out_phiRef(99.);
    int out_nRef(-1), out_indRef;
    outTree.Branch("ptRef", &out_ptRef, "ptRef/F");
    outTree.Branch("etaRef", &out_etaRef, "etaRef/F");
    outTree.Branch("phiRef", &out_phiRef, "phiRef/F");
    outTree.Branch("nRef", &out_nRef, "nRef/I");
    outTree.Branch("indRef", &out_indRef, "indRef/I");
    // Cleaning vars
    float out_chef(-1.), out_nhef(-1.), out_pef(-1.), out_eef(-1.), out_mef(-1.), out_hfhef(-1.), out_hfemef(-1.);
    short out_chMult(-1), out_nhMult(-1), out_phMult(-1), out_elMult(-1), out_muMult(-1), out_hfhMult(-1), out_hfemMult(-1);
    outTree.Branch("chef", &out_chef, "chef/F");
    outTree.Branch("nhef", &out_nhef, "nhef/F");
    outTree.Branch("pef", &out_pef, "pef/F");
    outTree.Branch("eef", &out_eef, "eef/F");
    outTree.Branch("mef", &out_mef, "mef/F");
    outTree.Branch("hfhef", &out_hfhef, "hfhef/F");
    outTree.Branch("hfemef", &out_hfemef, "hfemef/F");
    outTree.Branch("chMult", &out_chMult, "chMult/S");
    outTree.Branch("nhMult", &out_nhMult, "nhMult/S");
    outTree.Branch("phMult", &out_phMult, "phMult/S");
    outTree.Branch("elMult", &out_elMult, "elMult/S");
    outTree.Branch("muMult", &out_muMult, "muMult/S");
    outTree.Branch("hfhMult", &out_hfhMult, "hfhMult/S");
    outTree.Branch("hfemMult", &out_hfemMult, "hfemMult/S");
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
    // PU quantities
    float out_trueNumInteractions(-1.), out_numPUVertices(-1.);
    outTree.Branch("trueNumInteractions", &out_trueNumInteractions, "trueNumInteractions/F");
    outTree.Branch("numPUVertices", &out_numPUVertices, "numPUVertices/F");
    // Event info
    ULong64_t out_event(0);
    int out_ls(0);
    bool out_passCSC(true), out_ZeroBias(false);
    outTree.Branch("event", &out_event, "event/l");
    outTree.Branch("LS", &out_ls, "ls/I");
    outTree.Branch("passCSC", &out_passCSC, "passCSC/Bool_t");
    outTree.Branch("zeroBias", &out_ZeroBias, "zeroBias/Bool_t");

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
    std::unique_ptr<Matcher> matcher(new DeltaR_Matcher(maxDeltaR, minRefJetPt, maxRefJetPt, minL1JetPt, maxL1JetPt, maxJetEta));
    std::cout << *matcher << std::endl;

    //////////////////////
    // LOOP OVER EVENTS //
    //////////////////////
    // produce matching pairs and store
    Long64_t drawCounter(0), matchedEvent(0), cscFail(0);
    for (Long64_t iEntry = 0; iEntry < nEntries; ++iEntry) {

        if (iEntry % 10000 == 0) {
            cout << "Entry: " << iEntry << " at " << getCurrentTime() << endl;
        }

        if (refJetTree.getEntry(iEntry) < 1 ||
            l1JetTree.getEntry(iEntry) < 1 ||
            eventTree.getEntry(iEntry) < 1)
            break;

        // event info
        // fix underflow bug from ulonglong -> int for evt number
        int evt_num = eventData->event;
        out_event = (evt_num < 0) ? evt_num + 4294967296 : evt_num;
        out_ls = eventData->lumi;

        // Check CSC beam halo
        std::string thisEvent = lexical_cast<std::string>(out_ls) + ":" + lexical_cast<std::string>(out_event);
        out_passCSC = !(std::binary_search(cscList.begin(), cscList.end(), thisEvent));
        if (!out_passCSC) cscFail++;

        // Check which triggers fired
        out_ZeroBias = checkTriggerFired(eventData->hlt, "HLT_ZeroBias_v");

        // Rescale jet energy fractions to take account of the fact that they are post-JEC
        rescaleEnergyFractions(refData);

        // Get vectors of ref & L1 jets from trees
        // Note that we only want BX = 0 (the collision)
        std::vector<TLorentzVector> refJets = makeTLorentzVectors(refData->et, refData->eta, refData->phi);
        // std::vector<TLorentzVector> refJets = makeRecoTLorentzVectorsCleaned(*refData, "TIGHTLEPVETO"); // with JetID filters
        std::vector<TLorentzVector> l1Jets  = makeTLorentzVectors(l1Data->jetEt, l1Data->jetEta, l1Data->jetPhi, l1Data->jetBx);

        out_nL1 = l1Jets.size();
        out_nRef = refJets.size();

        // Pass jets to matcher, do matching
        matcher->setRefJets(refJets);
        matcher->setL1Jets(l1Jets);
        std::vector<MatchedPair> matchResults = matcher->getMatchingPairs();

        if (matchResults.size()>0) matchedEvent++;

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

            int rInd = findRecoJetIndex(out_ptRef, out_etaRef, out_phiRef, *refData);
            if (rInd < 0) throw std::range_error("No RecoJet");
            out_chef = refData->chef[rInd];
            out_nhef = refData->nhef[rInd];
            out_pef = refData->pef[rInd];
            out_eef = refData->eef[rInd];
            out_mef = refData->mef[rInd];
            out_hfhef = refData->hfhef[rInd];
            out_hfemef = refData->hfemef[rInd];
            out_chMult = refData->chMult[rInd];
            out_nhMult = refData->nhMult[rInd];
            out_phMult = refData->phMult[rInd];
            out_elMult = refData->elMult[rInd];
            out_muMult = refData->muMult[rInd];
            out_hfhMult = refData->hfhMult[rInd];
            out_hfemMult = refData->hfemMult[rInd];
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
                    outDir.Data(), inStem.Data(), "reco", "l1", iEntry);
                drawer.drawAndSave(pdfname);

                drawCounter++;
            }
        }
    }

    // save tree to new file and cleanup
    outTree.Write("", TObject::kOverwrite);
    outFile->Close();
    cout << matchedEvent << " events had 1+ matches, out of " << nEntries << endl;
    cout << cscFail << " events failed CSC check, out of " << nEntries << endl;
}


/**
 * @brief Check if a certain trigger was fired.
 * @details Note, only checks to see if it was fired,
 * not if it was the *only* trigger that was fired.
 *
 * @param hlt Input vector of TStrings of tirgger names fired
 * @param selection Trigger name
 *
 * @return [description]
 */
bool checkTriggerFired(const std::vector<TString> & hlt, const std::string & selection) {
    for (const auto & hltItr: hlt) {
        if (std::string(hltItr).find(selection) != std::string::npos)
            return true;
    }
    return false;
}

/**
 * @brief Rescale jet energy fractions to account for the fact that they are
 * stored after JEC, but cuts apply *before* JEC.
 * @details JEC only affects the total energy, so we can just rescale by the
 * sum of energy fractions (which should = 1)
 */
void rescaleEnergyFractions(L1AnalysisRecoJetDataFormat * jets) {
    for (int i = 0; i < jets->nJets; ++i) {
        float totalEf = jets->chef[i] + jets->nhef[i] + jets->pef[i] + jets->eef[i] + jets->mef[i] + jets->hfhef[i] + jets->hfemef[i];
        jets->chef[i] /= totalEf;
        jets->nhef[i] /= totalEf;
        jets->pef[i] /= totalEf;
        jets->eef[i] /= totalEf;
        jets->mef[i] /= totalEf;
        jets->hfhef[i] /= totalEf;
        jets->hfemef[i] /= totalEf;
    }
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
std::vector<TLorentzVector> makeRecoTLorentzVectorsCleaned(const L1AnalysisRecoJetDataFormat & jets, std::string quality) {

    std::vector<TLorentzVector> vecs;

    for (int i = 0; i < jets.nJets; ++i) {
        if (quality == "LOOSE") {
            if (!looseCleaning(jets.eta[i],
                               jets.chef[i], jets.nhef[i], jets.pef[i], jets.eef[i], jets.mef[i], jets.hfhef[i], jets.hfemef[i],
                               jets.chMult[i], jets.nhMult[i], jets.phMult[i], jets.elMult[i], jets.muMult[i], jets.hfhMult[i], jets.hfemMult[i]))
                continue;
        } else if (quality == "TIGHT") {
            if (!tightCleaning(jets.eta[i],
                               jets.chef[i], jets.nhef[i], jets.pef[i], jets.eef[i], jets.mef[i], jets.hfhef[i], jets.hfemef[i],
                               jets.chMult[i], jets.nhMult[i], jets.phMult[i], jets.elMult[i], jets.muMult[i], jets.hfhMult[i], jets.hfemMult[i]))
                continue;
        } else if (quality == "TIGHTLEPVETO") {
            if (!tightLepVetoCleaning(jets.eta[i],
                                      jets.chef[i], jets.nhef[i], jets.pef[i], jets.eef[i], jets.mef[i], jets.hfhef[i], jets.hfemef[i],
                                      jets.chMult[i], jets.nhMult[i], jets.phMult[i], jets.elMult[i], jets.muMult[i], jets.hfhMult[i], jets.hfemMult[i]))
                continue;
        } else {
            throw std::runtime_error("quality must be LOOSE/TIGHT/TIGHTLEPVETO");
        }
        // If got this far, then can add to list.
        TLorentzVector v;
        v.SetPtEtaPhiM(jets.et[i], jets.eta[i], jets.phi[i], 0);
        vecs.push_back(v);
    }

    return vecs;
}


bool looseCleaning(float eta,
                   float chef, float nhef, float pef, float eef, float mef, float hfhef, float hfemef,
                   short chMult, short nhMult, short phMult, short elMult, short muMult, short hfhMult, short hfemMult) {
    if (fabs(eta) < 3) {
        if ((fabs(eta) < 2.4) && !((chef > 0) && ((chMult+elMult+muMult) > 0) && (eef < 0.99)))
            return false;
        return (nhef < 0.99) && (pef < 0.99) && ((chMult+nhMult+phMult+elMult+muMult) > 1);
    } else {
        // TODO: HF
        return true;
    }
}


bool tightCleaning(float eta,
                   float chef, float nhef, float pef, float eef, float mef, float hfhef, float hfemef,
                   short chMult, short nhMult, short phMult, short elMult, short muMult, short hfhMult, short hfemMult) {
    if (fabs(eta) < 3) {
        if ((fabs(eta) < 2.4) && !((chef > 0) && ((chMult+elMult+muMult) > 0) && (eef < 0.99)))
            return false;
        return (nhef < 0.9) && (pef < 0.9) && ((chMult+nhMult+phMult+elMult+muMult) > 1);
    } else {
        return true;
    }
}


bool tightLepVetoCleaning(float eta,
                          float chef, float nhef, float pef, float eef, float mef, float hfhef, float hfemef,
                          short chMult, short nhMult, short phMult, short elMult, short muMult, short hfhMult, short hfemMult) {
    if (fabs(eta) < 3) {
        if ((fabs(eta) < 2.4) && !((chef > 0) && ((chMult+elMult+muMult) > 0) && (eef < 0.9)))
            return false;
        return (nhef < 0.9) && (pef < 0.9) && ((chMult+nhMult+phMult+elMult+muMult) > 1) && (mef < 0.8);
    } else {
        return true;
    }
}


int findRecoJetIndex(float et, float eta, float phi, const L1AnalysisRecoJetDataFormat & jets) {
    for (int i = 0; i < jets.nJets; ++i){
        if (jets.et[i] == et && jets.eta[i] == eta && jets.phi[i] == phi)
            return i;
    }
    return -1;
}


void getCSCList(std::string filename, std::vector<std::string> & lines) {
    cout << "Populating CSC list" << endl;
    std::ifstream infile(filename);
    std::string line = "";
    while (infile >> line) {
        lines.push_back(line);
    }
    if (lines.size() == 0) {
        throw std::range_error("CSC list is empty - check input file exists");
    }
}
