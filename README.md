# PENS (Parsing Evaluated Nuclear Sheets)
The oddly named 'PENS' is a python program that parses all 'Adopted Levels/Gammas' files from ENSDF, ultimately for the creation of a root file from which systematics can be plotted.  The user only needs to download the ROOT file, in principle, as it was/is recently created.  

Each nuclide is an instance of a class within the ROOT file, where the transitions and levels are two float vectors.  The exact structure can be seen in the createRoot.C file.  In short, the nuclear data is:

    int nMass // Nuclear Mass
    int nProton // Proton Number
    int nNeutron // Neutron Number

---  
## Level Information

    vector < vector < double> > nLevels

Where the index of the levels corresponds to:

    [0] State energy [keV]
    [1], [2] Confirmed spin and parity
  
The spin is -1 if unknown/tentative.  The parity is +1 for positive, -1 for negative, 0 for unknown/tentative.  For example, the second 2+ state will correspond to [1] = 2, [2] = +1

    [3], [4] Tentative spin and parity

Follows the same rules as before, but tentative spins are included in the total count.  As tentative spins are essentially comments in an ENSDF files, some information is lost.  So for spins that are listed with a delimiter "," the first value is taken, but for spins that give ranges or other comments e.g. "TO", "&", "GE", ":", ">" I have decided to list them as unknown i.e. -1, 0.

    [5], [6], [7] Half-life in ps, with the upper and lower errors

---
## Transition Information

    vector < vector < double> > nTransitions

Where the index of the transitions corresponds to:


    [0] The index of the level vector from which the transition originates
    [1] The index, where the transition decays to
    [2], [3], [4] Branching ratio (Intensity gamma) and the associated errors
    [5], [6], [7], [8] B(E1) [W.u.] and errors.  Fourth element is a flag for confirmed (1 if confirmed)
    [9], [10], [11], [12] B(E2) [W.u.], as above
    [13], , , [16] B(E3) [W.u.], as above
    [17], , , [20] B(E4) [W.u.], as above
    [5], [6], [7], [8] B(E1) [W.u.] and errors.  Fourth element is a flag for confirmed (1 if confirmed)
    [9], [10], [11], [12] B(E2) [W.u.], as above
    [13], , , [16] B(E3) [W.u.], as above
    [17], , , [20] B(E4) [W.u.], as above
    [21] -- [36] B(ML) [W.u.], as above
    [37], [38], [39] Mixing ratio with upper, lower errors
    [40], [41]

A number of these properties are not obtained through ENSDF, but via a Google Spreadsheet used as an injector/override if necessary.  This includes mostly the deformation and E0 related properties.

---
## A note on errors
If a quantity has 3 elements, such as the B(E2) values, the first is the value and the following two are the upper and lower respectively.  

If the error is a "less than", then the upper error = 0 and lower error = value.  
If the error is a "greater than", then the upper error = value and lower error = 0.  

This is made this way for the purpose of if conditions later on.
