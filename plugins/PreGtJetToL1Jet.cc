// -*- C++ -*-
//
// Package:    L1Trigger/L1JetEnergyCorrections
// Class:      PreGtJetToL1Jet
// 
/**\class PreGtJetToL1Jet PreGtJetToL1Jet.cc L1Trigger/L1JetEnergyCorrections/plugins/PreGtJetToL1Jet.cc

 Description: EDProducer to turn preGtJets (as JetBxCollection i.e. BXVector<Jet>) into L1JetParticles.
 Output can then be passed into l1ExtraTreeProducer.

 Implementation:
      Fairly simple - get pre GT jet collection, loop through it, and for each jet create a L1JetParticle using
      info from the Jet obj and then store the L1JetParticle in a collection, which will be added to output.
*/
//
// Original Author:  Robin Cameron Aggleton
//         Created:  Wed, 19 Nov 2014 22:13:47 GMT
//
//


// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDProducer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "DataFormats/Common/interface/Handle.h"
#include "FWCore/Framework/interface/ESHandle.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "DataFormats/L1Trigger/interface/L1JetParticle.h"
#include "DataFormats/L1Trigger/interface/L1JetParticleFwd.h"
#include "DataFormats/L1Trigger/interface/Jet.h"


//
// class declaration
//

class PreGtJetToL1Jet : public edm::EDProducer {
    public:
        explicit PreGtJetToL1Jet(const edm::ParameterSet&);
        ~PreGtJetToL1Jet();

        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

    private:
        virtual void produce(edm::Event&, const edm::EventSetup&) override;

        // virtual void beginJob() override;
        // virtual void endJob() override;
        //virtual void beginRun(edm::Run const&, edm::EventSetup const&) override;
        //virtual void endRun(edm::Run const&, edm::EventSetup const&) override;
        //virtual void beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&) override;
        //virtual void endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&) override;

        virtual math::PtEtaPhiMLorentzVector l1JetToLorentzVector(int hwPt, int hwEta, int hwPhi) ;
        virtual double trigTowerToEta(int hwEta);

        // ----------member data ---------------------------
        const edm::InputTag preGtJetSource_;
        edm::EDGetTokenT<l1t::JetBxCollection> preGtJetToken_;
        const bool useHwValues_;
        const double jetLsb_;
};

//
// constants, enums and typedefs
//


//
// static data member definitions
//

//
// constructors and destructor
//
PreGtJetToL1Jet::PreGtJetToL1Jet(const edm::ParameterSet& iConfig):
    preGtJetSource_(iConfig.getParameter<edm::InputTag>("preGtJetSource")),
    useHwValues_(iConfig.getParameter<bool>("useHwValues")),
    jetLsb_(iConfig.getParameter<double>("jetLsb"))
{
    using namespace l1extra ;

    //register your products
    produces<L1JetParticleCollection>("PreGtJets");

    //now do what ever other initialization is needed
    preGtJetToken_ = consumes<l1t::JetBxCollection>(preGtJetSource_);

}


PreGtJetToL1Jet::~PreGtJetToL1Jet()
{
 
    // do anything here that needs to be done at desctruction time
    // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called to produce the data  ------------
/**
 * @brief Produces L1JetParticleCollection from JetBxCollection
 * @details [long description]
 *
 * @param iEvent [description]
 * @param iSetup [description]
 */
void
PreGtJetToL1Jet::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
    using namespace edm;
    using namespace l1extra;
    using namespace std;

    // Get the JetBxCollection
    Handle<l1t::JetBxCollection> preGtJetCollection;
    iEvent.getByToken(preGtJetToken_, preGtJetCollection);
    if (!preGtJetCollection.isValid()) {
        throw cms::Exception("ProductNotValid") << "preGtJetSource not valid";
    }

    auto_ptr< L1JetParticleCollection > jetColl( new L1JetParticleCollection );

    // Loop over BX
    int firstBX = preGtJetCollection->getFirstBX();
    int lastBX = preGtJetCollection->getLastBX();

    for (int itBX = firstBX; itBX!=lastBX+1; ++itBX) {
        // Loop over each obj, make a l1extra::L1JetParticle obj from it
        l1t::JetBxCollection::const_iterator jetItr = preGtJetCollection->begin(itBX);
        l1t::JetBxCollection::const_iterator jetEnd = preGtJetCollection->end(itBX);
        for( ; jetItr != jetEnd ; ++jetItr) {
            if (useHwValues_) {
                // get pt, eta, phi from HW values - need to convert.
                math::PtEtaPhiMLorentzVector fourMom = l1JetToLorentzVector(jetItr->hwPt(), jetItr->hwEta(), jetItr->hwPhi());
                L1JetParticle::JetType jetStatus = L1JetParticle::JetType::kCentral;
                if (abs(fourMom.eta()) > 3) {
                    jetStatus = L1JetParticle::JetType::kForward;
                }
                jetColl->push_back(L1JetParticle(fourMom, jetStatus, itBX));
            } else {
                // use 4 momentum already stored in the object
                if (jetItr->et() != 0) {
                    L1JetParticle::JetType jetStatus = L1JetParticle::JetType::kCentral;
                    if (abs(jetItr->p4().eta()) > 3) {
                        jetStatus = L1JetParticle::JetType::kForward;
                    }
                    jetColl->push_back(L1JetParticle(jetItr->p4(), jetStatus, itBX));
                }
            }
        }
    }

    OrphanHandle< L1JetParticleCollection > preGtJetHandle = iEvent.put(jetColl, "PreGtJets");
}

