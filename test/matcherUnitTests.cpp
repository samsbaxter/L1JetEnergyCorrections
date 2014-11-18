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
    CPPUNIT_TEST( runSimpleTest );
    CPPUNIT_TEST_SUITE_END();

public:
    MatcherUnitTest() {};

    void setUp();
    void tearDown();

    void runSimpleTest();

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
    // if (m != nullptr) delete m;
}

/**
 * @brief Runs simple matching test to ensure it should do the basics
 * @details Should match l1_1 with ref_1, etc. Done in all 4 quadrants of eta-phi space.
 * No min pT or max eta checks.
 */
void MatcherUnitTest::runSimpleTest() {
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

    delete m;
    refJets.clear();
    L1Jets.clear();
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