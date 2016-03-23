#include <TFile.h>
#include <TTree.h>

#include <cmath>
#include <string>
#include <iostream>
#include <fstream>
#include <vector>

using namespace std;

class cNucleus {
  // Values with uncertainties will be contained in a vector
  // [0] = value, [1] = value+upper error, [2] = value-lower error
  vector <Double_t> nMass, nProton, nNeutron, nQuadrupole;
  vector <Double_t> nDeformation;
  vector <Double_t> nEnergy0n2, nEnergy2n1, nEnergy4n1, nEnergy2n2;
  
  // Transitions
  vector <string> transID;
  vector <Double_t> transEnergy, transLifetime, transBE2, transBM1, transMix, transq2, transRho, transX;

  public:      
        
    void SetMass(Double_t sMass) {nMass.push_back(sMass);}
    void SetProton(Double_t sProton) {nProton.push_back(sProton);}
    void SetNeutron(Double_t sNeutron) {nNeutron.push_back(sNeutron);}
    void SetDeformation(Double_t sValue, Double_t sUpper, Double_t sLower) {
      nDeformation.clear();
      nDeformation.push_back(sValue);
      nDeformation.push_back(sUpper);
      nDeformation.push_back(sLower);
    }
    void SetQuadrupole(Double_t sQuad) {nQuadrupole.push_back(sQuad);}
    
    
    void SetEnergy0n2(Double_t sEnergy0n2) {nEnergy0n2.push_back(sEnergy0n2);}
    void SetEnergy2n1(Double_t sEnergy2n1) {nEnergy2n1.push_back(sEnergy2n1);}
    void SetEnergy4n1(Double_t sEnergy4n1) {nEnergy4n1.push_back(sEnergy4n1);}
    void SetEnergy2n2(Double_t sEnergy2n2) {nEnergy2n2.push_back(sEnergy2n2);}
    
    void SetID(string sID) {transID.push_back(sID);}
    void SetEnergy(Double_t sValue) { transEnergy.push_back(sValue);}
    
    void SetLifetime(Double_t sValue, Double_t sUpper, Double_t sLower) {
      transLifetime.clear();
      transLifetime.push_back(sValue);
      transLifetime.push_back(sUpper);
      transLifetime.push_back(sLower);
    }
    void SetBE2(Double_t sValue, Double_t sUpper, Double_t sLower) {
      transBE2.clear();
      transBE2.push_back(sValue);
      transBE2.push_back(sUpper);
      transBE2.push_back(sLower);
    }
    void SetBM1(Double_t sValue, Double_t sUpper, Double_t sLower) {
      transBM1.clear();
      transBM1.push_back(sValue);
      transBM1.push_back(sUpper);
      transBM1.push_back(sLower);
    }
    void SetMix(Double_t sValue, Double_t sUpper, Double_t sLower) {
      transMix.clear();
      transMix.push_back(sValue);
      transMix.push_back(sUpper);
      transMix.push_back(sLower);
    }
    void Setq2(Double_t sValue, Double_t sUpper, Double_t sLower) {
      transq2.clear();
      transq2.push_back(sValue);
      transq2.push_back(sUpper);
      transq2.push_back(sLower);
    }
    void SetRho(Double_t sValue, Double_t sUpper, Double_t sLower) {
      transRho.clear();
      transRho.push_back(sValue);
      transRho.push_back(sUpper);
      transRho.push_back(sLower);
    }
    void SetX(Double_t sValue, Double_t sUpper, Double_t sLower) {
      transX.clear();
      transX.push_back(sValue);
      transX.push_back(sUpper);
      transX.push_back(sLower);
    }
    
};



int createRoot() {

  // Variable declaration
  // .. input file variables
  int inA, inZ, inN;
  double inB, inBu, inBl, inQ;
  double inEnergy0n2, inEnergy2n1, inEnergy4n1, inEnergy2n2;
  string inTransSpinPa, inTransSpinDa;
  string inTransCountPa, inTransCountDa;
  double inTransEnergy, inLife, inLifeu, inLifel, inBE2, inBE2u, inBE2l, inBM1, inBM1u, inBM1l;
  double inMix, inMixu, inMixl, inq2, inq2e, inRho, inRhol, inRhou;
  double inX, inXe;
  
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
    
    if (inString == "#N")
      inFile >> inA >> inZ >> inN >> inB >> inBu >> inBl >> inQ;
    else if (inString == "#L") {
      inFile >> inEnergy >> inSpin >> inCount >> inLife >> inLifeu >> inLifel;
      vector <Double_t> sVector
      
    cout << inA << "\t" << inZ << endl;
    

    /*
    inFile >> inA >> inZ >> inN >> inB >> inBu >> inBl >> inQ
           >> inEnergy0n2 >> inEnergy2n1 >> inEnergy4n1 >> inEnergy2n2
           >> inTransSpinPa >> inTransCountPa >> inTransSpinDa >> inTransCountDa
           >> inTransEnergy
           >> inLife >> inLifeu >> inLifel >> inBE2 >> inBE2u >> inBE2l
           >> inBM1 >> inBM1u >> inBM1l  >> inMix >> inMixu >>inMixl
           >> inq2 >> inq2e >> inRho >> inRhou >> inRhol >> inX >> inXe;

    if (inFile.eof()) break;
    
    cout << fCounter << "\t" << inA << "\t" << inZ << "\t" << inTransEnergy  << endl; */
    
    /*
    if (inA == 0) break;
        

    fNucleus = new cNucleus;
     
      fNucleus->SetMass(inA);
      fNucleus->SetProton(inZ);
      fNucleus->SetNeutron(inN);
             
      fNucleus->SetDeformation(inB, inBu, inBl);
      fNucleus->SetQuadrupole(inQ);
        
      fNucleus->SetEnergy0n2(inEnergy0n2);
      fNucleus->SetEnergy2n1(inEnergy2n1);
      fNucleus->SetEnergy4n1(inEnergy4n1);
      fNucleus->SetEnergy2n2(inEnergy2n2);
        
      fNucleus->SetID(inTransSpinPa);
      fNucleus->SetEnergy(inTransEnergy);
      fNucleus->SetLifetime( inLife, inLifeu, inLifel);
      fNucleus->SetBE2( inBE2, inBE2u, inBE2l);
      fNucleus->SetBM1( inBM1, inBM1u, inBM1l);
      fNucleus->SetMix(inMix, inMixu, inMixl);
      fNucleus->Setq2( inq2, inq2e, inq2e );
      fNucleus->SetRho(inRho, inRhou, inRhol);
      fNucleus->SetX(inX, inXe, inXe);
*/        
    fCounter++;
            
  //  fRootTree->Fill();
   // delete fNucleus;

  }
  inFile.close();
  //fRootTree->Write();
  fRootFile.Close();

  return 0;
}
