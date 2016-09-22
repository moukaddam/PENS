#include <TFile.h>
#include <TTree.h>

#include <cmath>
#include <string>
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>

using namespace std;

class cNucleus {

  public:
 
    int nMass, nProton, nNeutron;
    double nQuadrupole;
    // [0] = value, [1] = value+upper error, [2] = value-lower error
    vector <double> nDeformation;
    vector < vector <double >> nLevels;
    vector < vector <double >> nTransitions;
       
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
    
    void Clear(){
      nDeformation.clear();
      nLevels.clear();
      nTransitions.clear();
    };
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
  cNucleus *fNucleus = new cNucleus; 
  fRootTree->Branch("Nucleus", "cNucleus", &fNucleus, fSize, fSplit);
  
  Int_t fCounter = 1;
 
  // Read in data
  ifstream inFile("collate.dat");
    
  while (true) {
    // Read from file
    string inLine;
    stringstream inStream;
    getline(inFile, inLine);
    if (inFile.eof()) break;
    
    // Nuclear Information   
    if (inLine == "#N") {
      getline(inFile, inLine);
      inStream << inLine;
      inStream >> inA >> inZ >> inN >> inB >> inBu >> inBl >> inQ;
      cout << fCounter ++ << "\t" << inA << "\t" << inZ << endl;
      
      fNucleus->Clear(); 
      
      fNucleus->SetMass(inA);
      fNucleus->SetProton(inZ);
      fNucleus->SetNeutron(inN);
             
      fNucleus->SetDeformation(inB, inBu, inBl);
      fNucleus->SetQuadrupole(inQ);
      inStream << "";
      inStream.clear();
    
    // Level Information
    } else if (inLine == "#L") {
      getline(inFile, inLine);
      inStream << inLine;
      int sCount;
      inStream >> sCount;       // Get number of levels
      inStream << "";
      inStream.clear();
      for (int i=0; i<sCount; i++) {
        getline(inFile, inLine);
        inStream << inLine;
        vector <double> sLevel;
        for (int j=0; j<10; j++) {
          inStream >> inValue;
          sLevel.push_back(inValue);          
        }
        fNucleus->PushLevel(sLevel);
        sLevel.clear();
        inStream << "";
        inStream.clear();
      }
    // Transition Information
    } else if (inLine == "#T") {
      getline(inFile, inLine);
      inStream << inLine;
      int sCount;
      inStream >> sCount;       // Get number of transitions
      inStream << "";
      inStream.clear();
      for (int i=0; i<sCount; i++) {
        getline(inFile, inLine);
        inStream << inLine;
        vector <double> sTrans;
        for (int j=0; j<23; j++) {
          inStream >> inValue;
          sTrans.push_back(inValue);
        }
        fNucleus->PushTrans(sTrans);
        sTrans.clear();
        inStream << "";
        inStream.clear();
      } 
      
      fRootTree->Fill();
    } else {
      cout << "Unexpected error:\n\t" << inLine << endl;
      break;
    }

  }
  inFile.close();
  fRootTree->Write();
  fRootFile.Close();

  return 0;
}