/**
 * @brief Convert trigger tower (TT) number (aka iEta) to physical eta
 * @details Returns physical eta corresponding to centre of each trigger tower.
 * So tower 1 => 0.087 / 2 = 0.0435
 *
 * @param hwEta Hardware eta (iEta), ranges from -32 to + 32
 * @return Physical eta, at the centre of each trigger tower.
 */
double
PreGtJetToL1Jet::trigTowerToEta(int hwEta)
{
    double eta = 0.;
    if (abs(hwEta) <= 20) {
        // Up to the split HE, TT: 1 - 20, eta: 0 - 1.74. Each TT has dEta = 0.087.
        eta = (abs(hwEta) - .5) * 0.087;
    } else if (abs(hwEta) <= 28) {
        // Split HE, TT: 21 - 28, eta: 1.74 - 3. Towers have non-uniform segmentation.
        double etaEdges [] = {1.74, 1.83, 1.93, 2.043, 2.172, 2.322, 2.5, 2.65, 3};
        eta = 0.5 * (etaEdges[abs(hwEta)-20] + etaEdges[abs(hwEta)-21]);
    } else {
        // HF, TT: 29 - 32, Eta: 3 - 5. Each tower has dEta = 0.5
        eta = ((abs(hwEta) - 29) * 0.5) + 3.25;
    }
    int sign = (hwEta > 0) - (hwEta < 0);
    return eta * sign;
}


math::PtEtaPhiMLorentzVector
PreGtJetToL1Jet::l1JetToLorentzVector(int hwPt, int hwEta, int hwPhi)
{
    // get pt, eta, phi from HW values - need to convert.
    double pt = hwPt * jetLsb_;
    double eta = trigTowerToEta(hwEta);
    double phi = (hwPhi - 0.5) * 2 * M_PI / 72.;
    return math::PtEtaPhiMLorentzVector(pt, eta, phi, 0.);

}

// ------------ method called once each job just before starting event loop  ------------
/*
void 
PreGtJetToL1Jet::beginJob()
{
}
*/

// ------------ method called once each job just after ending the event loop  ------------
/*
void 
PreGtJetToL1Jet::endJob() {
}
*/

// ------------ method called when starting to processes a run  ------------
/*
void
PreGtJetToL1Jet::beginRun(edm::Run const&, edm::EventSetup const&)
{
}
*/
 
// ------------ method called when ending the processing of a run  ------------
/*
void
PreGtJetToL1Jet::endRun(edm::Run const&, edm::EventSetup const&)
{
}
*/
 
// ------------ method called when starting to processes a luminosity block  ------------
/*
void
PreGtJetToL1Jet::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}
*/
 
// ------------ method called when ending the processing of a luminosity block  ------------
/*
void
PreGtJetToL1Jet::endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}
*/
 
// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
PreGtJetToL1Jet::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  edm::ParameterSetDescription desc;
  desc.add<edm::InputTag>("preGtJetSource", edm::InputTag(""))->setComment("Name of module that produces JetBxCollection for preGtJets");
  desc.add<bool>("useHwValues")->setComment("Use jet hardware et/eta/phi. Otherwise use p4().");
  desc.add<double>("jetLsb")->setComment("LSB for jet et scale. Only used if useHwValues True.");
  descriptions.add("PreGtJetToL1Jet", desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(PreGtJetToL1Jet);
