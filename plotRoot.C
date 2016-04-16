#include <TFile.h>
#include <TString.h>
#include <TGraphAsymmErrors.h>
#include <TTreeReader.h>
#include <TTreeReaderValue.h>
#include <TTreeReaderArray.h>
#include <TAxis.h>

#include <vector>
#include <iostream>
#include <string>

using namespace std;

int plotRoot() {

  // Open file
  TFile *fFile = TFile::Open("pensExtract.root");
  TTreeReader fReader("NS", fFile);

  vector <Double_t> fX, fXU, fXL, fY, fYU, fYL;

  TTreeReaderValue< int > tMass(fReader,"nMass");
  TTreeReaderValue< int > tProton(fReader, "nProton");
  TTreeReaderValue< int > tNeutron(fReader, "nNeutron");
  TTreeReaderValue< double > tMoment(fReader, "nQuadrupole");
  TTreeReaderArray< double > tDeformation(fReader, "nDeformation"); // [0] is value, [1] and [2] are upper and lower errors
  TTreeReaderArray< vector<double> > tLevels(fReader, "nLevels");
  TTreeReaderArray< vector<double> > tTrans(fReader, "nTransitions");

  // .. loop through entries in tree, adding to vectors
  while (fReader.Next()) {

    Double_t sMass = *tMass;
    Double_t sProton = *tProton;
    Double_t sNeutron = *tNeutron;
    
    Int_t sSize = tTrans.GetSize(); // Number of transitions
        
    for (int i=0; i<sSize; i++) {
      Int_t sInitSpin = tTrans[i][0];
      Int_t sInitParity = tTrans[i][1]; // + is +1, - is -1, tentative/unknown is 0
      Int_t sInitCount = tTrans[i][2];  // nth state of Jpi.  tentative/unknown is 0
      
      Int_t sFinalSpin = tTrans[i][3];
      Int_t sFinalParity = tTrans[i][4]; // + is +1, - is -1, tentative/unknown is 0
      Int_t sFinalCount = tTrans[i][5];
      
      Double_t sTranEnergy = tTrans[i][6]; // Transition Energy [keV]
      
      Double_t sTransLife = tTrans[i][7]; // Parent Half-life [ps]
      Double_t sTransLifeU = tTrans[i][8];
      Double_t sTransLifeL = tTrans[i][9];
      
      Double_t sTransBE2 = tTrans[i][10]; // B(E2) [W.u.]
      Double_t sTransBE2u = tTrans[i][11];
      Double_t sTransBE2l = tTrans[i][12];    
      
      Double_t sTransBM1 = tTrans[i][13]; // B(M1) [W.u.]
      Double_t sTransBM1u = tTrans[i][14];
      Double_t sTransBM1l = tTrans[i][15];    
      
      Double_t sTransMix = tTrans[i][16]; // Mixing Ratio
      Double_t sTransMixu = tTrans[i][17];
      Double_t sTransMixl = tTrans[i][18];    
      
      Double_t sTransQ2 = tTrans[i][19]; // q^2 (I(E0)/I(E2))
      Double_t sTransQ2u = tTrans[i][20];
      Double_t sTransQ2l = tTrans[i][20];    
      
      Double_t sTransRho = tTrans[i][21]; // rho^2 (E0) [milliunits]
      Double_t sTransRhou = tTrans[i][22];
      Double_t sTransRhol = tTrans[i][23];    
      
      Double_t sTransX = tTrans[i][24]; // X = B(E2)/B(E0)
      Double_t sTransXu = tTrans[i][25];
      Double_t sTransXl = tTrans[i][25];    
      
      Double_t sAlpha = tTrans[i][26];
      Double_t sAlphau = tTrans[i][27];
      Double_t sAlphal = tTrans[i][28];

      if (sTransBE2 != 0 && sNeutron==34 && sInitSpin == 2 && sFinalSpin==2) {  //  This is where you would define conditions
        fX.push_back(sMass);
        fXU.push_back(0.);
        fXL.push_back(0.);
        
        fY.push_back(sAlpha);
        fYU.push_back(sAlphau);
        fYL.push_back(sAlphal);
      }
    }
    /*
    Int_t sSize = tLevels.GetSize(); // Number of levels
    for (int i=0; i<sSize; i++) {
    
      Double_t sLevelEnergy = tLevels[i][0];  // Energy Level [keV]
      
      Int_t sLevelSpin = tLevels[i][0];   // Spin
      Int_t sLevelParity = tLevels[i][1]; // + is +1, - is -1, tentative/unknown is 0
      Int_t sLevelCount = tLevels[i][2];  // nth state of Jpi.  tentative/unknown is 0
      
      Double_t sTransLife = tTrans[i][4]; // Half-life [ps]
      Double_t sTransLifeU = tTrans[i][5]; // upper error
      Double_t sTransLifeL = tTrans[i][6]; // lower error
      
      if (sNeutron==34 && sLevelSpin==2 && sLevelCount==2) {  //  This is where you would define conditions
        fX.push_back(sMass);
        fXU.push_back(0.);
        fXL.push_back(0.);
        
        fY.push_back(sLevelEnergy);
        fYU.push_back(0.);
        fYL.push_back(0.);
      }
    
    }
    */
  }

  // Draw Plot
  Int_t fSize = fX.size();
  TGraphAsymmErrors *fPlot = new TGraphAsymmErrors(fSize, &fX[0], &fY[0], &fXL[0], &fXU[0], &fYL[0], &fYU[0]);
  fPlot->SetTitle("");
  fPlot->GetXaxis()->SetTitle("Mass Number");
  fPlot->GetYaxis()->SetTitle("ICC_{TOTAL}");
  fPlot->SetMarkerStyle(kCircle);
  fPlot->SetMarkerSize(0.5);
  fPlot->Draw("AP");

  return 0;
}
