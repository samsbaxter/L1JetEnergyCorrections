#include "L1GenericTree.h"
#include <stdexcept>

template <typename T>
L1GenericTree<T>::L1GenericTree(TString filename, TString treeName, TString branchName):
  treeName_(treeName),
  branchName_(branchName)
{
  chain_ = new TChain(treeName_);
  l1Data_ = new T;
  addFile(filename);
  chain_->SetBranchAddress(branchName_, &l1Data_);
}


template <typename T>
L1GenericTree<T>::~L1GenericTree()
{
  if (chain_) delete chain_;
  if (l1Data_) delete l1Data_;
}


template <typename T>
void L1GenericTree<T>::addFile(TString filename) {
  int addResult = chain_->Add(filename, -1);
  if (addResult == 0) {
    throw std::runtime_error(("Couldn't get " + treeName_ + " from " + filename).Data());
  }
  cout << "Opened " << filename << ":/" << treeName_ << "/" << branchName_ << endl;
}


template<typename T>
Long64_t L1GenericTree<T>::getEntry(Long64_t iEntry) {
  Long64_t cEntry = chain_->LoadTree(iEntry);
  if (cEntry < 0)
    return cEntry;
  return chain_->GetEntry(iEntry);
}
