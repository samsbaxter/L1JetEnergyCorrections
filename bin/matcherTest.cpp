#include "DeltaR_Matcher.h"
#include <iostream>

int main() {
    std::cout << "Matching test" << std::endl;

    TLorentzVector ref1, ref2, ref3;
    TLorentzVector l11, l12, l13;
    ref1.SetPtEtaPhiE(10,0,0,10);
    ref2.SetPtEtaPhiE(12,0.1,0.1,12);
    ref3.SetPtEtaPhiE(15,0.21,0.21,15);
    std::vector<TLorentzVector> refJets = {ref1, ref2, ref3 };

    l11.SetPtEtaPhiE(10,0,0,10);
    l12.SetPtEtaPhiE(12,0.15,0.15,12);
    l13.SetPtEtaPhiE(15,0.25,0.25,15);
    std::vector<TLorentzVector> l1Jets = {l11, l12, l13 };

    DeltaR_Matcher * m = new DeltaR_Matcher(0.5);
    m->printName();
    m->setRefJets(refJets);
    m->setL1Jets(l1Jets);
    m->setMinRefJetPt(10);
    m->setMinL1JetPt(0);
    m->setMaxJetEta(5.0);
    std::vector<std::pair<TLorentzVector, TLorentzVector>> results = m->produceMatchingPairs();
    for (auto &it: results)
    {
        std::cout << "refjet: " ;
        it.first.Print() ;
        std::cout << " l1jet: " ;
        it.second.Print();
        std::cout << std::endl;
    }

    //@TODO Sort the input collections by?
}