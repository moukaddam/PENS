import re
import math

def gReturnProton(fName):
  return {
    'NI': 28,
  }.get(fName, "000")
  
def gCheckNumber(fChar):
  try:
    int(fChar)
    return True
  except ValueError:
    return False
    
def gMatchError(fValue, fUpper, fLower):
  if "E" in fValue:                                   # Sometimes B() values are in exponent format
    fFront, fExponent = fValue.split("E")
    if len(fUpper) > 1 or len(fLower) > 1:
      sDiv = len(str(max(int(fUpper), int(fLower))))  # Biggest value
      fUpper = str(float(fUpper) / 10**(sDiv-1)) 
      fLower = str(float(fLower) / 10**(sDiv-1)) 
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
    sValue, sError = fString[3:].split(" ")
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
  elif fString[2] == "<":
    sVector.append(fString[3:])
    sVector.append("0")
    sVector.append(fString[3:])
  elif fString[2] == ">" or fString[3:5] == "AP": #Approximately
    sVector.append(fString[3:])
    sVector.append("0")
    sVector.append("0")
  else:
    print fString
  return sVector

  
fLvlEnergy = []
fLvlSpPa = [] # Easier to create a list of both spin & parity for counting purposes
fLvlSpin = []
fLvlCount = []
fLvlParity = []
fLvlLifetime = []

# Open the file, get the mass and proton number  
fInput = open('data/60_28.dat','r')
nucMass = int(fInput.read(3))
nucName = fInput.read(2)
nucProton = gReturnProton(nucName)

# Read through each line in the file, firstly looking for energy levels
sTrsBM1 = []
sTrsBE2 = []
sTrsMixing = []
sTrsEnergy = 0.0
sTrsID = "1"

for fLine in fInput:
  if len(fLvlEnergy) == 8:               # Limit of the first x energy levels
    break
  if fLine[5:8] != "  L" and fLine[5:8] != "  G" and fLine[5:8] != "B G":
    continue                              # Skip everything that isn't energy level, transition, transition details

  if fLine[5:8] == "  L":                 # Energy level 
    fLvlEnergy.append(float(fLine[9:18])) # Energy, omitting error (error will be in gamma)
    sSpin = fLine[21:25].strip()

    if len(sSpin) == 2:
      fLvlSpPa.append(sSpin)
      fLvlSpin.append(sSpin[0])           # Spin
      if sSpin[1] == "+":                 # Parity (+ = 1, - = 0)
        fLvlParity.append("1")       
      elif sSpin[1] == "-":
        fLvlParity.append("0")
      else:
        fLvlParity.append("x")
      fLvlCount.append(str(fLvlSpPa.count(sSpin)))
    else:                                 #  If not J+ format (J<10) then subbed with char
      fLvlSpPa.append("xx")
      fLvlSpin.append("x")
      fLvlParity.append("x")
      fLvlCount.append("x")
    
    sList = []                            # Lifetime
    if float(fLine[9:18]) == 0.0:         # (STABLE)
      sLifetime = ["0", "0", "0"]
      fLvlLifetime.append(sLifetime)
    else:
      sLifeString = fLine[39:49].strip()   
      if sLifeString[-2:] == "PS":         # PS
        sList.append(str(sLifeString[:-2].strip()))
      elif sLifeString[-2:] == "FS":       # FS
        sList.append(str(float(sLifeString[:-2].strip()) * 0.001))
      elif not sLifeString:                # (BLANK)
        sLifetime = ["0", "0", "0"]
        fLvlLifetime.append(sLifetime)
        continue
      else:
        print sLifeString
        print "ATTN: UNKNOWN LIFETIME UNIT"
        break
        
      if fLine[49] == "+":                # Error (+/-)
        sSubstring = fLine[49:60].strip()
        sMatch = re.search(r"[^a-zA-Z](-)[^a-zA-Z]", sSubstring)
        sUpper, sLower = gMatchError(str(sLifeString[:-2].strip()), str(sSubstring[1:sMatch.start(1)]), str(sSubstring[sMatch.start(1)+1:]))
        sList.append(sUpper)
        sList.append(sLower)
      elif fLine[49] == "G":              # Error (GT)
        sList.append("0")                 # .. 0 error
        sList.append("0")
      elif fLine[49] == "L":
        sList.append("0")
        sList.append(str(sLifeString[:-2].strip()))
      else:
        sUpper, sLower = gMatchError(str(sLifeString[:-2].strip()), str(fLine[49:60].strip()), str(fLine[49:60].strip()))
        sList.append(sUpper)
        sList.append(sLower)
      fLvlLifetime.append(sList)
  
  elif fLine[5:8] == "  G":                 # Transition
  
    # Encountering a new transition, write to file the previous one
    print sTrsID, sTrsEnergy
    if sTrsBE2:
      print "B(E2) =", sTrsBE2[0], sTrsBE2[1], sTrsBE2[2]
    if sTrsBM1:
      print "B(M1) =", sTrsBM1[0], sTrsBM1[1], sTrsBM1[2]
    if sTrsMixing:
      print "B(E2) =", sTrsMixing[0], sTrsMixing[1], sTrsMixing[2]
    # Reset the details
    sTrsBM1 = []
    sTrsBE2 = []
    sTrsMixing = []
    sTrsEnergy = 0.0
    sTrsID = "1"
     
    sTrsEnergy = float(fLine[9:18].strip())
    sFinEnergy = min(fLvlEnergy, key=lambda x:abs(x-(fLvlEnergy[-1] - sTrsEnergy))) # Find final state
    sIndex = fLvlEnergy.index(sFinEnergy)
    # Create transition ID
    sTrsID = "1" + fLvlSpin[-1] + fLvlParity[-1] + fLvlCount[-1] + fLvlSpin[sIndex] + fLvlParity[sIndex] + fLvlCount[sIndex]
    
    if fLine[42:55].strip():                # If there's a mixing ratio....
      sStr = "XX="+re.sub(' +',' ',fLine[42:55].strip())
      sTrsMixing = gReturnB(sStr)


  elif fLine[5:8] == "B G":                 # B(.L) values
    sLine = fLine[9:].strip().translate(None, '()BW')
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

fOutput = open('collate.dat', 'w') # TODO Change to append after testing
fOutput.write(str(nucMass) + " " + str(nucProton) + " " + str(nucMass-nucProton))


