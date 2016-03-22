import re, math, os, csv, requests, urllib2

# PENS
# ====
# Lee J. Evitts (evitts at triumf.ca)
#
#
# The goal of the PENS project is to parse information of even-even nuclei from ENSDF for purpose of
# plotting systematics, though the code can be adapted for other things e.g. CLX or simulation inputs.  

def gReturnProton(fName):
  # Function to return proton number from name
  return {
    'HE': 2, 'BE': 4, 'C': 6, 'O': 8, 'NE': 10, 'MG': 12, 'SI': 14, 'S': 16, 'AR': 18,
    'CA': 20, 'TI': 22, 'CR': 24, 'FE': 26, 'NI': 28, 'ZN': 30, 'GE': 32, 'SE': 34,
    'KR': 36, 'SR': 38, 'ZR': 40, 'MO': 42, 'RU': 44, 'PD': 46, 'CD': 48, 'SN': 50,
    'TE': 52, 'XE': 54, 'BA': 56, 'CE': 58, 'ND': 60, 'SM': 62, 'GD': 64, 'DY': 66,
    'ER': 68, 'YB': 70, 'HF': 72,  'W': 74, 'OS': 76, 'PT': 78, 'HG': 80, 'PB': 82,
    'PO': 84, 'RN': 86, 'RA': 88, 'TH': 90,  'U': 92, 'PU': 94, 'CM': 96, 'CF': 98
  }.get(fName, "00")
         
def gReturnTime(fUnit):
  # Function to return conversion of [time] to PS
  return {
    'PS': 1.0, 'FS': 0.001, 'NS': 1000., 'US': 1.0E6, 'MS': 1.0E9, 'M': 6.0E13, 'S': 1.0E12, 'H': 3.6E15, 'Y': 3.154E19, 'D': 8.64E16, 'AS':1E-6
  }.get(fUnit, "??")
  
def gCheckNumber(fChar):
  # Function to check if string can be converted to integer
  try:
    float(fChar)
    return True
  except ValueError:
    return False
    
def gFindIter(fString, fSub, fN):
  # Finds the nth occurence of fSub in fString
  fStart = fString.find(fSub)
  while fStart >= 0 and fN > 1:
    fStart = fString.find(fSub, fStart+len(fSub))
    fN -= 1
  return fStart
    
def gMatchError(fValue, fUpper, fLower):
  # Errors in ENSDF are the last X digts of the value, this function changes error to
  # same magnitude as value e.g. 2.3(3) becomes 2.3 0.3
  fPrecision = 0
  if "E" in fValue:                                   # Sometimes B() values are in exponent format
    fFront, fExponent = fValue.split("E")
    if "." in fFront:
      fMain, fFraction = fFront.split('.')
      fPrecision = len(fFraction)
    else:
      fPrecision = 0
    fUpper = str(float(fUpper) / 10**fPrecision)
    fLower = str(float(fLower) / 10**fPrecision)
    return (fUpper + "E" + fExponent, fLower + "E" + fExponent)
  try:
    fMain, fFraction = fValue.split('.')
    fPrecision = len(fFraction)
    fUpper = float(fUpper) / 10**fPrecision
    fLower = float(fLower) / 10**fPrecision
    return (str(fUpper), str(fLower))
  except ValueError:
    return (fUpper, fLower)
    
