# PENS
The oddly named 'PENS' is a python program that parses all 'Adopted Levels/Gammas' files from ENSDF, for the creation of a root file containing all the information.  The user only needs to download the ROOT file, in principle, as it was/is recently created.

Each nuclide is a class within the ROOT file, where the transitions and levels are two float vectors.  The additional nuclear data is as follows:

    int nMass // Nuclear Mass
    int nProton // Proton Number
    int nNeutron // Neutron Number
    int nQuadrupole // Quadrupole Moment (Q)
    vector <double> nDeformation // Deformation (beta) where // [0] is value, [1] and [2] are upper and lower errors

---  
## Level Information

    vector < vector < double> > nLevels

Where the index of the levels corresponds to:

    [0] State energy [keV]
    [1], [2], [3] Confirmed spin, parity and Nth occurence
  
The spin is -1 if unknown/tentative.  The parity is +1 for positive, -1 for negative, 0 for unknown/tentative.  The count begins at 1, and is -1 if the state spin is unknown/tentative.  For example, the second 2+ state will correspond to [1] = 2, [2] = +1, [3] = 2

    [4], [5], [6] Tentative spin, parity and Nth occurence

Follows the same rules as before, but tentative spins are included in the total count.  As tentative spins are essentially comments in an ENSDF files, some information is lost e.g. if it's listed as (2+ to 4+) then it's tentatively assigned the first spin/parity listed

    [7], [8], [9] Half-life in ps, with the upper and lower errors

---
## Transition Information

    vector < vector < double> > nTransitions

Where the index of the transitions corresponds to:

3 1 0.8 2.0 14.9 2.4 4.2 0 0 0 +3.19 0.11 0.11 0.32 0.08 213 46 39 0.5 0.13 0.0 0.0 0.0

    [0] The index of the level vector from which the transition originates
    [1] The index, where the transition decays to
    [2], [3] Branching ratio (gamma) and the associated error NOTICED ERROR, UNRELIABLE TEMPORARILY
    [4], [5], [6] B(E2) [W.u.] if available with value, upper, lower errors
    [7], [8], [9] B(M1) [W.u.] if available
    [10], [11], [12] Mixing ratio with upper, lower errors
    [13], [14] q^2 (E0)/(E2) ratio with error
    [15], [16], [17] rho^2 (E0) with upper, lower error
    [18], [19] X (E0) UNRELIABLE, MUST IMPLEMENT CALCULATION
    [20], [21], [22] The total internal conversion coefficient

A number of these properties are not obtained through ENSDF, but via a Google Spreadsheet used as an injector/override if necessary.  This includes mostly the deformation and E0 related properties.
