// #define L1ExtraTree_cxx
#include <iostream>
#include <stdexcept>
#include <TH2.h>
#include <TStyle.h>
#include <TCanvas.h>
#include <TLeaf.h>
#include <TBranch.h>
#include "L1ExtraTree.h"


L1ExtraTree::L1ExtraTree(TString filename, TString directory, TTree *tree) :
   fChain(0),
   b_L1Extra_nIsoEm(0),
   b_L1Extra_isoEmEt(0),
   b_L1Extra_isoEmEta(0),
   b_L1Extra_isoEmPhi(0),
   b_L1Extra_isoEmBx(0),
   b_L1Extra_nNonIsoEm(0),
   b_L1Extra_nonIsoEmEt(0),
   b_L1Extra_nonIsoEmEta(0),
   b_L1Extra_nonIsoEmPhi(0),
   b_L1Extra_nonIsoEmBx(0),
   b_L1Extra_nCenJets(0),
   b_L1Extra_cenJetEt(0),
   b_L1Extra_cenJetEta(0),
   b_L1Extra_cenJetPhi(0),
   b_L1Extra_cenJetBx(0),
   b_L1Extra_nFwdJets(0),
   b_L1Extra_fwdJetEt(0),
   b_L1Extra_fwdJetEta(0),
   b_L1Extra_fwdJetPhi(0),
   b_L1Extra_fwdJetBx(0),
   b_L1Extra_nTauJets(0),
   b_L1Extra_tauJetEt(0),
   b_L1Extra_tauJetEta(0),
   b_L1Extra_tauJetPhi(0),
   b_L1Extra_tauJetBx(0),
   b_L1Extra_nMuons(0),
   b_L1Extra_muonEt(0),
   b_L1Extra_muonEta(0),
   b_L1Extra_muonPhi(0),
   b_L1Extra_muonChg(0),
   b_L1Extra_muonIso(0),
   b_L1Extra_muonFwd(0),
   b_L1Extra_muonMip(0),
   b_L1Extra_muonRPC(0),
   b_L1Extra_muonBx(0),
   b_L1Extra_muonQuality(0),
   b_L1Extra_hfEtSum(0),
   b_L1Extra_hfBitCnt(0),
   b_L1Extra_hfBx(0),
   b_L1Extra_nMet(0),
   b_L1Extra_et(0),
   b_L1Extra_met(0),
   b_L1Extra_metPhi(0),
   b_L1Extra_metBx(0),
   b_L1Extra_nMht(0),
   b_L1Extra_ht(0),
   b_L1Extra_mht(0),
   b_L1Extra_mhtPhi(0),
   b_L1Extra_mhtBx(0)
{
// if parameter tree is not specified (or zero), connect the file
// used to generate this class and read the Tree.
   if (tree == 0) {
      TFile *f = (TFile*)gROOT->GetListOfFiles()->FindObject(filename);
      if (!f || !f->IsOpen()) {
         f = new TFile(filename);
      }
      TDirectory * dir = (TDirectory*)f->Get(filename+":/"+directory);
      dir->GetObject("L1ExtraTree",tree);

   }
   Init(tree);
}


L1ExtraTree::~L1ExtraTree()
{
   if (!fChain) return;
   delete fChain->GetCurrentFile();
}


Int_t L1ExtraTree::GetEntry(Long64_t entry)
{
   if (!fChain) return 0;
   return fChain->GetEntry(entry);
}


Long64_t L1ExtraTree::LoadTree(Long64_t entry)
{
// Set the environment to read one entry
   if (!fChain) return -5;
   Long64_t centry = fChain->LoadTree(entry);
   if (centry < 0) return centry;
   if (fChain->GetTreeNumber() != fCurrent) {
      fCurrent = fChain->GetTreeNumber();
      Notify();
   }
   return centry;
}


