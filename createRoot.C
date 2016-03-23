#include <TFile.h>
#include <TTree.h>

#include <cmath>
#include <string>
#include <iostream>
#include <fstream>
#include <vector>

using namespace std;

class cNucleus {
 
  int nMass, nProton, nNeutron;
  double nQuadrupole;
  // [0] = value, [1] = value+upper error, [2] = value-lower error
  vector <double> nDeformation;
  vector < vector <double >> nLevels;
  vector < vector <double >> nTransitions;
 
  public:      
        
    void SetMass(int sMass) {nMass = sMass;}
    void SetProton(int sProton) {nProton = sProton;}
    void SetNeutron(int sNeutron) {nNeutron = sNeutron;}
    void SetDeformation(Double_t sValue, Double_t sUpper, Double_t sLower) {
      nDeformation.push_back(sValue);
      nDeformation.push_back(sUpper);
      nDeformation.push_back(sLower);
    }
    void SetQuadrupole(double sQuad) {nQuadrupole = sQuad;}
    
    void PushLevel(vector <double> sLevel) {nLevels.push_back(sLevel);}
    void PushTrans(vector <double> sTrans) {nTransitions.push_back(sTrans);}
    
};



int createRoot() {

  // Variable declaration
  // .. input file variables
  double inValue, inA, inZ, inN, inB, inBu, inBl, inQ;
  
  // Create root file and tree
  TFile fRootFile("pensExtract.root","RECREATE");
  TTree *fRootTree = new TTree("NS","Nuclear Systematics");
  // .. and create a new branch for each data member of event object
  Int_t fSplit = 1; // multi-branch -- what?
  Int_t fSize = 64000;
  cNucleus *fNucleus = 0;
  fRootTree->Branch("Nucleus", "cNucleus", &fNucleus, fSize, fSplit);
  
  Int_t fCounter = 1;
 
  // Read in data
  ifstream inFile("collate.dat");
  string inString;
  
  while (true) {
    // Read from file
    getline(inFile, inString);
    if (inFile.eof()) break;
    
    // Nuclear Information
    if (inString == "#N") {
      inFile >> inA >> inZ >> inN >> inB >> inBu >> inBl >> inQ;
      
      fNucleus = new cNucleus; 
      
      fNucleus->SetMass(inA);
      fNucleus->SetProton(inZ);
      fNucleus->SetNeutron(inN);
             
      fNucleus->SetDeformation(inB, inBu, inBl);
      fNucleus->SetQuadrupole(inQ);
    
    // Level Information
    } else if (inString == "#L") {
      int sCount;
      inFile >> sCount;       // Get number of levels
      for (int i=0; i<sCount; i++) {
        vector <double> sLevel;
        for (int j=0; j<7; j++) {
          inFile >> inValue;
          sLevel.push_back(inValue);
        }
        fNucleus->PushLevel(sLevel);
        sLevel.clear();
      }
    // Transition Information
    } else if (inString == "#T") {
      int sCount;
      inFile >> sCount;       // Get number of transitions
      for (int i=0; i<sCount; i++) {
        vector <double> sTrans;
        for (int j=0; j<26; j++) {
          inFile >> inValue;
          sTrans.push_back(inValue);
        }
        fNucleus->PushTrans(sTrans);
        sTrans.clear();
      }
      
      fRootTree->Fill();
      delete fNucleus;
    }

  }
  inFile.close();
  fRootTree->Write();
  fRootFile.Close();

  return 0;
}
