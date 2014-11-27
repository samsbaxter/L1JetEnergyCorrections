#include <iostream>
#include <vector>
#include <utility>

#include "TCanvas.h"
// #include "TInterpreter.h"
#include "TChain.h"
#include "TFile.h"
#include "TDirectoryFile.h"
#include "TTree.h"
#include "TROOT.h"
#include "TSystem.h"
#include "TLorentzVector.h"
#include "TRegexp.h"
#include "TString.h"

// #include <boost/algorithm/string.hpp>

#include "DeltaR_Matcher.h"
#include "commonRootUtils.h"

#include "../../../L1TriggerDPG/L1Ntuples/interface/L1AnalysisL1ExtraDataFormat.h"

#include "L1ExtraTree.h"


using std::cout;
using std::endl;
// using namespace boost;


/**
 * @brief This program implements an instance of Matcher to produce a ROOT file
 * with matching jet pairs from a L1NTuple file produced by XXX.
 * @details READ BEFORE RUNNING: To get this to work, you first need to build
 * the dictionaries ROOT needs to store vectors/pairs in TTree. See interface/LinkDef.h
 * for instructions.
 * @author Robin Aggleton, Nov 2014
 */
int main() {

    cout << "Running Matcher" << std::endl;
    // TODO: user program args

    // get input L1Extra trees
    TString refJetDirectory = "l1ExtraTreeProducerGenAk5";
    TString refJetSuffix  = refJetDirectory;
    TRegexp re("l1ExtraTreeProducer");
    refJetSuffix(re) = "";
    TString l1JetDirectory  = "l1ExtraTreeProducerGctIntern";
    TString l1JetSuffix  = l1JetDirectory;
    l1JetSuffix(re) = "";

    L1ExtraTree refJetExtraTree("python/L1Tree.root", "l1ExtraTreeProducerGenAk5");
    L1ExtraTree l1JetExtraTree("python/L1Tree.root", "l1ExtraTreeProducerGctIntern");

    // setup your jet matcher
    double maxDeltaR(0.7), minRefJetPt(0.), minL1JetPt(0.), maxJetEta(5.5);
    DeltaR_Matcher * matcher = new DeltaR_Matcher(maxDeltaR, minRefJetPt, minL1JetPt, maxJetEta);
    std::vector<std::pair<TLorentzVector, TLorentzVector>> matchResults; // holds results from one event

    // setup output tree to store matched pairs
    TString outTreeName;
    outTreeName.Form("MatchedPairs_%s_%s", refJetSuffix.Data(), l1JetSuffix.Data());
    TString outTreeTitle = outTreeName;
    TTree * outTree = new TTree(outTreeName, outTreeTitle);
    outTree->Branch("MatchedPairs", &matchResults);

    // check # events in boths trees is same
    // - if not then throw exception?
    Long64_t nEntriesRef = refJetExtraTree.fChain->GetEntriesFast();
    Long64_t nEntriesL1  = l1JetExtraTree.fChain->GetEntriesFast();
    if (nEntriesRef != nEntriesL1) {
        throw "Different number of events in L1 & ref trees";
    }

    // loop over all events in trees, produce matching pairs and store
    TMultiGraph *jetPlots;
    for (Long64_t iEntry = 0; iEntry < 1; ++iEntry) {

        Long64_t jentry = refJetExtraTree.LoadTree(iEntry); // jentry is the entry # in the current Tree
        if (jentry < 0) break;
        refJetExtraTree.fChain->GetEntry(iEntry);
        l1JetExtraTree.fChain->GetEntry(iEntry);

        // Get vectors of ref & L1 jets from trees
        std::vector<TLorentzVector> refJets = refJetExtraTree.makeTLorentzVectors("cenJet");
        std::vector<TLorentzVector> l1Jets  = l1JetExtraTree.makeTLorentzVectors("cenJet");

        // Pass jets to matcher, do matching, store output in tree
        matchResults.clear();
        matcher->setRefJets(refJets);
        matcher->setL1Jets(l1Jets);
        matchResults = matcher->getMatchingPairs();
        matcher->printMatches(matchResults);

        TCanvas c1;
        jetPlots = matcher->plotJets();
        jetPlots->Draw("ap");
        c1.SaveAs("jets.pdf");

        outTree->Fill();
    }

    // save tree to new file and cleanup
    TString outFilename("pairs.root");
    TFile * outFile = openFile(outFilename, "RECREATE");
    outTree->Write("", TObject::kOverwrite);
    jetPlots->Write("", TObject::kOverwrite);

    // cleanup
    outFile->Close();
}