def gReturnB(fString):
  # fString is in the format of e.g. E2=0.49 +13-18, this code strips out the value from
  # error and returns an array of (value, upper error, lower error)
  sVector = []
  if fString[2] == "=":
    try:
      sValue, sError = fString[3:].strip().split(" ")
      sVector.append(sValue)
      if sError.strip()[0] == "+":
        sMatch = re.search(r"[^a-zA-Z](-)[^a-zA-Z]", sError)
        sUpper, sLower = gMatchError(sValue, sError[1:sMatch.start(1)], sError[sMatch.start(1)+1:])
        sVector.append(sUpper)
        sVector.append(sLower)
      else:
        sUpper, sLower = gMatchError(sValue, sError, sError)
        sVector.append(sUpper)
        sVector.append(sLower)
    except ValueError:
      sVector.append(fString[3:])
      sVector.append("0")
      sVector.append("0")
  elif fString[2] == "<": 
    sVector.append(fString[3:])
    sVector.append("0")
    sVector.append(fString[3:])
  elif fString[3:5] ==  "LT" or fString[3:5] == "LE":
    sVector.append(fString[6:])
    sVector.append("0")
    sVector.append(fString[6:])
  elif fString[2] == ">":
    sVector.append(fString[3:])
    sVector.append("0")
    sVector.append("0")
  elif fString[3:5] == "GE" or fString[3:5] == "GT" or fString[3:5] == "AP": #Approximately
    sVector.append(fString[6:])
    sVector.append("0")
    sVector.append("0")
  else:
    print fString
  return sVector
  
# Import google csv in to overwrite list
print "Reading in from online spreadsheet..."
try:
  fCSVURL = 'https://docs.google.com/spreadsheet/ccc?key=178pS1nT7PEsmTwCdeJViEfrO2up3cMdzOgL7vO2Gyuk&output=csv'
  fInput = urllib2.urlopen(fCSVURL)
  fReader = csv.reader(fInput)
  fOverwrite = list(fReader)
  print "... SUCCESS!"
except urllib.request.URLError:
  print "... FAILURE!"

fNull = ["0.0", "0.0", "0.0"]

