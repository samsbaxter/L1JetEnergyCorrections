//////////////////////////////////////////////////////////
// This class has been automatically generated on
// Fri Jul  3 01:05:08 2015 by ROOT version 6.02/05
// from TTree PileupInfo/PileupInfo
// found on file: L1Tree_GCT_MCRUN2_74_V8_rerunRCT_newRCTv2.root
//////////////////////////////////////////////////////////

#ifndef PileupInfoTree_h
#define PileupInfoTree_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>
// Header file for the classes stored in the TTree if any.

class PileupInfoTree {
public :
    TTree          *fChain;   //!pointer to the analyzed TTree or TChain
    Int_t           fCurrent; //!current Tree number in a TChain

// Fixed size dimensions of array or collections stored in the TTree if any.

    // Declaration of leaf types
    Float_t         TrueNumInteractions;
    Int_t           NumPUVertices;

    // List of branches
    TBranch        *b_TrueNumInteractions;   //!
    TBranch        *b_NumPUVertices;   //!

    PileupInfoTree(TString filename, TString directory="puInfo", TString treeName="PileupInfo", TTree *tree=0);
    virtual ~PileupInfoTree();
    virtual Int_t    GetEntry(Long64_t entry);
    virtual Long64_t LoadTree(Long64_t entry);
    virtual void     Init(TTree *tree);
    virtual Bool_t   Notify();
    virtual void     Show(Long64_t entry = -1);

    /**
     * @brief Returns the "actual" number of simultaneous interactions - as pulled
     * from a Poisson prob. distr. fn, with mean = TrueNumInteractions
     * @return [description]
     */
    virtual float    numPUVertices() { return NumPUVertices; };

    /**
     * @brief Return the "true" number of simultaneous interactions - the number
     * that is the mean of POisson distribution
     * @details [long description]
     * @details [long description]
     * @return [description]
     */
    virtual float    trueNumInteractions() { return TrueNumInteractions; };

};

#endif
