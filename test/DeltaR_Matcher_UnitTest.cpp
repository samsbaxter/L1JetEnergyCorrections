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
 * @brief Unit tests for DeltaR_Matcher class & subclasses
 * @details To build and run, do:
 * scram b runtests
 * To turn on/off print statments, change the printStatments bool in setUp()
 */
class DeltaR_Matcher_UnitTest : public CppUnit::TestCase {

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
    CPPUNIT_TEST_SUITE( DeltaR_Matcher_UnitTest );
    CPPUNIT_TEST( runSimpleMatch );
    CPPUNIT_TEST( checkMinPtMaxEta );
    CPPUNIT_TEST( checkDeltaRMax );
    CPPUNIT_TEST( checkPtOrdering );
    CPPUNIT_TEST( checkRefJetRemoval );
    CPPUNIT_TEST_SUITE_END();

public:
    DeltaR_Matcher_UnitTest() {};

    void setUp();
    void tearDown();

    // Tests
    void runSimpleMatch();
    void checkMinPtMaxEta();
    void checkDeltaRMax();
    void checkPtOrdering();
    void checkRefJetRemoval();

private:
    bool printStatements;
    std::vector<TLorentzVector> refJets;
    std::vector<TLorentzVector> L1Jets;
    DeltaR_Matcher * matcher;
    std::vector<std::pair<TLorentzVector, TLorentzVector>> pairs;
};

// CPPUNIT_TEST_SUITE_NAMED_REGISTRATION( DeltaR_Matcher_UnitTest, "DeltaR_Matcher_UnitTest" );

/**
 * @brief Setup common objects used for tests, at start of each CPPUNIT_TEST
 */
void DeltaR_Matcher_UnitTest::setUp() {
    printStatements = true;
}


/**
 * @brief Destroy any common objects used for tests, at end of each CPPUNIT_TEST
 */
void DeltaR_Matcher_UnitTest::tearDown() {
    if (matcher != nullptr) delete matcher;
    if (refJets.size() != 0) refJets.clear();
    if (L1Jets.size() != 0) L1Jets.clear();
    if (pairs.size() != 0) pairs.clear();
}


/**
 * @brief Runs simple matching test to ensure it should do the basics
 * @details Should match l1_1 with ref_1, etc. Done in all 4 quadrants of eta-phi space.
 * No min pT or max eta checks.
 */
void DeltaR_Matcher_UnitTest::runSimpleMatch() {
    TLorentzVector l1_1; l1_1.SetPtEtaPhiM(40, 1, 0.5, 0);
    TLorentzVector ref_1; ref_1.SetPtEtaPhiM(38, 1.3, 0.46, 0);
    TLorentzVector l1_2; l1_2.SetPtEtaPhiM(40, 1, -0.5, 0);
    TLorentzVector ref_2; ref_2.SetPtEtaPhiM(38, 1.3, -0.46, 0);
    TLorentzVector l1_3; l1_3.SetPtEtaPhiM(40, -1, -0.5, 0);
    TLorentzVector ref_3; ref_3.SetPtEtaPhiM(38, -1.3, -0.46, 0);
    TLorentzVector l1_4; l1_4.SetPtEtaPhiM(40, -1, 0.5, 0);
    TLorentzVector ref_4; ref_4.SetPtEtaPhiM(38, -1.3, 0.46, 0);

    refJets = {ref_1, ref_2, ref_3, ref_4};
    L1Jets = {l1_1, l1_2, l1_3, l1_4};

    matcher = new DeltaR_Matcher(0.7);
    matcher->setRefJets(refJets);
    matcher->setL1Jets(L1Jets);
    pairs = matcher->getMatchingPairs();
    // check we have 4 matching pairs & print out matches
    if (printStatements) {
        matcher->printName();
        matcher->printMatches();
    }
    CPPUNIT_ASSERT( pairs.size() == 4 );
    CPPUNIT_ASSERT( pairs[0].first == ref_1 );
    CPPUNIT_ASSERT( pairs[0].second == l1_1 );
    CPPUNIT_ASSERT( pairs[1].first == ref_2 );
    CPPUNIT_ASSERT( pairs[1].second == l1_2 );
    CPPUNIT_ASSERT( pairs[2].first == ref_3 );
    CPPUNIT_ASSERT( pairs[2].second == l1_3 );
    CPPUNIT_ASSERT( pairs[3].first == ref_4 );
    CPPUNIT_ASSERT( pairs[3].second == l1_4 );

}