# In turn, open each file within the data folder
fOutput = open('collate.dat', 'w') 
for i in os.listdir(os.getcwd() + "/data"):

  fLvlEnergy = []
  fLvlSpin = []
  fLvlCount = []
  fLvlHalflife = []

  fTrsBM1 = []
  fTrsBE2 = []
  fTrsMixing = []
  fTrsEnergy = []
  fTrsSpinPa = []  # J+ of "parent" state
  fTrsCountPa = [] # n of "parent"
  fTrsSpinDa = []  # J+ of "daughter" state
  fTrsCountDa = [] # n of "daughter"
  fTrsLife = []

  # Open the file, get the mass and proton number  
  fInput = open("data/" + i,'r')
  nucMass = int(fInput.read(3))
  nucName = fInput.read(2)
  nucProton = gReturnProton(nucName.strip())
  
  print "Reading in " + str(nucMass) + nucName
 
  sTrsBM1 = []
  sTrsBE2 = []
  sTrsMixing = []
  sTrsEnergy = 0.0
  sTrsSpinPa = ""
  sTrsCountPa = ""
  sTrsSpinDa = ""
  sTrsCountDa = ""
  
  fGroundRead = False

  # Read through each line in the file, firstly looking for energy levels
  for fLine in fInput:
    
    #if len(fLvlEnergy) == 200:               # Limit of the first x energy levels
    #  break
    if fLine[5:8] != "  L" and fLine[5:8] != "  G" and fLine[5:8] != "B G":
      continue                              # Skip everything that isn't energy level, transition, transition details

    if fLine[5:8] == "  L":                 # Energy level 
      if not gCheckNumber(fLine[9:19]):       # .. skipping the +X levels
        continue
      #print(repr(fLine[9:19]))
      fLvlEnergy.append(float(fLine[9:19])) # Energy, omitting error 
      sSpin = fLine[21:25].strip()

      # Check for definitive spin/parity assignment (must have + or -, and must be a number without either of those characters)
      if any(sChar in sSpin for sChar in ["+", "-"]) and gCheckNumber(sSpin.translate(None, '+-')):
        fLvlSpin.append(sSpin)
        sCount = fLvlSpin.count(sSpin)
        fLvlCount.append(str(sCount))
      else:                                 #  If not J+ format (J<10) then subbed with char
        fLvlSpin.append("xx")
        fLvlCount.append("x")
      
      sList = []                            # Halflife
      if not fGroundRead:         # (STABLE)
        sHalflife = ["0.0", "0.0", "0.0"]
        fLvlHalflife.append(sHalflife)
      else:
        sLifeString = fLine[39:49].strip()   
        sUnit = gReturnTime(sLifeString[-2:].strip())
        if sUnit != "??":
          sList.append(str(float(sLifeString[:-2].strip()) * sUnit))
        elif not sLifeString or sLifeString[-2:] == "EV" or "?" in sLifeString[-2:]:    # (BLANK)
          sHalflife = ["0.0", "0.0", "0.0"]
          fLvlHalflife.append(sHalflife)
          continue
        else:
          print sLifeString
          print "ATTN: UNKNOWN HALF-LIFE UNIT", sLifeString[-2:]
          break
          
        if "+" in fLine[49:55]:              # Error (+/-)
          sSubstring = fLine[49:55].strip()
          sMatch = re.search(r"[^a-zA-Z](-)[^a-zA-Z]", sSubstring)
          sUpper, sLower = gMatchError(str(sLifeString[:-2].strip()), str(sSubstring[1:sMatch.start(1)]), str(sSubstring[sMatch.start(1)+1:]))
          sList.append(str(float(sUpper)*sUnit))
          sList.append(str(float(sLower)*sUnit))
        elif "G" in fLine[49:55]:              # Error (GT)
          sList.append("0.0")                 # .. 0 error
          sList.append("0.0")
        elif "L" in fLine[49:55]:
          sList.append("0.0")
          sList.append(str(float(sLifeString[:-2].strip())*sUnit))
        elif "AP" in fLine[49:55]:
          sList.append("0.0")
          sList.append("0.0")
        elif fLine[49:55].strip():
          sUpper, sLower = gMatchError(str(sLifeString[:-2].strip()), str(fLine[49:55].strip()), str(fLine[49:55].strip()))
          sList.append(str(float(sUpper)*sUnit))
          sList.append(str(float(sLower)*sUnit))
        else:
          sList.append("0.0")
          sList.append("0.0")
        fLvlHalflife.append(sList)
        
      fGroundRead = True
    
    elif fLine[5:8] == "  G" and fGroundRead:           # Transition
    
      if "X" in fLine[9:18] or "Y" in fLine[9:18]:
        continue
    
      # Encountering a new transition, write to vector the previous one
      if sTrsEnergy != 0:
        fTrsSpinPa.append(sTrsSpinPa)
        fTrsCountPa.append(sTrsCountPa)
        fTrsSpinDa.append(sTrsSpinDa)
        fTrsCountDa.append(sTrsCountDa)
        fTrsEnergy.append(str(sTrsEnergy))
        if sTrsLife:
          fTrsLife.append(sTrsLife)
        else:
          fTrsLife.append(fNull)
        if sTrsBE2:
          fTrsBE2.append(sTrsBE2)
        else:
          fTrsBE2.append(fNull)
        if sTrsBM1:
          fTrsBM1.append(sTrsBM1)
        else:
          fTrsBM1.append(fNull)
        if sTrsMixing:
          fTrsMixing.append(sTrsMixing)
        else:
          fTrsMixing.append(fNull)       
        
      # Reset the details
      sTrsBM1 = fNull
      sTrsBE2 = fNull
      sTrsMixing = fNull
      sTrsLife = fNull
      sTrsEnergy = 0.0
      sTrsSpinPa = ""
      sTrsCountPa = ""
      sTrsSpinDa = ""
      sTrsCountDa = ""
       
      sTrsEnergy = float(fLine[9:18].strip())
      sFinEnergy = min(fLvlEnergy, key=lambda x:abs(x-(fLvlEnergy[-1] - sTrsEnergy))) # Find final state
      sIndex = fLvlEnergy.index(sFinEnergy)
      # Create transition ID
      sTrsLife = fLvlHalflife[-1]
      sTrsSpinPa = fLvlSpin[-1]
      sTrsCountPa = fLvlCount[-1]
      sTrsSpinDa = fLvlSpin[sIndex]
      sTrsCountDa = fLvlCount[sIndex]
      
      if fLine[41:55].strip():                # If there's a mixing ratio....
        sStr = ""
        if "GE" in fLine[41:55] or "GT" in fLine[41:55] or ">" in fLine[41:55]:
          sStr = "XX>"+re.sub(' +',' ',fLine[41:55].strip()[:-2])
        elif "LE" in fLine[41:55] or "LT" in fLine[41:55] or "<" in fLine[41:55]:
          sStr = "XX<"+re.sub(' +',' ',fLine[41:55].strip()[:-2])
        elif "AP" in fLine[41:55]:
          sStr = "XX="+re.sub(' +',' ',fLine[41:55].strip()[:-2])
        else:
          sStr = "XX="+re.sub(' +',' ',fLine[41:55].replace("+", " +").replace(" -", "-").strip()) # Gets rid of extra spaces
        sTrsMixing = gReturnB(sStr)


    elif fLine[5:8] == "B G":                 # B(.L) values
      sLine = fLine[9:].strip()
      if sLine[-1] == ")" and sLine[-10] == "(": 
        sLine = sLine[:-10]                   # Delete reference
      if sLine.count("$") > 1:
        sLine = sLine[:gFindIter(sLine, "$", 2)]
      sLine = sLine.translate(None, '()BW?')
      try:                                  # Assumption is made that only 2, at most, B() values listed
        sOne, sTwo = sLine.split('$')
        if sOne[:2] == "M1" and sTwo[:2] == "E2":
          sTrsBM1 = gReturnB(sOne)
          sTrsBE2 = gReturnB(sTwo)
        elif sOne[:2] == "E2" and sTwo[:2] == "M1":
          sTrsBE2 = gReturnB(sOne)
          sTrsBM1 = gReturnB(sTwo)
      except ValueError:
        if sLine[:2] == "E2":
          sTrsBE2 = gReturnB(sLine)
        elif sLine[:2] == "M1":
          sTrsBM1 = gReturnB(sLine)

          
  fInput.close()
  
  print " Read in", len(fLvlEnergy), "energy levels and", len(fTrsSpinPa), "transitions"

  # This chunk will find the energy of ..
  fEneS0 = "0.0"
  fEneF2 = "0.0"
  fEneF4 = "0.0"
  fEneS2 = "0.0"
  inSec0 = -1
  try:
    for j in xrange(2):           # .. the second 0+
      inSec0 = fLvlSpin.index("0+", inSec0 + 1)
    fEneS0 = str(fLvlEnergy[inSec0])
  except ValueError:
    fEneS0 = "0.0"
  try:
    inFir2 = fLvlSpin.index("2+") # .. the first 2+
    fEneF2 = str(fLvlEnergy[inFir2])
  except ValueError:
    fEneF2 = "0.0"
  try:
    inFir4 = fLvlSpin.index("4+") # .. the first 4+
    fEneF4 = str(fLvlEnergy[inFir4])
  except ValueError:
    fEneF4 = "0.0"
  inSec2 = -1
  try:
    for j in xrange(2):           # .. the second 2+
      inSec2 = fLvlSpin.index("2+", inSec2 + 1)
      fEneS2 = str(fLvlEnergy[inSec2])
  except:
    fEneS2 = "0.0"
  
 
  fBeta = ["0.0", "0.0", "0.0", "0.0"]
  fOverList = []
  for row, i in enumerate(fOverwrite):
    if i[0] == str(nucMass) and i[1] == str(nucProton):
      fBeta = [fOverwrite[row][3], fOverwrite[row][4], fOverwrite[row][5], fOverwrite[row][6]]
      fOverList.append(row)
 
  # Write to file
  for i in range(0, len(fTrsSpinPa)):
    # Find the nucleus
    sQSq = [0.0, 0.0]
    sRho = [0.0, 0.0, 0.0]
    sX = [0.0, 0.0]

    for j in range(len(fOverList)):
      
    
      listID = fTrsSpinPa[i] + fTrsCountPa[i] + fTrsSpinDa[i] + fTrsCountDa[i]
      overID = fOverwrite[fOverList[j]][7] + fOverwrite[fOverList[j]][8] + fOverwrite[fOverList[j]][9] + fOverwrite[fOverList[j]][10]
      if listID == overID: #overwrite
        if fOverwrite[fOverList[j]][11] != 0:
          fTrsBE2[i] = [fOverwrite[fOverList[j]][11], fOverwrite[fOverList[j]][12], fOverwrite[fOverList[j]][13]]
        sQSq = [fOverwrite[fOverList[j]][14], fOverwrite[fOverList[j]][15]]
        sRho = [fOverwrite[fOverList[j]][16], fOverwrite[fOverList[j]][17], fOverwrite[fOverList[j]][18]]
        sX = [fOverwrite[fOverList[j]][19], fOverwrite[fOverList[j]][20]]
        fOverList.pop(j)
        break
  
    fOutput.write(str(nucMass) + " " + str(nucProton) + " " + str(nucMass-nucProton))
    fOutput.write(" " + fBeta[0] + " " + fBeta[1] + " " + fBeta[2] + " " + fBeta[3])
    fOutput.write(" " + fEneS0 + " " + fEneF2 + " " + fEneF4 + " " + fEneS2)
    fOutput.write(" " + fTrsSpinPa[i] + " " + fTrsCountPa[i] + " " + fTrsSpinDa[i] + " " + fTrsCountDa[i])
    fOutput.write(" " + fTrsEnergy[i])
    fOutput.write(" " + fTrsLife[i][0] + " " + fTrsLife[i][1] + " " + fTrsLife[i][2])
    fOutput.write(" " + fTrsBE2[i][0] + " " + fTrsBE2[i][1] + " " + fTrsBE2[i][2])
    fOutput.write(" " + fTrsBM1[i][0] + " " + fTrsBM1[i][1] + " " + fTrsBM1[i][2])
    fOutput.write(" " + fTrsMixing[i][0] + " " + fTrsMixing[i][1] + " " + fTrsMixing[i][2])
    fOutput.write(" " + str(sQSq[0]) + " " + str(sQSq[1]))
    fOutput.write(" " + str(sRho[0]) + " " + str(sRho[1]) + " " + str(sRho[2]))
    fOutput.write(" " + str(sX[0]) + " " + str(sX[1]))
    fOutput.write("\n")

  # Write any transitions left in 'overwrite'.  Missing components need to be calculated
  for i in range(0, len(fOverList)):
    fOutput.write(str(nucMass) + " " + str(nucProton) + " " + str(nucMass-nucProton))
    fOutput.write(" " + fBeta[0] + " " + fBeta[1] + " " + fBeta[2] + " " + fBeta[3])
    fOutput.write(" " + fEneS0 + " " + fEneF2 + " " + fEneF4 + " " + fEneS2)
    fOutput.write(" " + fOverwrite[fOverList[i]][7] + " " + fOverwrite[fOverList[i]][8] + " " + fOverwrite[fOverList[i]][9] + " " + fOverwrite[fOverList[i]][10])
    fOutput.write(" " + "0.0") # Transition energy is missing in online spreadsheet
    fOutput.write(" 0.0 0.0 0.0") # Parent halflife is missing
    fOutput.write(" " + fOverwrite[fOverList[i]][11] + " " + fOverwrite[fOverList[i]][12] + " " + fOverwrite[fOverList[i]][13])
    fOutput.write(" 0.0 0.0 0.0") # No B(M1) information in online spreadsheet
    fOutput.write(" 0.0 0.0 0.0") # No mixing either
    fOutput.write(" " + fOverwrite[fOverList[i]][14] + " " + fOverwrite[fOverList[i]][15])
    fOutput.write(" " + fOverwrite[fOverList[i]][16] + " " + fOverwrite[fOverList[i]][17] + " " + fOverwrite[fOverList[i]][18])
    fOutput.write(" " + fOverwrite[fOverList[i]][19] + " " + fOverwrite[fOverList[i]][20])
    fOutput.write("\n")
  
  
