//////////////////////////////////////////////////////////
// This class has been automatically generated on
// Fri Nov 21 15:50:50 2014 by ROOT version 5.34/18
// from TTree L1ExtraTree/L1ExtraTree
// found on file: L1Tree.root
//////////////////////////////////////////////////////////

#ifndef L1ExtraTree_h
#define L1ExtraTree_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>
#include <TString.h>
#include <TTree.h>
#include <TLorentzVector.h>

// #include "../../../L1TriggerDPG/L1Ntuples/interface/L1AnalysisL1ExtraDataFormat.h"

using namespace std;

/**
 * @brief Class to interface to L1ExtraTree produced by L1ExtraTreeProducer.
 * @details Based on default class generation by ROOT - hence all the public
 * data members, raw pointers, etc. Not really happy with this, but it'll do (for now)
 * @author Robin Aggleton
 */
class L1ExtraTree {
public :
    TTree          *fChain;   //!<pointer to the analyzed TTree or TChain
    Int_t           fCurrent; //!<current Tree number in a TChain

    // Declaration of leaf types
 //L1Analysis::L1AnalysisL1ExtraDataFormat *L1Extra;
    UInt_t          nIsoEm;   //!< Number of isolated EM obj in event
    vector<double>  isoEmEt;
    vector<double>  isoEmEta;
    vector<double>  isoEmPhi;
    vector<int>     isoEmBx;
    UInt_t          nNonIsoEm;   //!< Number of non-isolated EM obj in event
    vector<double>  nonIsoEmEt;
    vector<double>  nonIsoEmEta;
    vector<double>  nonIsoEmPhi;
    vector<int>     nonIsoEmBx;
    UInt_t          nCenJets;   //!< Number of central jets in event
    vector<double>  cenJetEt;
    vector<double>  cenJetEta;
    vector<double>  cenJetPhi;
    vector<int>     cenJetBx;
    UInt_t          nFwdJets;   //!< Number of forward jets in event
    vector<double>  fwdJetEt;
    vector<double>  fwdJetEta;
    vector<double>  fwdJetPhi;
    vector<int>     fwdJetBx;
    UInt_t          nTauJets;   //!< Number of tau jets in event
    vector<double>  tauJetEt;
    vector<double>  tauJetEta;
    vector<double>  tauJetPhi;
    vector<int>     tauJetBx;
    UInt_t          nMuons;   //!< Number of muons in event
    vector<double>  muonEt;
    vector<double>  muonEta;
    vector<double>  muonPhi;
    vector<int>     muonChg;
    vector<unsigned int> muonIso;
    vector<unsigned int> muonFwd;
    vector<unsigned int> muonMip;
    vector<unsigned int> muonRPC;
    vector<int>     muonBx;
    vector<int>     muonQuality;
    vector<double>  hfEtSum;
    vector<unsigned int> hfBitCnt;
    vector<int>     hfBx;
    UInt_t          nMet;
    vector<double>  et;
    vector<double>  met;
    vector<double>  metPhi;
    vector<double>  metBx;
    UInt_t          nMht;
    vector<double>  ht;
    vector<double>  mht;
    vector<double>  mhtPhi;
    vector<double>  mhtBx;

    /**
     * @brief Constructor, getting "L1ExtraTree" from directory in filename
     * @details [long description]
     *
     * @param filename ROOT file to get L1ExtraTree from
     * @param directory Directory that L1ExtraTree is stored in (e.g. l1ExtraTreeProducer)
     * @param tree Optional TTree to use instead of from file... shoudl prob do diff ctors.
     */
    L1ExtraTree(TString filename, TString directory, TString treeName="L1ExtraTree", TTree *tree=0);

    /**
     * @brief Destructor
     * @details  Deleteing just fChain ok as it "owns" all branch pointers, etc?
    */
    virtual ~L1ExtraTree();

    /**
     * @brief Read contents of specified event number
     * @details Values of all branches for this entry are loaded into class variables
     *
     * @param entry Entry number
     * @return Total number of bytes read, or 0 if unsuccessful
     */
    virtual Int_t    GetEntry(Long64_t entry);

    /**
     * @brief Set the environment to read one entry
     * @details [long description]
     *
     * @param entry [description]
     * @return [description]
     */
    virtual Long64_t LoadTree(Long64_t entry);

    /**
     * @brief The Init() function is called when the selector needs to initialize
     * a new tree or chain. Typically here the branch addresses and branch
     * pointers of the tree will be set.
     * @details It is normally not necessary to make changes to the generated
     * code, but the routine can be extended by the user if needed.
     * Init() will be called many times when running on PROOF
     * (once per file to be processed).
     *
     * @param tree Tree to initialise
     */
    virtual void     Init(TTree *tree);

