import re, math, os, csv, requests, urllib2, sys

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
    'H': 1, 'HE': 2, 'LI': 3, 'BE': 4, 'B': 5, 'C': 6, 'N': 7, 'O': 8, 'F': 9, 
    'NE': 10, 'NA': 11, 'MG': 12, 'AL': 13, 'SI': 14, 'P': 15,  'S': 16,  'CL': 17, 'AR': 18, 'K': 19,
    'CA': 20, 'SC': 21, 'TI': 22, 'V': 23,  'CR': 24, 'MN': 25, 'FE': 26, 'CO': 27, 'NI': 28, 'CU': 29,
    'ZN': 30, 'GA': 31, 'GE': 32, 'AS': 33, 'SE': 34, 'BR': 35, 'KR': 36, 'RB': 37, 'SR': 38, 'Y': 39,
    'ZR': 40, 'NB': 41, 'MO': 42, 'TC': 43, 'RU': 44, 'RH': 45, 'PD': 46, 'AG': 47, 'CD': 48, 'IN': 49, 
    'SN': 50, 'SB': 51, 'TE': 52, 'I': 53, 'XE': 54, 'CS': 55, 'BA': 56, 'LA': 57, 'CE': 58, 'PR': 59, 
    'ND': 60, 'PM': 61, 'SM': 62, 'EU': 63, 'GD': 64, 'TB': 65, 'DY': 66, 'HO': 67, 'ER': 68, 'TM': 69, 
    'YB': 70, 'LU': 71, 'HF': 72, 'TA': 73, 'W': 74, 'RE': 75, 'OS': 76, 'IR': 77, 'PT': 78, 'AU': 79, 
    'HG': 80, 'TL': 81, 'PB': 82, 'BI': 83, 'PO': 84, 'AT': 85, 'RN': 86, 'FR': 87, 'RA': 88, 'AC': 89, 
    'TH': 90, 'PA': 91,  'U': 92, 'NP': 93, 'PU': 94, 'AM': 95, 'CM': 96, 'BK': 97, 'CF': 98, 'ES': 99
  }.get(fName, "00")
         
def gReturnTime(fUnit):
  # Function to return conversion of [time] to PS
  return {
    'PS': 1.0, 'FS': 0.001, 'NS': 1000., 'US': 1.0E6, 'MS': 1.0E9, 'M': 6.0E13, 'S': 1.0E12, 'H': 3.6E15, 'Y': 3.154E19, 'D': 8.64E16, 'AS':1E-6
  }.get(fUnit, "??")
  
def gCheckNumber(fChar):
  # Function to check if string can be converted to a number
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
  
def gGetIndex(fFileName):
  # Split name into number and name
  if gCheckNumber(fFileName[-1]):
    print "INCORRECT FILE NAME", fFileName
    sys.exit()
  sElement = fFileName.strip('0123456789')
  sMass = str(fFileName[:len(fFileName)-len(sElement)])
  if len(sMass) == 1:
    sMass = "0" + sMass
  if len(sMass) == 2:
    sMass = "0" + sMass
  sElement = str(gReturnProton(sElement))
  if len(sElement) == 1:
    sElement = "0" + sElement
  if len(sElement) == 2:
    sElement = "0" + sElement
  return sMass + sElement
  
# Import google csv in to overwrite list
print "Reading in from online spreadsheet..."
try:
  fCSVURL = 'https://docs.google.com/spreadsheet/ccc?key=178pS1nT7PEsmTwCdeJViEfrO2up3cMdzOgL7vO2Gyuk&output=csv'
  fInput = urllib2.urlopen(fCSVURL)
  fReader = csv.reader(fInput)
  fOverwrite = list(fReader)
  print "... SUCCESS!"
  print "... Read in", len(fOverwrite), "lines"
except urllib2.URLError:
  print "... FAILURE!"
#fOverwrite = []

fNull = ["0.0", "0.0", "0.0"]

