#include "L1UpgradeTree.h"
#include <stdexcept>


L1UpgradeTree::L1UpgradeTree(TString filename, TString treeName):
  treeName_(treeName)
{
  chain_ = new TChain(treeName_);
  l1Upgrade_ = new L1Analysis::L1AnalysisL1UpgradeDataFormat();
  addFile(filename);
  chain_->SetBranchAddress("L1Upgrade", &l1Upgrade_);
}


L1UpgradeTree::~L1UpgradeTree()
{
  if (chain_) delete chain_;
  if (l1Upgrade_) delete l1Upgrade_;
}


void L1UpgradeTree::addFile(TString filename) {
  int addResult = chain_->Add(filename, -1);
  if (addResult == 0) {
    throw std::runtime_error(("Couldn't get " + treeName_ + " from " + filename).Data());
  }
  cout << "Opened " << treeName_ << " in " << filename << endl;
}


Long64_t L1UpgradeTree::getEntry(Long64_t iEntry) {
  Long64_t cEntry = chain_->LoadTree(iEntry);
  if (cEntry < 0)
    return cEntry;
  return chain_->GetEntry(iEntry);
}