/**
 * @brief Check that min pT cut works for ref & L1 jets, and max eta works for both
 * @details 4 pairs of jets that match in eta/phi, but should all fail on min pT or max Eta
 */
void DeltaR_Matcher_UnitTest::checkMinPtMaxEta() {
    TLorentzVector l1_1; l1_1.SetPtEtaPhiM(1.2, 1, 0.5, 0); // fail min L1 jet pT
    TLorentzVector ref_1; ref_1.SetPtEtaPhiM(38, 1.3, 0.46, 0);

    TLorentzVector l1_2; l1_2.SetPtEtaPhiM(40, 1, -0.5, 0);
    TLorentzVector ref_2; ref_2.SetPtEtaPhiM(1.2, 1.3, -0.46, 0); // fail min ref jet pT

    TLorentzVector l1_3; l1_3.SetPtEtaPhiM(40, -5.6, -1, 0); // fail max L1 jet eta
    TLorentzVector ref_3; ref_3.SetPtEtaPhiM(38, -4.99, -1.1, 0);

    TLorentzVector l1_4; l1_4.SetPtEtaPhiM(40, 4.99, 1.1, 0);
    TLorentzVector ref_4; ref_4.SetPtEtaPhiM(38, 5.6, 1.1, 0); // fail max ref jet Eta

    refJets = {ref_1, ref_2, ref_3, ref_4};
    L1Jets = {l1_1, l1_2, l1_3, l1_4};

    // test via constructor
    matcher = new DeltaR_Matcher(0.7, 3, 4, 5.5);
    matcher->setRefJets(refJets);
    matcher->setL1Jets(L1Jets);
    pairs = matcher->getMatchingPairs();
    if (printStatements) {
        matcher->printName();
        matcher->printMatches();
    }
    CPPUNIT_ASSERT( pairs.size() == 0 );

    delete matcher;

    // test via setters
    matcher = new DeltaR_Matcher(0.7);
    matcher->setMinL1JetPt(1.5);
    matcher->setMinRefJetPt(1.5);
    matcher->setMaxJetEta(5);
    matcher->setRefJets(refJets);
    matcher->setL1Jets(L1Jets);
    pairs = matcher->getMatchingPairs();
    if (printStatements) {
        matcher->printName();
        matcher->printMatches();
    }
    CPPUNIT_ASSERT( pairs.size() == 0 );
}


/**
 * @brief Check that DeltaR_Matcher excludes pairs with deltaR > maxDeltaR
 * @details Check for deltaEta, deltaPhi, and deltaR. No pairs should match.
 */
void DeltaR_Matcher_UnitTest::checkDeltaRMax() {
    TLorentzVector l1_1; l1_1.SetPtEtaPhiM(40, 1, 0.71, 0); // deltaR > maxDeltaR
    TLorentzVector ref_1; ref_1.SetPtEtaPhiM(38, 1.41, 0.4, 0);

    TLorentzVector l1_2; l1_2.SetPtEtaPhiM(40, 1, -0.5, 0); // deltaEta > maxDeltaR
    TLorentzVector ref_2; ref_2.SetPtEtaPhiM(38, 1.8, -0.5, 0);

    TLorentzVector l1_3; l1_3.SetPtEtaPhiM(40, -1, -0.5, 0); // deltaPhi > maxDeltaR (checking we calculate out deltaPhi corectly)
    TLorentzVector ref_3; ref_3.SetPtEtaPhiM(38, -1, -1.46, 0);

    refJets = {ref_1, ref_2, ref_3};
    L1Jets = {l1_1, l1_2, l1_3};

    matcher = new DeltaR_Matcher(0.5);
    matcher->setRefJets(refJets);
    matcher->setL1Jets(L1Jets);
    pairs = matcher->getMatchingPairs();
    if (printStatements) {
        matcher->printName();
        matcher->printMatches();
    }
    CPPUNIT_ASSERT( pairs.size() == 0 );
}


