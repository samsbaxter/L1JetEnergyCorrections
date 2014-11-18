#include <iostream>
#include <memory>

#include <cppunit/TestFixture.h>
#include <cppunit/extensions/TestFactoryRegistry.h>
#include <cppunit/ui/text/TestRunner.h>
#include <cppunit/CompilerOutputter.h>
#include <cppunit/TestCase.h>
#include <cppunit/extensions/HelperMacros.h>

#include "TLorentzVector.h"
#include "DeltaR_Matcher.h"

/**
 * @brief Unit tests for Matcher class & subclasses
 * @details To build and run, do:
 * scram b runtests
 */
class MatcherUnitTest : public CppUnit::TestCase {

    /**
     * CppUnit provides a TestSuite class that runs any number of TestCases together.
     * In this case, you'll want your test class to inherit from CppUnit::TestFixture
     *
     * These macros saves a lot of typing - basically registers a TestSuite, and
     * attaches tests to suite.
     *
     * Make sure you put these before the other function declarations, otherwise it'll
     * complain about setUp() being private.
     */
    CPPUNIT_TEST_SUITE( MatcherUnitTest );
    CPPUNIT_TEST( runSimpleMatch );
    CPPUNIT_TEST( checkMinPtMaxEta );
    CPPUNIT_TEST_SUITE_END();

public:
    MatcherUnitTest() {};

    void setUp();
    void tearDown();

    void runSimpleMatch();
    void checkMinPtMaxEta();

    // Utilities
    void cleanupObjects(DeltaR_Matcher *m,
                        std::vector<TLorentzVector> refJets,
                        std::vector<TLorentzVector> L1Jets,
                        std::vector<std::pair<TLorentzVector, TLorentzVector>> pairs);

    void cleanupObjects(DeltaR_Matcher *m,
                        std::vector<std::pair<TLorentzVector, TLorentzVector>> pairs);

private:
    std::vector<TLorentzVector> refJets;
    std::vector<TLorentzVector> L1Jets;
    DeltaR_Matcher * m;
};

// CPPUNIT_TEST_SUITE_NAMED_REGISTRATION( MatcherUnitTest, "MatcherUnitTest" );

/**
 * @brief Setup common objects used for tests
 */
void MatcherUnitTest::setUp() {
}


/**
 * @brief Destroy any common objects used for tests
 */
void MatcherUnitTest::tearDown() {
}


/**
 * @brief Runs simple matching test to ensure it should do the basics
 * @details Should match l1_1 with ref_1, etc. Done in all 4 quadrants of eta-phi space.
 * No min pT or max eta checks.
 */
void MatcherUnitTest::runSimpleMatch() {
    TLorentzVector l1_1; l1_1.SetPtEtaPhiM(40,1,0.5,0);
    TLorentzVector ref_1; ref_1.SetPtEtaPhiM(38,1.3,0.46,0);
    TLorentzVector l1_2; l1_2.SetPtEtaPhiM(40,1,-0.5,0);
    TLorentzVector ref_2; ref_2.SetPtEtaPhiM(38,1.3,-0.46,0);
    TLorentzVector l1_3; l1_3.SetPtEtaPhiM(40,-1,-0.5,0);
    TLorentzVector ref_3; ref_3.SetPtEtaPhiM(38,-1.3,-0.46,0);
    TLorentzVector l1_4; l1_4.SetPtEtaPhiM(40,-1,0.5,0);
    TLorentzVector ref_4; ref_4.SetPtEtaPhiM(38,-1.3,0.46,0);

    refJets = {ref_1, ref_2, ref_3, ref_4};
    L1Jets = {l1_1, l1_2, l1_3, l1_4};

    m = new DeltaR_Matcher(0.7);
    m->setRefJets(refJets);
    m->setL1Jets(L1Jets);
    m->printName();
    std::vector<std::pair<TLorentzVector, TLorentzVector>> pairs = m->produceMatchingPairs();
    // check we have 4 matching pairs & print out matches
    m->printMatches(pairs);
    CPPUNIT_ASSERT( pairs.size() == 4 );

    cleanupObjects(m, refJets, L1Jets, pairs);
}


