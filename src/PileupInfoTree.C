#include <iostream>
#include <stdexcept>
#include <TH2.h>
#include <TStyle.h>
#include <TCanvas.h>
#include "PileupInfoTree.h"

using std::cout;
using std::endl;


PileupInfoTree::PileupInfoTree(TString filename, TString directory, TString treeName, TTree *tree) :
    fChain(0),
    b_TrueNumInteractions(0),
    b_NumPUVertices(0)
{
// if parameter tree is not specified (or zero), connect the file
// used to generate this class and read the Tree.
    if (tree == 0) {
        TFile *f = (TFile*)gROOT->GetListOfFiles()->FindObject(filename);
        if (!f || !f->IsOpen()) {
            f = new TFile(filename);
        }
        if (f->IsZombie()) throw std::runtime_error(("Couldn't open file"+filename).Data());
        TDirectory * dir = (TDirectory*)f->Get(filename+":/"+directory);
        if (!dir) {
            throw std::runtime_error(("Couldn't open "+filename+":/"+directory).Data());
        }
        dir->GetObject(treeName, tree);
        if(!tree) {
            throw std::runtime_error(("Couldn't open tree "+treeName).Data());
        }
        cout << "Opened " << treeName << " in " << filename << ":/" << directory << endl;


    }
    Init(tree);
}


PileupInfoTree::~PileupInfoTree()
{
    if (!fChain) return;
    delete fChain->GetCurrentFile();
}


Int_t PileupInfoTree::GetEntry(Long64_t entry)
{
// Read contents of entry.
    if (!fChain) return 0;
    return fChain->GetEntry(entry);
}


Long64_t PileupInfoTree::LoadTree(Long64_t entry)
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


void PileupInfoTree::Init(TTree *tree)
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

    fChain->SetBranchAddress("TrueNumInteractions", &TrueNumInteractions, &b_TrueNumInteractions);
    fChain->SetBranchAddress("NumPUVertices", &NumPUVertices, &b_NumPUVertices);
    Notify();
}


Bool_t PileupInfoTree::Notify()
{
    // The Notify() function is called when a new file is opened. This
    // can be either for a new TTree in a TChain or when when a new TTree
    // is started when using PROOF. It is normally not necessary to make changes
    // to the generated code, but the routine can be extended by the
    // user if needed. The return value is currently not used.

    return kTRUE;
}


void PileupInfoTree::Show(Long64_t entry)
{
// Print contents of entry.
// If entry is not specified, print current entry
    if (!fChain) return;
    fChain->Show(entry);
}
