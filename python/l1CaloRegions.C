/**
 * @brief Plot the L1CaloRegions & L1CaloEmCands as output by the RCT emulator and GCT unpacker for comparison
 */
{
	TFile f("SimGCTEmulator_newRCT.root");
	TTree * tree;
	f.GetObject("Events", tree);

	// jet regions
	tree->Draw("L1CaloRegions_gctDigis__L1NTUPLE.obj.et()>>h_gct", "L1CaloRegions_gctDigis__L1NTUPLE.obj.et()>0");
	tree->Draw("L1CaloRegions_simRctDigis__L1NTUPLE.obj.et()>>h_rct", "L1CaloRegions_simRctDigis__L1NTUPLE.obj.et()>0");

	// EM
	tree->Draw("L1CaloEmCands_gctDigis__L1NTUPLE.obj.rank()>>h_gct_em");
	tree->Draw("L1CaloEmCands_simRctDigis__L1NTUPLE.obj.rank()>>h_rct_em");

	tree->Draw("L1GctJetCands_gctDigis_cenJets_L1NTUPLE.obj.raw()>>h_gct_jets", "L1GctJetCands_gctDigis_cenJets_L1NTUPLE.obj.raw()>0");
	tree->Draw("L1GctJetCands_simGctDigis_cenJets_L1NTUPLE.obj.raw()>>h_rct_jets", "L1GctJetCands_simGctDigis_cenJets_L1NTUPLE.obj.raw()>0");

	h_rct.SetLineColor(kRed);
	h_rct_em.SetLineColor(kRed);

	TLegend leg(0.5, 0.5, 0.8, 0.8);
	leg.AddEntry(h_gct, "L1CaloRegions from gctDigis","L");
	leg.AddEntry(h_rct, "L1CaloRegions from simRctDigis", "L");
	h_gct.SetTitle("Running with simHcalTriggerPrimitiveDigis remade using simHcalUnsuppressedDigis, new RCT calibs no cff;L1CaloRegion.et();N");
	c1.SetLogy();
	h_gct.Draw();
	h_rct.Draw("SAME");
	leg.Draw();
	c1.SaveAs("gct_vs_rct_region_et_simHcalTriggerPrimitiveDigis-simHcalUnsuppressedDigis_newRCT.pdf");

	h_gct.SetTitle("new RCT calibs, no cff;L1CaloEmCand.rank();N");
	h_gct_em.Draw();
	h_rct_em.Draw("SAME");
	TLegend leg(0.5, 0.5, 0.8, 0.8);
	leg.AddEntry(h_gct_em, "L1CaloEmCands from gctDigis","L");
	leg.AddEntry(h_rct_em, "L1CaloEmCands from simRctDigis", "L");
	leg.Draw();
	c1.SaveAs("gct_vs_rct_em_regions_newRCT.pdf");

	// h_gct_jets.Draw();
	// h_rct_jets.SetLineColor(kRed);
	// h_rct_jets.Draw("SAME");
	// c1.SaveAs("gct_vs_rct_cenJets.pdf");

}
