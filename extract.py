import re, math, os, csv, requests, urllib2, sys
from functions import *

# Import google csv in to overwrite list
fExternal = []
print "Reading in from online spreadsheet..."
try:
  sCSVURL = 'https://docs.google.com/spreadsheet/ccc?key=178pS1nT7PEsmTwCdeJViEfrO2up3cMdzOgL7vO2Gyuk&output=csv'
  sInput = urllib2.urlopen(sCSVURL)
  sReader = csv.reader(sInput)
  fExternal = list(sReader)
  print "... SUCCESS!"
  print "... Read in", len(fExternal), "lines"
except urllib2.URLError:
  print "... FAILURE!"
#print "Ignore spreadsheet..."


# In turn, open each file within the data folder
fOutput = open('collate.dat', 'w') 
for i in sorted(os.listdir(os.getcwd() + "/data"), key=gGetIndex):

  fLvlEnergy = [] # Float single
  fLvlSpin = []   # Str 4 elements
  fLvlLife = []   # Str 3 elements
  
  fTrsIndex = []  # Str 2 elements
  fTrsBranch = [] # Str 3
  fTrsMixing = [] # Str 3 ele
  fTrsAlpha = []  # Str 2
  fTrsB = []      # Str 32
  
  fGroundRead = False

  # Open the file, get the mass and proton number  
  fInput = open("data/" + i,'r')
  nucMass = int(fInput.read(3))
  nucName = fInput.read(2)
  nucProton = gReturnProton(nucName.strip())
  nucS2n = [0., 0.]
  
  # At this point, let's extract the nuclides transitions from the external db into smaller list
  fOverwrite = [x for x in fExternal if gMatchMass(str(nucMass), str(nucProton), x)]
  #print fOverwrite
  
  
  
  print "Reading in", nucMass, nucName, nucProton
  
  # Read through each line in the file
  for fLine in fInput:
  
    if fLine[5:8] == " cQ":
      # Again, very little consistency in ENSDF files on a comment line, so I need to make >15 lines of code to read S(2n)
      if "S(2n)=" in fLine and not "theo" in fLine and not "|" in fLine:
        sPos = fLine.find("S(2n)=")
        sEnd = fLine.find("(",sPos+4)
        if (sEnd < 0):
          sEnd = len(fLine)
        if (fLine.find(",",sPos) < sEnd and fLine.find(",",sPos) > 0):
          sEnd = fLine.find(",",sPos)
        if (fLine.find(";",sPos) < sEnd and fLine.find(";",sPos) > 0):
          sEnd = fLine.find(";",sPos)
        if (fLine.find("}",sPos) < sEnd and fLine.find("}",sPos) > 0):
          sEnd = fLine.find("}",sPos)
        sArray = fLine[sPos+6:sEnd].replace("syst", "").replace("{I", "").replace("{i", "").replace("  ", " ").split()
        sError = 0
        if (len(sArray)>1):
          sError, sNull = gMatchError(sArray[0], sArray[1], sArray[1])
        nucS2n = [float(sArray[0]), float(sError)]
          
    if fLine[5:8] == "  L":                 # Level 
    
      sEnergy = fLine[9:19].strip()             # Energy (keV)
      if not gCheckNumber(sEnergy):
        continue  # Skip the +X, +Y, +Z energy levels
      else:
        fLvlEnergy.append(float(sEnergy))
        
      fGroundRead = True
      
      sSpin = fLine[21:39].strip()              # Spin and parity
      sLvlSpin = ["-1", "0", "-1", "0"]
      if len(sSpin) != 0:                   
        sLvlSpin = gProcessSpin(sSpin)
      fLvlSpin.append(sLvlSpin)
  
      sLife = fLine[39:49].strip()              # Half-life
      sLvlLife = ["0", "0", "0"]
      if sLife == "STABLE":
        sLvlLife = ["-1", "-1", "-1"]
      elif len(sLife) != 0:
        sLvlLife = gProcessLife(sLife, fLine[49:55].strip())
      fLvlLife.append(sLvlLife)
      
    elif fLine[5:8] == "  G" and fGroundRead:# Transition

      sEnergy = fLine[9:19].strip()             # Energy (keV)
      if not gCheckNumber(sEnergy):
        continue
      # Look through the list of energies to find the daughter state
      try:
        sFinEnergy = min(fLvlEnergy, key=lambda x:abs(x-(fLvlEnergy[-1] - float(sEnergy))))
      except ValueError:
        print fLvlEnergy[-1], sEnergy
      sIndex = [len(fLvlEnergy) - 1, fLvlEnergy.index(sFinEnergy)]
      fTrsIndex.append(sIndex)                  # Transition indices
      
      sBranch = fLine[21:29].strip()            # Branching ratio
      sTrsBranch = ["0", "0", "0"]
      if sBranch:
        sTrsBranch = gProcessBranch(sBranch, fLine[29:31].strip())
      fTrsBranch.append(sTrsBranch)
      
      sMixing = fLine[41:49].strip()            # Mixing ratio
      sTrsMixing = ["0", "0", "0"]
      if sMixing:
        sTrsMixing = gProcessMixing(sMixing, fLine[49:55].strip())
      fTrsMixing.append(sTrsMixing)
      
      sAlpha = fLine[55:62].strip()             # Conversion coefficient
      sTrsAlpha = ["0", "0"]
      if sAlpha:
        sTrsAlpha = gProcessAlpha(sAlpha, fLine[62:64].strip())
      fTrsAlpha.append(sTrsAlpha)
      
      # Not every transition will have a B(mL) value associated, so we want
      # to append a blank array now, then edit it when B(mL) line is read
      sTrsB = []
      while len(sTrsB) < 32:
        sTrsB.append("0")  
      fTrsB.append(sTrsB)
  
    elif fLine[5:8] == "B G" and fGroundRead:# B(mL) values of that transition
    
      sTrsB = gProcessB(fLine)
      if len(sTrsB) != 32:
        print "ERROR: Mismatched array in:\n " + fLine
        sys.exit()
      fTrsB[len(fTrsIndex) - 1] = sTrsB
  
  print " ... ", len(fLvlEnergy), " states and ", len(fTrsB), " transitions"
  fInput.close()
  
  # Write the nuclear data first
  fOutput.write("#N\n")
  fOutput.write("%d %d %d" % (nucMass, nucProton, nucMass-nucProton))
  fOutput.write(" %f %f\n" % (nucS2n[0], nucS2n[1]))
  
  # .. then the level information
  fOutput.write("#L\n")
  fOutput.write("%d\n" % (len(fLvlEnergy)))
  for i in range(0, len(fLvlEnergy)): # Loop over ith element in array, rather than element itself 
    fOutput.write("%d" % (fLvlEnergy[i]))
    fOutput.write(" %s %s %s %s" % (fLvlSpin[i][0], fLvlSpin[i][1], fLvlSpin[i][2], fLvlSpin[i][3]))
    fOutput.write(" %s %s %s\n" % (fLvlLife[i][0], fLvlLife[i][1], fLvlLife[i][2]))

  # .. then the transition information
  fOutput.write("#T\n")
  fOutput.write("%d\n" % (len(fTrsIndex)))
  for i in range(0, len(fTrsIndex)):
    fOutput.write("%s %s" % (fTrsIndex[i][0], fTrsIndex[i][1]) )
    fOutput.write(" %s %s %s" % (fTrsBranch[i][0], fTrsBranch[i][1], fTrsBranch[i][2]) )
    for eachEntry in fTrsB[i]:
      fOutput.write(" " + eachEntry)
    fOutput.write(" %s %s %s" % (fTrsMixing[i][0], fTrsMixing[i][1], fTrsMixing[i][2]) )
    fOutput.write(" %s %s\n" % (fTrsAlpha[i][0], fTrsAlpha[i][1]) )


fOutput.close()
  
