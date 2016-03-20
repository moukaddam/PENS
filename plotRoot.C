#include <TFile.h>
#include <TString.h>
#include <TGraphAsymmErrors.h>
#include <TTreeReader.h>
#include <TTreeReaderValue.h>
#include <TAxis.h>

#include <vector>
#include <iostream>
#include <string>

using namespace std;

bool gDEBUG = true;

string GetName(string name);
int plotRoot(string userX="nMass", string userY="transBE2", string userCondition="transID") {

  // Open file
  TFile *fFile = TFile::Open("pensExtract.root");
  TTreeReader fReader("T", fFile);
  
  vector <Double_t> fX, fXU, fXL, fY, fYU, fYL;
   
  // TTreeReader opens property.  Every property is a vector for convenience, no error values (e.g. Z) have size == 1
  // For properties with error, the second number is upper error, the third number is lower error
  TTreeReaderValue< vector<Double_t> > fXValue(fReader, userX.c_str());
  TTreeReaderValue< vector<Double_t> > fYValue(fReader, userY.c_str());
  TTreeReaderValue< vector<string> > fCond(fReader, userCondition.c_str());
  // .. loop through entries in tree, adding to vectors
  int fCounter = 1;
  if (gDEBUG) cout << Form("Line\t\t%s\t\t%s\n", GetName(userX).c_str(), GetName(userY).c_str());
  while (fReader.Next()) {
    Double_t sX = fXValue->at(0);
    Double_t sY = fYValue->at(0);
    if (sX != 0 && sY != 0 && fCond->at(0) == "1211011") { //  This is where you would add additional limits e.g. && fCond->at(0) == 12221
      if (gDEBUG) cout << fCounter << "\t\t" << sX << " " << "\t\t" << sY << endl;
      fX.push_back(sX);
      if (fXValue->size() > 1) {
        fXU.push_back(fXValue->at(1)); fXL.push_back(fXValue->at(2));
      } else {
        fXU.push_back(0); fXL.push_back(0);
      }
      fY.push_back(sY);
      if (fYValue->size() > 1) {
        fYU.push_back(fYValue->at(1)); fYL.push_back(fYValue->at(2));
      } else {
        fYU.push_back(0); fYL.push_back(0);
      }
    
    }
    fCounter++;
  }

  // Draw Plot
  Int_t fSize = fX.size();
  TGraphAsymmErrors *fPlot = new TGraphAsymmErrors(fSize, &fX[0], &fY[0], &fXL[0], &fXU[0], &fYL[0], &fYU[0]);
  fPlot->SetTitle("");
  fPlot->GetXaxis()->SetTitle(GetName(userX).c_str());
  fPlot->GetYaxis()->SetTitle(GetName(userY).c_str());
  fPlot->SetMarkerStyle(kCircle);
  fPlot->SetMarkerSize(0.5);
  fPlot->Draw("AP");


  return 0;
}

string GetName(string fName) {

  if (fName == "nMass") return "Mass Number";
  if (fName == "nProton") return "Proton Number";
  if (fName == "nNeutron") return "Neutron Number";
  if (fName == "nQuadrupole") return "Quadrupole Moment";
  if (fName == "nDeformation") return "Deformation";
  if (fName == "nEnergy0n2") return "0^{+}_{2} Energy [keV]";
  if (fName == "nEnergy2n1") return "2^{+}_{1} Energy [keV]";
  if (fName == "nEnergy4n1") return "4^{+}_{1} Energy [keV]";
  if (fName == "nEnergy2n2") return "2^{+}_{2} Energy [keV]";
  if (fName == "transID") return "Transition ID";
  if (fName == "transEnergy") return "Transition Energy [keV]";
  if (fName == "transLifetime") return "Parent Lifetime [ps]";
  if (fName == "transBE2") return "B(E2) [W.u.]";
  if (fName == "transBM1") return "B(M1) [W.u.]";
  if (fName == "transMix") return "Mixing Ratio";
  if (fName == "transq2") return "q^{2}";
  if (fName == "transRho") return "#rho^{2} (E0) #times 10^{-3}";
  if (fName == "transX") return "X";
  else return "UNKNOWN";
  
}
