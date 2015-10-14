#ifndef L1GenericTree_h
#define L1GenericTree_h

#include <iostream>

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>
#include <TString.h>
#include <TTree.h>

using std::cout;
using std::endl;

/**
 * @brief Templated class to provide a handy interface for acessing the info in
 * any L1Analysis*DataFormat object stored in the L1Ntuple.
 * @details The idea here is that you can use several instances of this object
 * to analyse only the parts of the L1Ntuple that you want to - nice and modular,
 * instead of having 1 heavy class.
 *
 * IMPORTANT: if you must ensure that your specialisation is added to
 * src/L1GenericTree-impl.cc, otherwise you will see undefined reference errors
 *
 * @tparam T [description]
 */
template <typename T>
class L1GenericTree {

  public:
    /**
     * @brief Constructor.
     * @details [long description]
     *
     * @param filename Name of ROOT file.
     * @param treeName Name of TTree in file, including all directories.
     * e.g. "l1ExtraTreeProducer/L1ExtraTree"
     * @param branchName Name of TBranch in file, e.g. "L1Extra".
     */
    L1GenericTree(TString filename, TString treeName, TString branchName);

    /**
     * @brief Destructor
     */
    virtual ~L1GenericTree();

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
     * @brief Getter for the T DataFormat object
     * @return [description]
     */
    T * getData() { return l1Data_; }

    /**
     * @brief Getter for the internal TChain
     * @return [description]
     */
    TChain * getTChain() { return chain_; }

  private:
    T * l1Data_;
    TChain * chain_;   //!<pointer to the analyzed TTree or TChain
    TString treeName_;
    TString branchName_;
};

#endif