    /**
     * @brief The Notify() function is called when a new file is opened. This
     * can be either for a new TTree in a TChain or when when a new TTree
     * is started when using PROOF.
     * @details It is normally not necessary to make changes
     * to the generated code, but the routine can be extended by the
     * user if needed. The return value is currently not used.
     * @return [description]
     */
    virtual Bool_t   Notify();

    /**
     * @brief Prints contents of entry
     * @details If entry not specified, print current entry
     *
     * @param entry Entry number to print, if unspecified prints current entry.
     */
    virtual void     Show(Long64_t entry = -1);

    /**
     * @brief Makes vector of TLorentzVectors from given branch for a given event
     * (so you need to call fChain->GetEntry(i) first)
     * @details Utilises variables stored in branches: branchName+Et,
     * branchName+Eta, branchName+Phi
     *
     * @param branchName Branch to be considered, e.g. cenJet, or tauJet
     * @return Vector of TLorentzVectors
     */
    virtual std::vector<TLorentzVector> makeTLorentzVectors(TString branchName) const;


    /**
     * @brief Makes vector of TLorentzVectors from given branches for a given event
     * (so you need to call fChain->GetEntry(i) first)
     * @details Utilises variables stored in branches: branchName+Et,
     * branchName+Eta, branchName+Phi.
     *
     * @param branchNames Branches to be considered, e.g. cenJet, or tauJet
     * @return Vector of TLorentzVectors
     */
    virtual std::vector<TLorentzVector> makeTLorentzVectors(std::vector<std::string> branchNames) const;

private:
    // List of branches
    TBranch        *b_L1Extra_nIsoEm;   //!< Number of isolated EM obj in event
    TBranch        *b_L1Extra_isoEmEt;   //!<
    TBranch        *b_L1Extra_isoEmEta;   //!<
    TBranch        *b_L1Extra_isoEmPhi;   //!<
    TBranch        *b_L1Extra_isoEmBx;   //!<
    TBranch        *b_L1Extra_nNonIsoEm;   //!< Number of non-isolated EM obj in event
    TBranch        *b_L1Extra_nonIsoEmEt;   //!<
    TBranch        *b_L1Extra_nonIsoEmEta;   //!<
    TBranch        *b_L1Extra_nonIsoEmPhi;   //!<
    TBranch        *b_L1Extra_nonIsoEmBx;   //!<
    TBranch        *b_L1Extra_nCenJets;   //!< Number of central jets in event
    TBranch        *b_L1Extra_cenJetEt;   //!<
    TBranch        *b_L1Extra_cenJetEta;   //!<
    TBranch        *b_L1Extra_cenJetPhi;   //!<
    TBranch        *b_L1Extra_cenJetBx;   //!<
    TBranch        *b_L1Extra_nFwdJets;   //!< Number of forward jets in event
    TBranch        *b_L1Extra_fwdJetEt;   //!<
    TBranch        *b_L1Extra_fwdJetEta;   //!<
    TBranch        *b_L1Extra_fwdJetPhi;   //!<
    TBranch        *b_L1Extra_fwdJetBx;   //!<
    TBranch        *b_L1Extra_nTauJets;   //!< Number of tau jets in event
    TBranch        *b_L1Extra_tauJetEt;   //!<
    TBranch        *b_L1Extra_tauJetEta;   //!<
    TBranch        *b_L1Extra_tauJetPhi;   //!<
    TBranch        *b_L1Extra_tauJetBx;   //!<
    TBranch        *b_L1Extra_nMuons;   //!< Number of muons in event
    TBranch        *b_L1Extra_muonEt;   //!<
    TBranch        *b_L1Extra_muonEta;   //!<
    TBranch        *b_L1Extra_muonPhi;   //!<
    TBranch        *b_L1Extra_muonChg;   //!<
    TBranch        *b_L1Extra_muonIso;   //!<
    TBranch        *b_L1Extra_muonFwd;   //!<
    TBranch        *b_L1Extra_muonMip;   //!<
    TBranch        *b_L1Extra_muonRPC;   //!<
    TBranch        *b_L1Extra_muonBx;   //!<
    TBranch        *b_L1Extra_muonQuality;   //!<
    TBranch        *b_L1Extra_hfEtSum;   //!<
    TBranch        *b_L1Extra_hfBitCnt;   //!<
    TBranch        *b_L1Extra_hfBx;   //!<
    TBranch        *b_L1Extra_nMet;   //!<
    TBranch        *b_L1Extra_et;   //!<
    TBranch        *b_L1Extra_met;   //!<
    TBranch        *b_L1Extra_metPhi;   //!<
    TBranch        *b_L1Extra_metBx;   //!<
    TBranch        *b_L1Extra_nMht;   //!<
    TBranch        *b_L1Extra_ht;   //!<
    TBranch        *b_L1Extra_mht;   //!<
    TBranch        *b_L1Extra_mhtPhi;   //!<
    TBranch        *b_L1Extra_mhtBx;   //!<
};

#endif