import re
import math

def gReturnProton(fName):
  return {
    'NI': 28,
  }.get(fName, "???")
  
def gCheckNumber(fChar):
  try:
    int(fChar)
    return True
  except ValueError:
    return False
    
def gMatchError(fValue, fError):
  try:
    fMain, fFraction = fValue.split('.')
    fPrecision = len(fFraction)
    fError = float(fError) / 10**fPrecision
    return str(fError)
  except ValueError:
    return fError

  
fLvlEnergy = []
fLvlSpPa = [] # Easier to create a list of both spin & parity for counting purposes
fLvlSpin = []
fLvlCount = []
fLvlParity = []
fLvlLifetime = []

# Open the file, get the mass and proton number  
fInput = open('data/62_28.dat','r')
nucMass = int(fInput.read(3))
nucName = fInput.read(2)
nucProton = gReturnProton(nucName)

# Read through each line in the file, firstly looking for energy levels
for fLine in fInput:
  if len(fLvlEnergy) == 100:               # Limit of the first x energy levels
    break
  if fLine[6] == "c" or fLine[5] == "X":
    continue                              # Skip comments and cross-references
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
      elif not sLifeString:                # (BLANK)
        sLifetime = ["0", "0", "0"]
        fLvlLifetime.append(sLifetime)
        continue
      else:
        print "ATTN: UNKNOWN LIFETIME UNIT"
        break
        
      if fLine[49] == "+":                # Error (+/-)
        sSubstring = fLine[49:60].strip()
        sMatch = re.search(r"[^a-zA-Z](-)[^a-zA-Z]", sSubstring)
        sList.append(gMatchError(str(sLifeString[:-2].strip()), str(sSubstring[1:sMatch.start(1)])))
        sList.append(gMatchError(str(sLifeString[:-2].strip()), str(sSubstring[sMatch.start(1)+1:])))
      elif fLine[49] == "G":              # Error (GT)
        sList.append("0")                 # .. 0 error
        sList.append("0")
      elif fLine[49] == "L":
        sList.append("0")
        sList.append(str(sLifeString[:-2].strip()))
      else:
        sList.append(gMatchError(str(sLifeString[:-2].strip()), str(fLine[49:60].strip())))
        sList.append(gMatchError(str(sLifeString[:-2].strip()), str(fLine[49:60].strip())))
      fLvlLifetime.append(sList)
  
  if fLine[5:8] == "  G":                 # Transition
    sTrsEnergy = float(fLine[9:18].strip())
    sFinEnergy = min(fLvlEnergy, key=lambda x:abs(x-(fLvlEnergy[-1] - sTrsEnergy))) # Find final state
    sIndex = fLvlEnergy.index(sFinEnergy)
    # Create transition ID
    sID = "1" + fLvlSpin[-1] + fLvlParity[-1] + fLvlCount[-1] + fLvlSpin[sIndex] + fLvlParity[sIndex] + fLvlCount[sIndex]

  if fLine[5:8] == "B G":                 # B(.L) values
    sLine = fLine[9:].strip().translate(None, '()BW')
    try:                                  # Assumption is made that only 2, at most, B() values listed
      sOne, sTwo = sLine.split('$')
      print sOne, sTwo
    except ValueError:
      print sLine

fInput.close()

#for i in range(0, len(fLvlEnergy)-1):
#  if not fLvlLifetime[i][0] == "0":
#    print str(fLvlEnergy[i]) + "\t" + fLvlSpin[i] + fLvlParity[i] + "\t" + str(fLvlLifetime[i][0]) + " +" + str(fLvlLifetime[i][1]) + " -" + str(fLvlLifetime[i][2])

fOutput = open('collate.dat', 'w')
fOutput.write(str(nucMass) + " " + str(nucProton) + " " + str(nucMass-nucProton))


