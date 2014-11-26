// #define L1ExtraTree_cxx
#include "L1ExtraTree.h"
#include <TH2.h>
#include <TStyle.h>
#include <TCanvas.h>


L1ExtraTree::L1ExtraTree(TString filename, TString directory, TTree *tree) : fChain(0)
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
// Read contents of entry.
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
