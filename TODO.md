# TODO

- [ ] Start with TLorentzVector being passed, THEN generalise to template it
- [ ] Write tests - CppUnit is in CMSSW
    + [x] for Matcher/DeltaR_Matcher
- [ ] Do NVI? https://en.wikibooks.org/wiki/More_C%2B%2B_Idioms/Non-Virtual_Interface http://www.parashift.com/c++-faq-lite/protected-virtuals.html
- [ ] Rename getMatchingPairs -> getMatch**ed**Pairs?
- bsub -q 8nh -W 400 runConfigJob.sh
- [ ] check Matcher memory usage
- [ ] print out all options
- [ ] namesapce?
- [ ] do cuts on jets outside matcher?
- [ ] const ify things!
- [?] Change from passing object copies to refs/ptrs
- [ ] consistent style - K&R? clang-format
- [ ] stage 1 setup?
- [ ] stage 2 setup?

Done
=====
- [x] Update doxy comments  on L1ExtraTree
- [x] check TDirectory actually exists in L1ExtraTree ctor
- [x] How to stop matching to same L1 jet more than once?
- [x] What priority for ref jets? pT?
- [x] Match L1 to ref? or v.v.
- [x] visual drawer for L1 & ref jets, and matches - useful for debugging? JS? **Use TMultiGraph for now**
- [x] match_lots folder to take on suffixes?
- [x] No raw pointers. SHARED/AUTO PTRS
- [x] Do Matcher first.
- [x] Update README and write DEVNOTES
- [x] maxJetPT cut?