/**
 * @brief Check that min pT cut works for ref & L1 jets, and max eta works for both
 * @details 4 pairs of jets that match in eta/phi, but should fail on min pT or max Eta
 */
void MatcherUnitTest::checkMinPtMaxEta() {
    TLorentzVector l1_1; l1_1.SetPtEtaPhiM(1.2,1,0.5,0); // fail min L1 jet pT
    TLorentzVector ref_1; ref_1.SetPtEtaPhiM(38,1.3,0.46,0);

    TLorentzVector l1_2; l1_2.SetPtEtaPhiM(40,1,-0.5,0);
    TLorentzVector ref_2; ref_2.SetPtEtaPhiM(1.2,1.3,-0.46,0); // fail min ref jet pT

    TLorentzVector l1_3; l1_3.SetPtEtaPhiM(40,-5.1,-1,0); // fail max L1 jet eta
    TLorentzVector ref_3; ref_3.SetPtEtaPhiM(38,-4.6,-1.2,0);

    TLorentzVector l1_4; l1_4.SetPtEtaPhiM(40,4.5,1.1,0);
    TLorentzVector ref_4; ref_4.SetPtEtaPhiM(38,5.1,1.2,0); // fail max ref jet Eta

    refJets = {ref_1, ref_2, ref_3, ref_4};
    L1Jets = {l1_1, l1_2, l1_3, l1_4};

    // test via constructor
    m = new DeltaR_Matcher(0.7, 3, 4, 5);
    m->setRefJets(refJets);
    m->setL1Jets(L1Jets);
    m->printName();
    std::vector<std::pair<TLorentzVector, TLorentzVector>> pairs = m->produceMatchingPairs();
    m->printMatches(pairs);
    CPPUNIT_ASSERT( pairs.size() == 0 );

    cleanupObjects(m, pairs);

    // test via setters
    m = new DeltaR_Matcher(0.7);
    m->setMinL1JetPt(1.5);
    m->setMinRefJetPt(1.5);
    m->setMaxJetEta(5);
    m->printName();
    pairs = m->produceMatchingPairs();
    m->printMatches(pairs);
    CPPUNIT_ASSERT( pairs.size() == 0 );

    cleanupObjects(m, refJets, L1Jets, pairs);
}



/**
 * @brief Cleanup Matcher, jet collections, and mathed pairs
 *
 * @param matcher Matcher
 * @param refJets Ref jet collection
 * @param L1Jets L1 jet collection
 * @param pairs Matched pairs
 */
void MatcherUnitTest::cleanupObjects(DeltaR_Matcher *matcher,
                                    std::vector<TLorentzVector> refJets,
                                    std::vector<TLorentzVector> L1Jets,
                                    std::vector<std::pair<TLorentzVector, TLorentzVector>> pairs) {
    if (matcher != nullptr) delete matcher;
    if (refJets.size() != 0) refJets.clear();
    if (L1Jets.size() != 0) L1Jets.clear();
    if (pairs.size() != 0) pairs.clear();
}


/**
 * @brief Cleanup Matcher and matched pairs
 *
 * @param matcher Matcher pointer
 * @param pairs Vector of pairs
 */
void MatcherUnitTest::cleanupObjects(DeltaR_Matcher *matcher,
                                     std::vector<std::pair<TLorentzVector, TLorentzVector>> pairs) {
    if (matcher != nullptr) delete matcher;
    if (pairs.size() != 0) pairs.clear();
}


/**
 * @brief Main routine that runs the tests and output the results to screen.
 */
int main() {
    /**
     * A TestRunner runs your tests and collects the results. It needs a
     * CppUnit::TestSuite, which your test class returns via static method suite. This
     * is all done via the macros used in the class above.
     */
    CppUnit::TextUi::TestRunner runner;
    runner.addTest( MatcherUnitTest::suite() );
    runner.run();
    return 0;

    // alternatively, to include in BuildProcess, have to return value
    // diff to 0 in event of Failure
    // bool wasSuccessful = runner.run("", false);
    // return !wasSuccessful;
}