void L1ExtraTree::Init(TTree *tree)
{
   // The Init() function is called when the selector needs to initialize
   // a new tree or chain. Typically here the branch addresses and branch
   // pointers of the tree will be set.
   // It is normally not necessary to make changes to the generated
   // code, but the routine can be extended by the user if needed.
   // Init() will be called many times when running on PROOF
   // (once per file to be processed).

   // Set branch addresses and branch pointers
   if (!tree) return;
   fChain = tree;
   fCurrent = -1;
   fChain->SetMakeClass(1);

   fChain->SetBranchAddress("nIsoEm", &nIsoEm, &b_L1Extra_nIsoEm);
   fChain->SetBranchAddress("isoEmEt", &isoEmEt, &b_L1Extra_isoEmEt);
   fChain->SetBranchAddress("isoEmEta", &isoEmEta, &b_L1Extra_isoEmEta);
   fChain->SetBranchAddress("isoEmPhi", &isoEmPhi, &b_L1Extra_isoEmPhi);
   fChain->SetBranchAddress("isoEmBx", &isoEmBx, &b_L1Extra_isoEmBx);
   fChain->SetBranchAddress("nNonIsoEm", &nNonIsoEm, &b_L1Extra_nNonIsoEm);
   fChain->SetBranchAddress("nonIsoEmEt", &nonIsoEmEt, &b_L1Extra_nonIsoEmEt);
   fChain->SetBranchAddress("nonIsoEmEta", &nonIsoEmEta, &b_L1Extra_nonIsoEmEta);
   fChain->SetBranchAddress("nonIsoEmPhi", &nonIsoEmPhi, &b_L1Extra_nonIsoEmPhi);
   fChain->SetBranchAddress("nonIsoEmBx", &nonIsoEmBx, &b_L1Extra_nonIsoEmBx);
   fChain->SetBranchAddress("nCenJets", &nCenJets, &b_L1Extra_nCenJets);
   fChain->SetBranchAddress("cenJetEt", &cenJetEt, &b_L1Extra_cenJetEt);
   fChain->SetBranchAddress("cenJetEta", &cenJetEta, &b_L1Extra_cenJetEta);
   fChain->SetBranchAddress("cenJetPhi", &cenJetPhi, &b_L1Extra_cenJetPhi);
   fChain->SetBranchAddress("cenJetBx", &cenJetBx, &b_L1Extra_cenJetBx);
   fChain->SetBranchAddress("nFwdJets", &nFwdJets, &b_L1Extra_nFwdJets);
   fChain->SetBranchAddress("fwdJetEt", &fwdJetEt, &b_L1Extra_fwdJetEt);
   fChain->SetBranchAddress("fwdJetEta", &fwdJetEta, &b_L1Extra_fwdJetEta);
   fChain->SetBranchAddress("fwdJetPhi", &fwdJetPhi, &b_L1Extra_fwdJetPhi);
   fChain->SetBranchAddress("fwdJetBx", &fwdJetBx, &b_L1Extra_fwdJetBx);
   fChain->SetBranchAddress("nTauJets", &nTauJets, &b_L1Extra_nTauJets);
   fChain->SetBranchAddress("tauJetEt", &tauJetEt, &b_L1Extra_tauJetEt);
   fChain->SetBranchAddress("tauJetEta", &tauJetEta, &b_L1Extra_tauJetEta);
   fChain->SetBranchAddress("tauJetPhi", &tauJetPhi, &b_L1Extra_tauJetPhi);
   fChain->SetBranchAddress("tauJetBx", &tauJetBx, &b_L1Extra_tauJetBx);
   fChain->SetBranchAddress("nMuons", &nMuons, &b_L1Extra_nMuons);
   fChain->SetBranchAddress("muonEt", &muonEt, &b_L1Extra_muonEt);
   fChain->SetBranchAddress("muonEta", &muonEta, &b_L1Extra_muonEta);
   fChain->SetBranchAddress("muonPhi", &muonPhi, &b_L1Extra_muonPhi);
   fChain->SetBranchAddress("muonChg", &muonChg, &b_L1Extra_muonChg);
   fChain->SetBranchAddress("muonIso", &muonIso, &b_L1Extra_muonIso);
   fChain->SetBranchAddress("muonFwd", &muonFwd, &b_L1Extra_muonFwd);
   fChain->SetBranchAddress("muonMip", &muonMip, &b_L1Extra_muonMip);
   fChain->SetBranchAddress("muonRPC", &muonRPC, &b_L1Extra_muonRPC);
   fChain->SetBranchAddress("muonBx", &muonBx, &b_L1Extra_muonBx);
   fChain->SetBranchAddress("muonQuality", &muonQuality, &b_L1Extra_muonQuality);
   fChain->SetBranchAddress("hfEtSum", &hfEtSum, &b_L1Extra_hfEtSum);
   fChain->SetBranchAddress("hfBitCnt", &hfBitCnt, &b_L1Extra_hfBitCnt);
   fChain->SetBranchAddress("hfBx", &hfBx, &b_L1Extra_hfBx);
   fChain->SetBranchAddress("nMet", &nMet, &b_L1Extra_nMet);
   fChain->SetBranchAddress("et", &et, &b_L1Extra_et);
   fChain->SetBranchAddress("met", &met, &b_L1Extra_met);
   fChain->SetBranchAddress("metPhi", &metPhi, &b_L1Extra_metPhi);
   fChain->SetBranchAddress("metBx", &metBx, &b_L1Extra_metBx);
   fChain->SetBranchAddress("nMht", &nMht, &b_L1Extra_nMht);
   fChain->SetBranchAddress("ht", &ht, &b_L1Extra_ht);
   fChain->SetBranchAddress("mht", &mht, &b_L1Extra_mht);
   fChain->SetBranchAddress("mhtPhi", &mhtPhi, &b_L1Extra_mhtPhi);
   fChain->SetBranchAddress("mhtBx", &mhtBx, &b_L1Extra_mhtBx);
   Notify();
}