/**
 * @brief Check to ensure that matches are made with pT-ordered collections
 * @details If there is a ref jet halfway between 2 l1 jets, it should be
 * matched with higher pT l1 jet (in this scheme)
 */
void DeltaR_Matcher_UnitTest::checkPtOrdering() {
    TLorentzVector l1_1;  l1_1.SetPtEtaPhiM(40, 1, 0.5, 0); // ref_1 should match with l1_1, not l1_2
    TLorentzVector l1_2; l1_2.SetPtEtaPhiM(38, 1, 1.0, 0);
    TLorentzVector ref_1; ref_1.SetPtEtaPhiM(32, 1, 0.75, 0);

    refJets = {ref_1};
    L1Jets = {l1_1, l1_2};

    matcher = new DeltaR_Matcher(0.5);
    matcher->setRefJets(refJets);
    matcher->setL1Jets(L1Jets);
    pairs = matcher->getMatchingPairs();
    if (printStatements) {
        matcher->printName();
        matcher->printMatches();
    }
    CPPUNIT_ASSERT( pairs.size() == 1 );
    CPPUNIT_ASSERT( pairs.at(0).first == ref_1 );
    CPPUNIT_ASSERT( pairs.at(0).second == l1_1 );
}


/**
 * @brief Checks to ensure ref jets are removed from collection after matched to L1 jet
 * @details If we have situation where l1_1 and l2_2 are equidistant to ref_1,
 * and there's also a ref_2 which is a bit further away from l1_2, then we should
 * match (l1_1,ref_1) and (l1_2,ref_2), not (l1_1,ref_1) and (l1_2,ref_2)
 */
void DeltaR_Matcher_UnitTest::checkRefJetRemoval() {
    TLorentzVector l1_1;  l1_1.SetPtEtaPhiM(40, 1, 0.5, 0); // ref_1 should match with l1_1, not l1_2
    TLorentzVector l1_2; l1_2.SetPtEtaPhiM(38, 1, 1.0, 0);
    TLorentzVector ref_1; ref_1.SetPtEtaPhiM(32, 1, 0.75, 0);
    TLorentzVector ref_2; ref_2.SetPtEtaPhiM(30, 1, 1.4, 0);

    refJets = {ref_1, ref_2};
    L1Jets = {l1_1, l1_2};

    matcher = new DeltaR_Matcher(0.5);
    matcher->setRefJets(refJets);
    matcher->setL1Jets(L1Jets);
    pairs = matcher->getMatchingPairs();
    if (printStatements) {
        matcher->printName();
        matcher->printMatches();
    }
    CPPUNIT_ASSERT( pairs.size() == 2 );
    CPPUNIT_ASSERT( pairs.at(0).first == ref_1 );
    CPPUNIT_ASSERT( pairs.at(0).second == l1_1 );
    CPPUNIT_ASSERT( pairs.at(1).first == ref_2 );
    CPPUNIT_ASSERT( pairs.at(1).second == l1_2 );
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
    runner.addTest( DeltaR_Matcher_UnitTest::suite() );
    runner.run();
    return 0;

    // alternatively, to include in BuildProcess, have to return value
    // diff to 0 in event of Failure
    // bool wasSuccessful = runner.run("", false);
    // return !wasSuccessful;
}