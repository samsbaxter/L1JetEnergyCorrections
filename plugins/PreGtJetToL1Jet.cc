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

#include "CondFormats/L1TObjects/interface/L1CaloGeometry.h"
#include "CondFormats/DataRecord/interface/L1CaloGeometryRecord.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "DataFormats/L1Trigger/interface/L1JetParticle.h"
#include "DataFormats/L1Trigger/interface/L1JetParticleFwd.h"

#include "DataFormats/L1GlobalCaloTrigger/interface/L1GctCollections.h"
#include "DataFormats/L1Trigger/interface/Jet.h"


#include "CondFormats/L1TObjects/interface/L1CaloEtScale.h"
#include "CondFormats/DataRecord/interface/L1JetEtScaleRcd.h"
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
        math::PtEtaPhiMLorentzVector JetToLorentzVector(
            const l1t::Jet& jet,
            const L1CaloGeometry& geom,
            const L1CaloEtScale& scale);

        // virtual void beginJob() override;
        // virtual void endJob() override;
        //virtual void beginRun(edm::Run const&, edm::EventSetup const&) override;
        //virtual void endRun(edm::Run const&, edm::EventSetup const&) override;
        //virtual void beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&) override;
        //virtual void endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&) override;

        // ----------member data ---------------------------
        const edm::InputTag preGtJetSource_;
        edm::EDGetTokenT<l1t::JetBxCollection> preGtJetToken_;
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
PreGtJetToL1Jet::PreGtJetToL1Jet(const edm::ParameterSet& iConfig)
    : preGtJetSource_( iConfig.getParameter< edm::InputTag >("preGtJetSource") )
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
    using namespace l1extra ;
    using namespace std ;

    ESHandle< L1CaloGeometry > caloGeomESH ;
    iSetup.get< L1CaloGeometryRecord >().get( caloGeomESH ) ;
    const L1CaloGeometry* caloGeom = &( *caloGeomESH ) ;

    ESHandle< L1CaloEtScale > jetScale ;
    iSetup.get< L1JetEtScaleRcd >().get( jetScale ) ;

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
        // Loop over each obj, make a L1JetParticle obj from it
        l1t::JetBxCollection::const_iterator jetItr = preGtJetCollection->begin(itBX);
        l1t::JetBxCollection::const_iterator jetEnd = preGtJetCollection->end(itBX);
        for( ; jetItr != jetEnd ; ++jetItr) {
            if (jetItr->et() != 0) {
                // cout << "Jet: " << jetItr->bx() << " : " << jetItr->rank() << " : " << jetScale->et(jetItr->rank()) << " : " << jetItr->et() << " : "  << jetItr->eta() << " : " << jetItr->phi() << endl;
                jetColl->push_back(
                    L1JetParticle(JetToLorentzVector(*jetItr, *caloGeom, *jetScale),
                                  L1JetParticle::JetType::kUndefined,
                                  itBX)
                    );
            }
        }
    }

    OrphanHandle< L1JetParticleCollection > preGtJetHandle = iEvent.put(jetColl, "PreGtJets");
}

/**
 * @brief Converts info in Jet to LorentzVector
 * @details [long description]
 *
 * @param jet Input Jet
 * @param geom L1CaloGeometry to convert eta and phi into physical values
 * @param scale L1CaloEtScale to convert jet rank into physical ET
 * @return PolarLorentzVector (aka math::PtEtaPhiMLorentzVector) to use in L1JetParticle ctor
 */
math::PtEtaPhiMLorentzVector
PreGtJetToL1Jet::JetToLorentzVector(const l1t::Jet& jet,
                                   const L1CaloGeometry& geom,
                                   const L1CaloEtScale& scale) {
    double et = jet.et();
    double eta = jet.eta();
    double phi = jet.phi();
    // double et2 = jet.hwPt() * scale.linearLsb(); // pre calibration + compression
    // double eta2 = geom.etaBinCenter(jet.regionId());
    // double phi2 = geom.emJetPhiBinCenter(jet.regionId());
    double mass = 0.;
    // std::cout << et << " : "  << eta << " : " << phi << std::endl;
    // std::cout << et2 << " : "  << eta2 << " : " << phi2 << std::endl;
    return math::PtEtaPhiMLorentzVector(et, eta, phi, mass);
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
  descriptions.add("PreGtJetToL1Jet", desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(PreGtJetToL1Jet);
