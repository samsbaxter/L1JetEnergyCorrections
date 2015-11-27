#include "L1GenericTree.cc"

#include "L1Trigger/L1TNtuples/interface/L1AnalysisEventDataFormat.h"
#include "L1Trigger/L1TNtuples/interface/L1AnalysisCSCTFDataFormat.h"
#include "L1Trigger/L1TNtuples/interface/L1AnalysisDTTFDataFormat.h"
#include "L1Trigger/L1TNtuples/interface/L1AnalysisGCTDataFormat.h"
#include "L1Trigger/L1TNtuples/interface/L1AnalysisGMTDataFormat.h"
#include "L1Trigger/L1TNtuples/interface/L1AnalysisGTDataFormat.h"
#include "L1Trigger/L1TNtuples/interface/L1AnalysisRCTDataFormat.h"
#include "L1Trigger/L1TNtuples/interface/L1AnalysisCaloTPDataFormat.h"
#include "L1Trigger/L1TNtuples/interface/L1AnalysisGeneratorDataFormat.h"
#include "L1Trigger/L1TNtuples/interface/L1AnalysisSimulationDataFormat.h"
#include "L1Trigger/L1TNtuples/interface/L1AnalysisL1ExtraDataFormat.h"
#include "L1Trigger/L1TNtuples/interface/L1AnalysisRecoMuonDataFormat.h"
#include "L1Trigger/L1TNtuples/interface/L1AnalysisRecoRpcHitDataFormat.h"
#include "L1Trigger/L1TNtuples/interface/L1AnalysisRecoMetDataFormat.h"
#include "L1Trigger/L1TNtuples/interface/L1AnalysisRecoJetDataFormat.h"
#include "L1Trigger/L1TNtuples/interface/L1AnalysisRecoClusterDataFormat.h"
#include "L1Trigger/L1TNtuples/interface/L1AnalysisRecoVertexDataFormat.h"
#include "L1Trigger/L1TNtuples/interface/L1AnalysisRecoTrackDataFormat.h"
#include "L1Trigger/L1TNtuples/interface/L1AnalysisL1MenuDataFormat.h"
#include "L1Trigger/L1TNtuples/interface/L1AnalysisL1UpgradeDataFormat.h"
#include "L1Trigger/L1TNtuples/interface/L1AnalysisL1CaloTowerDataFormat.h"

#include "L1Trigger/L1TNtuples/interface/L1AnalysisRecoTauDataFormat.h"
#include "L1Trigger/L1TNtuples/interface/L1AnalysisRecoMuon2DataFormat.h"
#include "L1Trigger/L1TNtuples/interface/L1AnalysisRecoElectronDataFormat.h"

// declare any specialisations here
template class L1GenericTree<L1Analysis::L1AnalysisEventDataFormat>;
template class L1GenericTree<L1Analysis::L1AnalysisCSCTFDataFormat>;
template class L1GenericTree<L1Analysis::L1AnalysisDTTFDataFormat>;
template class L1GenericTree<L1Analysis::L1AnalysisGCTDataFormat>;
template class L1GenericTree<L1Analysis::L1AnalysisGMTDataFormat>;
template class L1GenericTree<L1Analysis::L1AnalysisGTDataFormat>;
template class L1GenericTree<L1Analysis::L1AnalysisRCTDataFormat>;
template class L1GenericTree<L1Analysis::L1AnalysisCaloTPDataFormat>;
template class L1GenericTree<L1Analysis::L1AnalysisGeneratorDataFormat>;
template class L1GenericTree<L1Analysis::L1AnalysisSimulationDataFormat>;
template class L1GenericTree<L1Analysis::L1AnalysisL1ExtraDataFormat>;
template class L1GenericTree<L1Analysis::L1AnalysisRecoMuonDataFormat>;
template class L1GenericTree<L1Analysis::L1AnalysisRecoRpcHitDataFormat>;
template class L1GenericTree<L1Analysis::L1AnalysisRecoMetDataFormat>;
template class L1GenericTree<L1Analysis::L1AnalysisRecoJetDataFormat>;
template class L1GenericTree<L1Analysis::L1AnalysisRecoClusterDataFormat>;
template class L1GenericTree<L1Analysis::L1AnalysisRecoVertexDataFormat>;
template class L1GenericTree<L1Analysis::L1AnalysisRecoTrackDataFormat>;
template class L1GenericTree<L1Analysis::L1AnalysisL1MenuDataFormat>;
template class L1GenericTree<L1Analysis::L1AnalysisL1UpgradeDataFormat>;
template class L1GenericTree<L1Analysis::L1AnalysisL1CaloTowerDataFormat>;
template class L1GenericTree<L1Analysis::L1AnalysisRecoTauDataFormat>;
template class L1GenericTree<L1Analysis::L1AnalysisRecoMuon2DataFormat>;
template class L1GenericTree<L1Analysis::L1AnalysisRecoElectronDataFormat>;