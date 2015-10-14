#include "L1GenericTree.cc"

#include "L1Trigger/L1TNtuples/interface/L1AnalysisL1UpgradeDataFormat.h"
#include "L1Trigger/L1TNtuples/interface/L1AnalysisL1ExtraDataFormat.h"

// declare any specialisations here

template class L1GenericTree<L1Analysis::L1AnalysisL1ExtraDataFormat>;
template class L1GenericTree<L1Analysis::L1AnalysisL1UpgradeDataFormat>;