# In turn, open each file within the data folder
fOutput = open('collate.dat', 'w') 
for i in sorted(os.listdir(os.getcwd() + "/data"), key=gGetIndex):

  fLvlEnergy = []
  fLvlSpin = []
  fLvlSpinTent = []
  fLvlCount = []
  fLvlCountTent = []
  fLvlHalflife = []

  fTrsBM1 = []
  fTrsBE2 = []
  fTrsMixing = []
  fTrsEnergy = []
  fTrsBranch = []
  fTrsIndPa = []
  fTrsIndDa = []
  fTrsLife = []
  fTrsAlpha = []
  fTrsQSq = []
  fTrsRho = []
  fTrsX =[]

  # Open the file, get the mass and proton number  
  fInput = open("data/" + i,'r')
  nucMass = int(fInput.read(3))
  nucName = fInput.read(2)
  nucProton = gReturnProton(nucName.strip())
  
  print "Reading in " + str(nucMass) + nucName, nucProton
 
  sTrsBM1 = []
  sTrsBE2 = []
  sTrsMixing = []
  sTrsBranch = []
  sTrsEnergy = 0.0
  
  fGroundRead = False

  # Read through each line in the file, firstly looking for energy levels
  for fLine in fInput:
    
    #if len(fLvlEnergy) == 20:               # Limit of the first x energy levels
    #  break
    if fLine[5:8] != "  L" and fLine[5:8] != "  G" and fLine[5:8] != "B G" and fLine[5:8] != "S G":
      continue                              # Skip everything that isn't energy level, transition, transition details

    if fLine[5:8] == "  L":                 # Energy level 
      if not gCheckNumber(fLine[9:19]):       # .. skipping the +X levels
        continue
      #print(repr(fLine[9:19]))
      fLvlEnergy.append(float(fLine[9:19])) # Energy, omitting error 
      sSpin = fLine[21:39].strip()
      # Check for definitive spin/parity assignment (must have + or -, and must be a number without either of those characters)
      if any(sChar in sSpin for sChar in ["+", "-"]) and gCheckNumber(sSpin.translate(None, '+-/')):
        fLvlSpin.append(sSpin)
        sCount = fLvlSpin.count(sSpin)
        fLvlCount.append(str(sCount))
        # Must also add these to the 'tentative list' so that an accurate count is made
        fLvlSpinTent.append(sSpin)
        sCount = fLvlSpinTent.count(sSpin)
        fLvlCountTent.append(str(sCount))
      elif any(sChar in sSpin for sChar in ["L", "G", "J", "NOT", ">", "AP"]):
        fLvlSpin.append("-1")
        fLvlCount.append("-1")
        fLvlSpinTent.append("-1")
        fLvlCountTent.append("-1")
      elif len(sSpin) != 0:
        # The tentative spin assignments are essentially comments with little consistency
        sParity = ""
        if "&" in sSpin:
          sSpin = sSpin[0:sSpin.find("&")]
        if "AND" in sSpin:
          sSpin = sSpin[0:sSpin.find("A")]
        if "OR" in sSpin:
          sSpin = sSpin[0:sSpin.find("O")]
        if any(sChar in sSpin[-1] for sChar in ["+", "-"]):
          sParity = sSpin[-1]        
        sSpin = sSpin.translate(None, '()[]')
        if "," in sSpin:
          sSpin = sSpin[0:sSpin.find(",")] + sParity
        if ":" in sSpin:
          sSpin = sSpin[0:sSpin.find(":")] + sParity
        if "TO" in sSpin:
          sSpin = sSpin[0:sSpin.find("T")] + sParity
        if "to" in sSpin:
          sSpin = sSpin[0:sSpin.find("t")] + sParity
        fLvlSpinTent.append(sSpin)
        sCount = fLvlSpinTent.count(sSpin)
        fLvlCountTent.append(str(sCount))
        # Must also fill the 'confirmed list' with unknowns, to avoid mismatched lists
        fLvlSpin.append("-1")
        fLvlCount.append("-1")
      else:                                 #  If completly unknown, make -1
        fLvlSpin.append("-1")
        fLvlCount.append("-1")
        fLvlSpinTent.append("-1")
        fLvlCountTent.append("-1")
      
      sList = []                            # Halflife
      sLifeString = fLine[39:49].strip() 
      if "STABLE" in sLifeString:         # (STABLE)
        sHalflife = ["-1.0", "0.0", "0.0"] # -1.0 ps for stable
        fLvlHalflife.append(sHalflife)
      else:
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
        elif gCheckNumber(fLine[49:55].strip()):
          sUpper, sLower = gMatchError(str(sLifeString[:-2].strip()), str(fLine[49:55].strip()), str(fLine[49:55].strip()))
          sList.append(str(float(sUpper)*sUnit))
          sList.append(str(float(sLower)*sUnit))
        else:
          sList.append("0.0")
          sList.append("0.0")
        fLvlHalflife.append(sList)
        
      fGroundRead = True
    
    elif fLine[5:8] == "  G" and fGroundRead:           # Transition
    
      if not gCheckNumber(fLine[9:18]):
        continue
    
      # Encountering a new transition, write to vector the previous one
      if sTrsEnergy != 0:
        fTrsIndPa.append(sIndexPa)
        fTrsIndDa.append(sIndexDa)
        fTrsEnergy.append(str(sTrsEnergy))
        fTrsBranch.append(sTrsBranch)
        if sTrsAlpha:
          fTrsAlpha.append(sTrsAlpha)
        else:
          fTrsAlpha.append(fNull)
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
      sTrsAlpha = fNull
      sTrsEnergy = 0.0
      sTrsBranch = ["0.0", "0.0"]
       
      sTrsEnergy = float(fLine[9:18].strip())  
      if len(fLine[21:29].strip()) != 0 and gCheckNumber(fLine[21:29].strip()):
        sTrsBranch = [fLine[21:29].strip(), "0.0"]
        if len(fLine[29:31].strip()) != 0 and gCheckNumber(fLine[29:31].strip()):
          sBrErr = fLine[29:31].strip()
          sA, sB = gMatchError(fLine[21:29].strip(), sBrErr, sBrErr)
          sTrsBranch = [fLine[21:29].strip(), sA]
      sFinEnergy = min(fLvlEnergy, key=lambda x:abs(x-(fLvlEnergy[-1] - sTrsEnergy))) # Find final state
      sIndexDa = fLvlEnergy.index(sFinEnergy)
      sIndexPa = len(fLvlEnergy) - 1
      
      if fLine[41:55].strip():                # If there's a mixing ratio....
        sStr = ""
        if "GE" in fLine[41:55] or "GT" in fLine[41:55] or ">" in fLine[41:55]:
          sStr = "XX>"+re.sub(' +',' ',fLine[41:55].strip()[:-2])
        elif "LE" in fLine[41:55] or "LT" in fLine[41:55] or "<" in fLine[41:55]:
          sStr = "XX<"+re.sub(' +',' ',fLine[41:55].strip()[:-2])
        elif "AP" in fLine[41:55]:
          sStr = "XX="+re.sub(' +',' ',fLine[41:55].strip()[:-2])
        elif "SY" in fLine[41:55]:
          sStr = "XX="+fLine[41:55].translate(None, "SY")
        else:
          sStr = "XX="+re.sub(' +',' ',fLine[41:55].replace("+", " +").replace(" -", "-").strip()) # Gets rid of extra spaces
        sTrsMixing = gReturnB(sStr)


    elif fLine[5:8] == "B G":                 # B(.L) values
      sLine = fLine[9:].strip()
      if sLine[-1] == ")" and sLine[-10] == "(": 
        sLine = sLine[:-10]                   # Delete reference
      if "if" in sLine:
        sLine = sLine[0:sLine.find("i")]
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
          
    elif fLine[5:8] == "S G":                 # alpha values
      if "NC" in fLine and not "CC" in fLine:
        sTrsAlpha = fNull  #Remove last CC
      if "CC=" in fLine:
        if "CC" in fLine and "NC" in fLine:
          continue
        
        # Only interested in total (not K, L, etc)
        sVector = []
        if "$" in fLine:
          sString = fLine[fLine.index("=")+1:fLine.index("$")]
        else:
          sString = fLine[fLine.index("=")+1:].strip()
        if " " in sString:
          sValue = sString[:sString.index(" ")]
          sErrA = sString[sString.index(" "):]
          sErrB = sErrA
          if "+" in sErrA:
            sErrA = sErrA[0:sErrA.find("-")]
            sErrB = sErrA[sErrA.find("-"):]
          sUpper, sLower = gMatchError(sValue, sErrA, sErrB)
        else:
          sValue = sString.strip()
          sUpper = 0.0
          sLower = 0.0
        sVector.append(sValue)
        sVector.append(sUpper)
        sVector.append(sLower) # for the sake of consistency
        sTrsAlpha = sVector  