Bool_t L1ExtraTree::Notify()
{
   // The Notify() function is called when a new file is opened. This
   // can be either for a new TTree in a TChain or when when a new TTree
   // is started when using PROOF. It is normally not necessary to make changes
   // to the generated code, but the routine can be extended by the
   // user if needed. The return value is currently not used.

   return kTRUE;
}


void L1ExtraTree::Show(Long64_t entry)
{
// Print contents of entry.
// If entry is not specified, print current entry
   if (!fChain) return;
   fChain->Show(entry);
}


void L1ExtraTree::Loop()
{
//   In a ROOT session, you can do:
//      Root > .L L1ExtraTree.C
//      Root > L1ExtraTree t
//      Root > t.GetEntry(12); // Fill t data members with entry number 12
//      Root > t.Show();       // Show values of entry 12
//      Root > t.Show(16);     // Read and show values of entry 16
//      Root > t.Loop();       // Loop on all entries
//

//     This is the loop skeleton where:
//    jentry is the global entry number in the chain
//    ientry is the entry number in the current Tree
//  Note that the argument to GetEntry must be:
//    jentry for TChain::GetEntry
//    ientry for TTree::GetEntry and TBranch::GetEntry
//
//       To read only selected branches, Insert statements like:
// METHOD1:
//    fChain->SetBranchStatus("*",0);  // disable all branches
//    fChain->SetBranchStatus("branchname",1);  // activate branchname
// METHOD2: replace line
//    fChain->GetEntry(jentry);       //read all branches
//by  b_branchname->GetEntry(ientry); //read only this branch
   if (fChain == 0) return;

   Long64_t nentries = fChain->GetEntriesFast();

   Long64_t nbytes = 0, nb = 0;
   for (Long64_t jentry=0; jentry<nentries;jentry++) {
      Long64_t ientry = LoadTree(jentry);
      if (ientry < 0) break;
      nb = fChain->GetEntry(jentry);   nbytes += nb;
   }
}


std::vector<TLorentzVector> L1ExtraTree::makeTLorentzVectors(TString branchName) const {
   // Make vector of TLorentzVectors from branches

   TString etBranchName  = branchName+"Et";
   TString etaBranchName = branchName+"Eta";
   TString phiBranchName = branchName+"Phi";

   // make sure we have et, eta & phi for this branch
   if (fChain->GetBranch(etBranchName)
   && fChain->GetBranch(etaBranchName)
   && fChain->GetBranch(phiBranchName)) {

      // This is so crazy. To get the value from a TBranch, I have to first assign a
      // variable to it. But we don't want to overide the class member variables,
      // so instead we create new ones, and manually assign addresses.
      // I'm basically doing fCahin->SetBranchAddress again...
      const vector<double> &et  = *(vector<double>*)fChain->GetBranch(etBranchName)->GetAddress();
      const vector<double> &eta = *(vector<double>*)fChain->GetBranch(etaBranchName)->GetAddress();
      const vector<double> &phi = *(vector<double>*)fChain->GetBranch(phiBranchName)->GetAddress();

      std::vector<TLorentzVector> vecs;
      for (unsigned i = 0; i < et.size(); ++i) {
         TLorentzVector v;
         v.SetPtEtaPhiM(et[i], eta[i], phi[i], 0.);
         vecs.push_back(v);
         // v.Print();
      }
      return vecs;
   } else {
      throw invalid_argument(std::string("You cannot make TLorentzVectors from branchName: ") + branchName.Data());
   }
}
