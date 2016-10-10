# List of functions used in the parser.  Many of the gProcess* functions can be combined in to one
# large function, but will remaim separate for now for debugging purposes.

# ---------------------------------------------
# This function returns proton number from name
def gReturnProton(fName):
  return {
    'H': 1,   'HE': 2,  'LI': 3,  'BE': 4,   'B': 5,   'C': 6, 'N': 7, 'O': 8, 'F': 9, 
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


# ---------------------------------------------
# This function simply checks if string can be converted to a number
def gCheckNumber(fChar):
  try:
    float(fChar)
    return True
  except ValueError:
    return False
    

# ---------------------------------------------
# Finds the nth occurence of fSub in fString
def gFindIter(fString, fSub, fN):
  fStart = fString.find(fSub)
  while fStart >= 0 and fN > 1:
    fStart = fString.find(fSub, fStart+len(fSub))
    fN -= 1
  return fStart


# ---------------------------------------------
# Function to return conversion of [time] to PS
def gReturnTime(fUnit):
  return {
    'PS': 1.0, 'FS': 0.001, 'NS': 1000., 'US': 1.0E6, 'MS': 1.0E9, 'M': 6.0E13, 'S': 1.0E12, 'H': 3.6E15, 'Y': 3.154E19, 'D': 8.64E16, 'AS':1E-6
  }.get(fUnit, "??")
  

# ---------------------------------------------
# Errors in ENSDF are the last X digts of the value, this function changes error to
# same magnitude as value e.g. 2.3(3) becomes 2.3 0.3
def gMatchError(fValue, fUpper, fLower):

  fPrecision = 0
  if "E" in fValue:                                   # Sometimes values are in exponent format
    fFront, fExponent = fValue.split("E")
    if "." in fFront:
      fMain, fFraction = fFront.split('.')
      fPrecision = len(fFraction)
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

# ---------------------------------------------
# This function sorts the list of files by mass number then element
def gGetIndex(fFileName):
  if gCheckNumber(fFileName[-1]): #If last digit is number, return error
    print "INCORRECT FILE NAME", fFileName
    sys.exit()
  # Split name into number and name
  sElement = fFileName.strip('0123456789')
  sMass = str(fFileName[:len(fFileName)-len(sElement)])
  # Make a 6 digit code identifying element, which can be sorted numerically
  while len(sMass) < 3:
    sMass = "0" + sMass   
  sElement = str(gReturnProton(sElement))
  while len(sElement) < 3:
    sElement = "0" + sElement
  return sMass + sElement
  

# ---------------------------------------------  
# This function converts the comments of the spin/parity into a final number
def gProcessSpin(fSpinString):
  fSpin = ["-1", "0", "-1", "0"]      # The counting must occur later
  if len(fSpinString) == 0:
    return fSpin
  
  # Obtain the tentative flags, then strip out the ()
  sTentative = [False, False]
  if fSpinString[0] == "(":
    sTentative = [True, True]
    if fSpinString[-1] != ")":
      sTentative = [True, False]
  sString = fSpinString.translate(None, '()')
  
  if len(sString.translate(None, '+-')) == 0:
    fSpin[1 + 2*int(sTentative[1])] = sString
  elif gCheckNumber(sString.translate(None, '+-/')): 
    # Check to see if there's only one number listed
    fSpin[0 + 2*int(sTentative[0])] = sString.translate(None, '+-')
    if sString[-1] == "+" or sString[-1] == "-":
      fSpin[1 + 2*int(sTentative[1])] = sString[-1]
  elif any(c.isalpha() for c in sString) or ">" in sString or "<" in sString:
    # Skipping "TO", "GE" etc
    s = 1
  else:
    # Get the first number
    sFirst = -1
    sLast = -1
    for sChar in sString:
      if gCheckNumber(sChar) and sFirst < 0:
        sFirst = sString.index(sChar)
      elif not gCheckNumber(sChar) and sFirst != -1 and sLast == -1 and sChar != "/":
        sLast = sString.index(sChar)
        break
    fSpin[0 + 2*int(sTentative[0])] = sString[sFirst:sLast]
    if sString[sLast] == "+" or sString[sLast] == "-":
      fSpin[1 + 2*int(sTentative[1])] = sString[sLast]
      
  # Convert fraction to decimal
  if "/" in fSpin[0]:
    sNum,sDen = fSpin[0].split('/')
    fSpin[0] = str(float(sNum)/float(sDen))
  if "/" in fSpin[2]:
    sNum,sDen = fSpin[2].split('/')
    fSpin[2] = str(float(sNum)/float(sDen))
 
  # Let's just convert +/- to +1, -1
  if fSpin[1] == "+":
    fSpin[1] = "1"
  if fSpin[1] == "-":
    fSpin[1] = "-1"
  if fSpin[3] == "+":
    fSpin[3] = "1"
  if fSpin[3] == "-":
    fSpin[3] = "-1"  
    
  # Lastly, transfer 'confirmed' data to tentative too
  if fSpin[0] != "-1":
    fSpin[2] = fSpin[0]
  if fSpin[1] != "0":
    fSpin[3] = fSpin[1]
    
  # Check that everything in the array is a number
  for x in fSpin:
    if not gCheckNumber(x):
      print "ERROR: Spin not a number:\n", fSpinString, fSpin
      sys.exit()
    
  return fSpin


# ---------------------------------------------
# This function converts the half-life to a standard (ps) number
def gProcessLife(fValStr, fErrStr):

  fHalf = ["0.0", "0.0", "0.0"]
  if "EV" in fValStr: # Half life sometimes given as width, ignore it
    return fHalf

  # The string is given as VALUE UNIT, take the value and
  # convert to a number to allow multiplication later
  fValue = float(fValStr[:fValStr.index(' ')])
  if not gCheckNumber(fValue):
    # Check if it is actually a number
    print "ERROR: Half-life is not a number:\n", fValStr
    sys.exit()
    
  # Obtain the unit of measurement, and a float that converts it to PS
  fUnit = gReturnTime(fValStr[fValStr.index(' ')+1:].translate(None, '?').strip())
  if gCheckNumber(fUnit):
    fHalf[0] = str(fValue * fUnit)
  else:
    print "ERROR: Unknown half-life unit:\n", fValStr
    sys.exit()

  # Then we need to deal with the error
  # Simple if there is none
  if not fErrStr or fErrStr == "AP" or fErrStr == "SY":
    # Do nothing, error already set to 0
    s = 1
  elif gCheckNumber(fErrStr):
    # Need to match the error before multiplying by time unit
    sError, sN = gMatchError(str(fValue), fErrStr, fErrStr)
    fHalf[1] = str(float(sError) * fUnit)
    fHalf[2] = str(float(sError) * fUnit)
  elif fErrStr[0] == "+" and "-" in fErrStr:
    sU, sL = gMatchError(str(fValue), fErrStr[1:fErrStr.index('-')], fErrStr[fErrStr.index('-')+1:])
    fHalf[1] = str(float(sU) * fUnit)
    fHalf[2] = str(float(sL) * fUnit)
  elif fErrStr == "LE" or fErrStr == "LT":
    fHalf[2] = fHalf[0]
  elif fErrStr == "GE" or fErrStr == "GT":
    fHalf[1] = fHalf[0]
  else:
    print "ERROR: Unknown half-life error:\n", fValStr, fErrStr
  
  # Check everything is a number
  for x in fHalf:
    if not gCheckNumber(x):
      print "ERROR: Half-life not a number:\n", fValStr, fErrStr
      sys.exit()
    
  return fHalf
  
  
# ---------------------------------------------
# This function processes branching ratio
def gProcessBranch(fValStr, fErrStr):

  fBranch = ["0", "0", "0"]
  fValStr = fValStr.translate(None, '()')

  if gCheckNumber(fValStr):
    fBranch[0] = fValStr
    if gCheckNumber(fErrStr):
      sE, sN = gMatchError(fBranch[0], fErrStr, fErrStr)
      fBranch[1] = sE
      fBranch[2] = sE
    elif fErrStr == "LT" or fErrStr == "LE":
      fBranch[2] = fBranch[0]
    elif fErrStr == "GT" or fErrStr == "GE":
      fBranch[1] = fBranch[0]
    elif fErrStr and fErrStr != "AP" and fErrStr != "CA":
      # 242Am lists as CA, assuming it means AP
      print "ERROR: Unknown branching error:\n", fValStr, fErrStr
      sys.exit()
  elif fValStr and fValStr != "WEAK":
    print "ERROR: Unknown branching:\n", fValStr, fErrStr
    sys.exit()

  # Check numbers
  for x in fBranch:
    if not gCheckNumber(x):
      print "ERROR: Branching not a number:\n", fValStr, fErrStr
      sys.exit()
      
  return fBranch


# ---------------------------------------------
# This function processes mixing ratio
def gProcessMixing(fValStr, fErrStr):

  fMixing = ["0", "0", "0"]

  if gCheckNumber(fValStr):
    fMixing[0] = fValStr
    # Then deal with error
    if gCheckNumber(fErrStr):
      sE, sN = gMatchError(fMixing[0], fErrStr, fErrStr)
      fMixing[1] = sE
      fMixing[2] = sE
    elif fErrStr:
      if fErrStr[0] == "+":
        sU, sL = gMatchError(fMixing[0], fErrStr[1:fErrStr.index('-')], fErrStr[fErrStr.index('-')+1:])
        fMixing[1] = sU
        fMixing[2] = sL
      elif fErrStr[0] == "-":
        sL, sU = gMatchError(fMixing[0], fErrStr[1:fErrStr.index('+')], fErrStr[fErrStr.index('+')+1:])
        fMixing[1] = sU
        fMixing[2] = sL
      elif fErrStr == "LT" or fErrStr == "LE":
        fMixing[2] = fMixing[0]
      elif fErrStr == "GT" or fErrStr == "GE":
        fMixing[1] = fMixing[0]
      elif fErrStr != "AP" and fErrStr != "SY":
        print "ERROR: Unknown mixing error:\n", fValStr, fErrStr
        sys.exit()
  else:
    print "ERROR: Unknown mixing ratio:\n", fValStr, fErrStr
    sys.exit()
  
  # Check numbers
  for x in fMixing:
    if not gCheckNumber(x):
      print "ERROR: Branching not a number:\n", fValStr, fErrStr
      sys.exit()
  
  return fMixing
  
  
# ---------------------------------------------
# This function processes conversion coefficient
def gProcessAlpha(fValStr, fErrStr):  

  fAlpha = ["0", "0"]
  if gCheckNumber(fValStr):
    fAlpha[0] = fValStr
    if gCheckNumber(fErrStr):
      sE, sN = gMatchError(fAlpha[0], fErrStr, fErrStr)
      fAlpha[1] = sE
    elif not fValStr:
      print "ERROR: Unexpected cc error:\n", fValStr, fErrStr
      sys.exit()
  else:
    print "ERROR: Unknown conversion coefficient:\n", fValStr, fErrStr
    sys.exit()

  # Check numbers
  for x in fAlpha:
    if not gCheckNumber(x):
      print "ERROR: Conversion coefficient not a number:\n", fValStr, fErrStr
      sys.exit()
      
  return fAlpha
      
# ---------------------------------------------
# This function processes B(mL) values
def gProcessB(fString):
 
  # Create the B(mL) array that is returned at the end
  fResults = []
  while len(fResults) < 32:
    fResults.append("0")  
  
  # The first 9 characters are just B(mL) flags
  # Every B(mL) value is delimited by a $ symbol, split into array
  fArray = fString[9:].split("$")
  for sEntry in fArray:
    # Sometimes delimiter $ is listed even when there's only 1 value
    if len(sEntry.strip()) == 0 or sEntry[0] != "B":
      continue
      
    sConfirmed = True
    if "(" in sEntry: # Unfortunately includes listed references (~16 occurences, no easy way around it)
      sConfirmed = False

    # Remove the BW and tentative identifiers, strip whitespace at front and end
    sStripped = sEntry.translate(None, 'BW()?').strip()
    
    # First two characters identify the mL, convert to a vector element ID
    sM = sStripped[0]
    if sM == "M":
      sM = int(1)
    elif sM == "E":
      sM = int(0)
    else:
      print "ERROR: Unknown multipolarity " + sStripped[:2] + " in:\n " + fString + "\n" + sEntry[:5]
      sys.exit()
    sL = int(sStripped[1])
    sID = (sM * 16) + ((sL - 1) * 4)
    fResults[sID+3] = str(int(sConfirmed))
    
    sStripped = sStripped[2:].strip()
    # Then we need to identify the type of value (=, <, >)
    if len(sStripped[0].translate(None, '=><')) == 1:
      # In this situation we have AP (approx), LT, LE, GE, GT, replace with symbols =><
      sStripped = sStripped.replace("AP ", "=")
      sStripped = sStripped.replace("LT ", "<")
      sStripped = sStripped.replace("LE ", "<")
      sStripped = sStripped.replace("GT ", ">")
      sStripped = sStripped.replace("GE ", ">")
      
    if not gCheckNumber(sStripped[1]):
      # Very rare occasion where extra spaces are placed, remove them
      sStripped = sStripped[0] + sStripped[2:]

    if (sStripped[0] == ">" or sStripped[0] == "<") and sStripped.count(' ') != 0:
      # Seems nonsensical to have errors on limits, and there's an occasional reference listed here
      sStripped = sStripped[:sStripped.index(' ')]
      
    if sStripped[0] == ">":
      # Check that the value is a number
      if not gCheckNumber(sStripped.translate(None, '>')):
        print "ERROR: Unknown symbols " + sStripped + " in:\n " + fString
        sys.exit()
      fResults[sID] = sStripped.translate(None, '>')
    elif sStripped[0] == "<":
      if not gCheckNumber(sStripped.translate(None, '<')):
        print "ERROR: Unknown symbols " + sStripped + " in:\n " + fString
        sys.exit()
      fResults[sID] = sStripped.translate(None, '<')
      fResults[sID+2] = sStripped.translate(None, '<')
    elif sStripped[0] == "=": 
      if '  ' in sStripped:
        sStripped = sStripped.replace(" ", " ")
      if sStripped.count(' ') > 1:
        # Want to get rid of everything that appears after the value + error (references)
        sStripped = sStripped[:gFindIter(sStripped, " ", 2)]
      sStripped = sStripped[1:] # Get rid of the =
      sArray = sStripped.strip().split(' ')
      if not gCheckNumber(sArray[0]):
        print "ERROR: Unknown number " + sArray[0] + " in:\n " + fString
        sys.exit()
      else:
        fResults[sID] = sArray[0]
      # Three types of error: a) None, in which case no changes to array needed
      if len(sArray) == 1:
        continue
      # b) single error
      if gCheckNumber(sArray[1]):
        sU, sL = gMatchError(sArray[0], sArray[1], sArray[1])
        fResults[sID+1] = sU
        fResults[sID+2] = sL
      elif "+" in sArray[1]:
        # c) +/- error
        if sArray[1][0] != "+":
          print "ERROR: Unknown format " + sStripped + " in:\n " + fString
          sys.exit()
        else:
          # Split up upper, lower error
          sU, sL = gMatchError(sArray[0], sArray[1][1:sArray[1].index('-')], sArray[1][sArray[1].index('-')+1:])
          fResults[sID+1] = sU
          fResults[sID+2] = sL
      else:
        # All that's left is a reference, can skip as value already written
        continue
    else:
      print "ERROR: Unknown format " + sStripped + " in:\n " + fString
      sys.exit()
               
  return fResults