#    if "|r{+2}" in fLine and fGroundRead:
#      print fLvlEnergy[-1], sTrsEnergy, sTrsSpinPa, sTrsCountPa, sTrsSpinDa, sTrsCountDa
#      print fLine    
          
  fInput.close()
  
  print " Read in", len(fLvlEnergy), "energy levels and", len(fTrsIndPa), "transitions"

  fBeta = ["0.0", "0.0", "0.0", "0.0"]
  fOverList = []
  # Find the nucleus in the overwrite array, replace beta information
  for row, i in enumerate(fOverwrite):
    if i[0] == str(nucMass) and i[1] == str(nucProton):
      fBeta = [fOverwrite[row][3], fOverwrite[row][4], fOverwrite[row][5], fOverwrite[row][6]]
      fOverList.append(row)
 
  # Write to file
  fOutput.write("#N\n")
  fOutput.write(str(nucMass) + " " + str(nucProton) + " " + str(nucMass-nucProton))
  fOutput.write(" " + fBeta[0] + " " + fBeta[1] + " " + fBeta[2] + " " + fBeta[3] + "\n")
  
  fOutput.write("#L\n")
  fOutput.write(str(len(fLvlEnergy)) + "\n")
  for i in range(0, len(fLvlEnergy)):
    fOutput.write(str(fLvlEnergy[i]))
    sParity = "0"
    if fLvlSpin[i][-1] == "+":
      sParity = "1"
    elif fLvlSpin[i][-1] == "-":
      sParity = "-1"
    if fLvlSpin[i] == "-1":
      fOutput.write(" " + fLvlSpin[i] + " " + sParity + " " + fLvlCount[i])
    else:
      sRes = fLvlSpin[i]
      if '/' in sRes:
        sNum,sDen = fLvlSpin[i].translate(None, '+-').split( '/' )
        sRes = str(float(sNum)/float(sDen))
      fOutput.write(" " + sRes + " " + sParity + " " + fLvlCount[i])
    
    sParity = "0"
    if fLvlSpinTent[i][-1] == "+":
      sParity = "1"
    elif fLvlSpinTent[i][-1] == "-":
      sParity = "-1"
    if fLvlSpinTent[i] == "-1":
      fOutput.write(" " + fLvlSpinTent[i] + " " + sParity + " " + fLvlCountTent[i])
    else:
      sRes = fLvlSpinTent[i]
      if '/' in sRes:
        sNum,sDen = fLvlSpinTent[i].translate(None, '+-').split( '/' )
        sRes = str(float(sNum)/float(sDen))
      fOutput.write(" " + sRes + " " + sParity + " " + fLvlCountTent[i])

    fOutput.write(" " + fLvlHalflife[i][0] + " " + fLvlHalflife[i][1] + " " + fLvlHalflife[i][2] + "\n")

  # Overwrite values
  # Loop through each transition...
  for i in range(0, len(fTrsIndPa)):
    
    sQSq = [0.0, 0.0]
    sRho = [0.0, 0.0, 0.0]
    sX = [0.0, 0.0]
    # Loop through each overwrite row...
    for j in range(len(fOverList)):
      # Compare transition IDs    
      listID = fLvlSpin[fTrsIndPa[i]] + fLvlCount[fTrsIndPa[i]] + fLvlSpin[fTrsIndDa[i]] + fLvlCount[fTrsIndDa[i]]
      overID = fOverwrite[fOverList[j]][7] + fOverwrite[fOverList[j]][8] + fOverwrite[fOverList[j]][9] + fOverwrite[fOverList[j]][10]
      if listID == overID: #overwrite
        if fOverwrite[fOverList[j]][11] != 0:
          fTrsBE2[i] = [fOverwrite[fOverList[j]][11], fOverwrite[fOverList[j]][12], fOverwrite[fOverList[j]][13]]
        if fOverwrite[fOverList[j]][14] != 0:
          fTrsBM1[i] = [fOverwrite[fOverList[j]][14], fOverwrite[fOverList[j]][15], fOverwrite[fOverList[j]][16]]
        sQSq = [fOverwrite[fOverList[j]][17], fOverwrite[fOverList[j]][18]]
        sRho = [fOverwrite[fOverList[j]][19], fOverwrite[fOverList[j]][20], fOverwrite[fOverList[j]][21]]
        sX = [fOverwrite[fOverList[j]][22], fOverwrite[fOverList[j]][23]]
        fOverList.pop(j)
        break
        
    fTrsQSq.append(sQSq)
    fTrsRho.append(sRho)
    fTrsX.append(sX)



  fOutput.write("#T\n")
  fOutput.write(str(len(fTrsIndPa) + len(fOverList)) + "\n")
  for i in range(0, len(fTrsIndPa)):
    
    fOutput.write(str(fTrsIndPa[i]) + " " + str(fTrsIndDa[i]))
    fOutput.write(" " + fTrsBranch[i][0] + " " + fTrsBranch[i][1])
    fOutput.write(" " + fTrsBE2[i][0] + " " + fTrsBE2[i][1] + " " + fTrsBE2[i][2])
    fOutput.write(" " + fTrsBM1[i][0] + " " + fTrsBM1[i][1] + " " + fTrsBM1[i][2])
    fOutput.write(" " + fTrsMixing[i][0] + " " + fTrsMixing[i][1] + " " + fTrsMixing[i][2])
    fOutput.write(" " + str(fTrsQSq[i][0]) + " " + str(fTrsQSq[i][1]))
    fOutput.write(" " + str(fTrsRho[i][0]) + " " + str(fTrsRho[i][1]) + " " + str(fTrsRho[i][2]))
    fOutput.write(" " + str(fTrsX[i][0]) + " " + str(fTrsX[i][1]))
    fOutput.write(" " + str(fTrsAlpha[i][0]) + " " + str(fTrsAlpha[i][1]) + " " + str(fTrsAlpha[i][2]))
    fOutput.write("\n")

  # Write any transitions left in 'overwrite'.  Missing components need to be calculated
  for i in range(0, len(fOverList)):
    # Find parent ID
    c = 1
    for k, j in enumerate(fLvlSpin):
      if j == fOverwrite[fOverList[i]][7]:
        if c == int(fOverwrite[fOverList[i]][8]):
          fOutput.write(str(k))
        c += 1
    fOutput.write(" ")
    # Find daughter ID
    c = 1
    for k, j in enumerate(fLvlSpin):
      if j == fOverwrite[fOverList[i]][9]:
        if c == int(fOverwrite[fOverList[i]][10]):
          fOutput.write(str(k))
        c += 1

    fOutput.write(" 0.0 0.0") # No branching ratio in online spreadsheet
    fOutput.write(" " + fOverwrite[fOverList[i]][11] + " " + fOverwrite[fOverList[i]][12] + " " + fOverwrite[fOverList[i]][13])
    fOutput.write(" " + fOverwrite[fOverList[i]][14] + " " + fOverwrite[fOverList[i]][15] + " " + fOverwrite[fOverList[i]][16])
    fOutput.write(" 0.0 0.0 0.0") # No mixing either
    fOutput.write(" " + fOverwrite[fOverList[i]][17] + " " + fOverwrite[fOverList[i]][18])
    fOutput.write(" " + fOverwrite[fOverList[i]][19] + " " + fOverwrite[fOverList[i]][20] + " " + fOverwrite[fOverList[i]][21])
    fOutput.write(" " + fOverwrite[fOverList[i]][22] + " " + fOverwrite[fOverList[i]][23])
    fOutput.write(" 0.0 0.0 0.0") # No alpha either
    fOutput.write("\n")
    
fOutput.close()
