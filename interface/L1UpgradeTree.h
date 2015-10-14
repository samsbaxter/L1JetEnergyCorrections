#ifndef L1UpgradeTree_h
#define L1UpgradeTree_h

#include <iostream>

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>
#include <TString.h>
#include <TTree.h>

// #include "L1Trigger/L1TNtuples/interface/L1AnalysisL1ExtraDataFormat.h"
#include "L1Trigger/L1TNtuples/interface/L1AnalysisL1UpgradeDataFormat.h"

using std::cout;
using std::endl;

class L1UpgradeTree {

  public:
    /**
     * @brief Constructor.
     * @details [long description]
     *
     * @param filename Name of ROOT file.
     * @param treeName Name of TTree in file, including all directories.
     * e.g. "l1UpgradeTreeProducer/L1UpgradeTree"
     */
    L1UpgradeTree(TString filename, TString treeName);

    /**
     * @brief Destructor
     */
    virtual ~L1UpgradeTree();

    /**
     * @brief Add a ROOT file to the TChain.
     * @details Must hae the same treeName as passed to the constructor.
     */
    void addFile(TString filename);

    /**
     * @brief Load the entry into memory
     * @details Attempts TChain::LoadTree() first then TChain::GetEntry().
     * The return value should be tested, since LoadTree() will return
     * [-1, -2, -3, -4] for various errors, whilst GetEntry() will return the
     * total number of bytes read, with 0 indicating failure.
     *
     * @return The value of TChain::LoadTree() if it is < 0, otherwise
     * the result of TChain::GetEntry(). 0 indicates failure.
     */
    Long64_t getEntry(Long64_t iEntry);

    /**
     * @brief Return the number of entries in the TChain
     * @return [description]
     */
    Long64_t getEntries() { return chain_->GetEntriesFast(); }

    /**
     * @brief Getter for the L1AnalysisL1UpgradeDataFormat object
     * @return [description]
     */
    L1Analysis::L1AnalysisL1UpgradeDataFormat * getData() { return l1Upgrade_; }

    /**
     * @brief Getter for the internal TChain
     * @return [description]
     */
    TChain * getTChain() { return chain_; }

  private:
    L1Analysis::L1AnalysisL1UpgradeDataFormat * l1Upgrade_;
    TChain * chain_;   //!<pointer to the analyzed TTree or TChain
    TString treeName_;
};

#endif