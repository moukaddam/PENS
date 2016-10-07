#include <TFile.h>
#include <TString.h>
#include <TGraphAsymmErrors.h>
#include <TTreeReader.h>
#include <TTreeReaderValue.h>
#include <TTreeReaderArray.h>
#include <TAxis.h>

#include <vector>
#include <iostream>
#include <fstream>
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

  TTreeReaderArray< vector<double> > tLevels(fReader, "nLevels");
  TTreeReaderArray< vector<double> > tTrans(fReader, "nTransitions");
  
  ofstream outFile("out.dat");

  // .. loop through entries in tree, adding to vectors
  while (fReader.Next()) {

    Double_t sMass = *tMass;
    Double_t sProton = *tProton;
    Double_t sNeutron = *tNeutron;
    
    Int_t sTrsSize = tTrans.GetSize(); // Number of transitions
    Int_t sLvlSize = tLevels.GetSize();
    
    //cout << "Reading " << sMass << " " << sProton << endl;
    //cout << " with " << sLvlSize << " level(s) and " << sTrsSize << " transition(s)" << endl;
                
    for (int i=0; i<sTrsSize; i++) {
    
      // In the level vector:
      // [0] - State energy (keV)
      // [1], [2], [3] Confirmed spin, parity and Nth occurence
      //   The spin is -1 if unknown/tentative. 
      //   The parity is +1 for positive, -1 for negative, 0 for unknown/tentative. 
      //   The count begins at 1, and is -1 if the state spin is unknown/tentative. 
      //   For example, the second 2+ state will correspond to [1] = 2, [2] = +1, [3] = 2
      // [4], [5], [6] As above, but including tentative assignments
      // [7], [8], [9] Half-life in ps, with the upper and lower errors
    
      // In the transition vector:
      // [0] - Parent ID of the level vector
      // [1] - Daughter ID of the level vector
      // [2], [3] Branching ratio (I_gamma) and the associated error
      // [4], [5], [6], [7] B(E1) (W.u.) value, upper, lower error and confirmed flag
      //   Flag is 1 if confirmed, 0 if tentative
      // [8], [9], [10], [11] B(E2)
      // [12], [13], [14], [15] B(E3)
      // [16], [17], [18], [19] B(E4)
      // [20], [21], [22], [23] B(M1)
      // [24], [25], [26], [27] B(M2)
      // [28], [29], [30], [31] B(M3)
      // [32], [33], [34], [35] B(M4)    
      // [36], [37], [38] Mixing ratio with upper, lower errors
      // [39], [40] ICC with error
      
      for (int j=0; j<sLvlSize; j++) 
        double sE =  tLevels[j][0]; // Program crashes if you don't read through level vector prior
    
      Int_t sParent = (int)(tTrans[i][0]);
      Double_t sParentSpin = tLevels[sParent][4];
      Double_t sParentParity = tLevels[sParent][5];
      Double_t sParentCount = tLevels[sParent][6];
      
      Int_t sDaughter = (int)(tTrans[i][1]);
      Double_t sDaughterSpin = tLevels[sDaughter][4];
      Double_t sDaughterParity = tLevels[sDaughter][5];
      Double_t sDaughterCount = tLevels[sDaughter][6];
      
      Double_t sTransEnergy = tLevels[sParent][0] - tLevels[sDaughter][0];
      
      Double_t sHalflife = tLevels[sParent][7];
      Double_t sMixing = tTrans[i][36];
      Double_t sAlpha = tTrans[i][39];
      
      if ((sParentSpin == sDaughterSpin) && (sParentParity == sDaughterParity) 
          && (sHalflife != 0) && (sMixing != 0) && (sAlpha != 0)
          && (sParentSpin == 2) && (sParentParity != 0)) {
        outFile << sMass << "\t" << sProton << "\t"
                << sTransEnergy << "\t" 
                << sParentSpin << "\t" << sParentParity << "\t" << sParentCount << "\t"
                << sDaughterSpin << "\t" << sDaughterParity << "\t" << sDaughterCount << "\t"
                << sHalflife << "\t" << sMixing << "\t" << sAlpha << endl;
      }
      
/*
      if (sTransBE2 != 0 && sNeutron==34 && sInitSpin == 2 && sFinalSpin==2) {  //  This is where you would define conditions
        fX.push_back(sMass);
        fXU.push_back(0.);
        fXL.push_back(0.);
        
        fY.push_back(sAlpha);
        fYU.push_back(sAlphau);
        fYL.push_back(sAlphal);
      }
      */
    }

  }
  
  outFile.close();
/*
  // Draw Plot
  Int_t fSize = fX.size();
  TGraphAsymmErrors *fPlot = new TGraphAsymmErrors(fSize, &fX[0], &fY[0], &fXL[0], &fXU[0], &fYL[0], &fYU[0]);
  fPlot->SetTitle("");
  fPlot->GetXaxis()->SetTitle("Mass Number");
  fPlot->GetYaxis()->SetTitle("ICC_{TOTAL}");
  fPlot->SetMarkerStyle(kCircle);
  fPlot->SetMarkerSize(0.5);
  fPlot->Draw("AP");
*/
  return 0;
}
