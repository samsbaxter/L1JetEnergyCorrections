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

#include "../../../L1TriggerDPG/L1Ntuples/interface/L1AnalysisL1ExtraDataFormat.h"

using namespace std;
// Header file for the classes stored in the TTree if any.

// Fixed size dimensions of array or collections stored in the TTree if any.

class L1ExtraTree {
public :
   TTree          *fChain;   //!pointer to the analyzed TTree or TChain
   Int_t           fCurrent; //!current Tree number in a TChain

   // Declaration of leaf types
 //L1Analysis::L1AnalysisL1ExtraDataFormat *L1Extra;
   UInt_t          nIsoEm;
   vector<double>  isoEmEt;
   vector<double>  isoEmEta;
   vector<double>  isoEmPhi;
   vector<int>     isoEmBx;
   UInt_t          nNonIsoEm;
   vector<double>  nonIsoEmEt;
   vector<double>  nonIsoEmEta;
   vector<double>  nonIsoEmPhi;
   vector<int>     nonIsoEmBx;
   UInt_t          nCenJets;
   vector<double>  cenJetEt;
   vector<double>  cenJetEta;
   vector<double>  cenJetPhi;
   vector<int>     cenJetBx;
   UInt_t          nFwdJets;
   vector<double>  fwdJetEt;
   vector<double>  fwdJetEta;
   vector<double>  fwdJetPhi;
   vector<int>     fwdJetBx;
   UInt_t          nTauJets;
   vector<double>  tauJetEt;
   vector<double>  tauJetEta;
   vector<double>  tauJetPhi;
   vector<int>     tauJetBx;
   UInt_t          nMuons;
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

   // List of branches
   TBranch        *b_L1Extra_nIsoEm;   //!
   TBranch        *b_L1Extra_isoEmEt;   //!
   TBranch        *b_L1Extra_isoEmEta;   //!
   TBranch        *b_L1Extra_isoEmPhi;   //!
   TBranch        *b_L1Extra_isoEmBx;   //!
   TBranch        *b_L1Extra_nNonIsoEm;   //!
   TBranch        *b_L1Extra_nonIsoEmEt;   //!
   TBranch        *b_L1Extra_nonIsoEmEta;   //!
   TBranch        *b_L1Extra_nonIsoEmPhi;   //!
   TBranch        *b_L1Extra_nonIsoEmBx;   //!
   TBranch        *b_L1Extra_nCenJets;   //!
   TBranch        *b_L1Extra_cenJetEt;   //!
   TBranch        *b_L1Extra_cenJetEta;   //!
   TBranch        *b_L1Extra_cenJetPhi;   //!
   TBranch        *b_L1Extra_cenJetBx;   //!
   TBranch        *b_L1Extra_nFwdJets;   //!
   TBranch        *b_L1Extra_fwdJetEt;   //!
   TBranch        *b_L1Extra_fwdJetEta;   //!
   TBranch        *b_L1Extra_fwdJetPhi;   //!
   TBranch        *b_L1Extra_fwdJetBx;   //!
   TBranch        *b_L1Extra_nTauJets;   //!
   TBranch        *b_L1Extra_tauJetEt;   //!
   TBranch        *b_L1Extra_tauJetEta;   //!
   TBranch        *b_L1Extra_tauJetPhi;   //!
   TBranch        *b_L1Extra_tauJetBx;   //!
   TBranch        *b_L1Extra_nMuons;   //!
   TBranch        *b_L1Extra_muonEt;   //!
   TBranch        *b_L1Extra_muonEta;   //!
   TBranch        *b_L1Extra_muonPhi;   //!
   TBranch        *b_L1Extra_muonChg;   //!
   TBranch        *b_L1Extra_muonIso;   //!
   TBranch        *b_L1Extra_muonFwd;   //!
   TBranch        *b_L1Extra_muonMip;   //!
   TBranch        *b_L1Extra_muonRPC;   //!
   TBranch        *b_L1Extra_muonBx;   //!
   TBranch        *b_L1Extra_muonQuality;   //!
   TBranch        *b_L1Extra_hfEtSum;   //!
   TBranch        *b_L1Extra_hfBitCnt;   //!
   TBranch        *b_L1Extra_hfBx;   //!
   TBranch        *b_L1Extra_nMet;   //!
   TBranch        *b_L1Extra_et;   //!
   TBranch        *b_L1Extra_met;   //!
   TBranch        *b_L1Extra_metPhi;   //!
   TBranch        *b_L1Extra_metBx;   //!
   TBranch        *b_L1Extra_nMht;   //!
   TBranch        *b_L1Extra_ht;   //!
   TBranch        *b_L1Extra_mht;   //!
   TBranch        *b_L1Extra_mhtPhi;   //!
   TBranch        *b_L1Extra_mhtBx;   //!

   L1ExtraTree(TString filename, TString directory, TTree *tree=0);
   virtual ~L1ExtraTree();
   virtual Int_t    GetEntry(Long64_t entry);
   virtual Long64_t LoadTree(Long64_t entry);
   virtual void     Init(TTree *tree);
   virtual void     Loop();
   virtual Bool_t   Notify();
   virtual void     Show(Long64_t entry = -1);
};

#endif