# Purpose of deepATTRACT

ATTRACT [1] is a protein - protein/RNA/DNA docking software.
It uses a coarse-grained representation and a knowledge-based soft Lennard-Jones potential.
The ligand is moved by gradient-based minimisation from many initial positions
around the receptor. Several conformations of the ligand can be used simultaneously.

ssRN'ATTRACT [2] performs fragment-based docking of ssRNA,
by docking multiple conformations for each trinucleotide (3-nt) in the RNA sequence,
then assembling the docked fragments into a continuous RNA chain.

deepATTRACT [3] was created to tackle the problem of ssRNA docking into
deep cavities of the protein, where 3-nt could not enter from their external
initial position by simple gradient-based minimisation.


# Strategy of deepATTRACT

deepATTRACT uses dense grid points as starting positions for the ligand,
and applies hierarchical filters to retain a reasonnable number of
suitable starting positions for gradient descent minimisation in ATTRACT ff.

At first, deepATTRACT selects points of the grid surrounded by a sufficient
volume to accomodate a 3-nt. At each of those points are placed each of few
 idealised 3-nt conformations with 128 different orientations. The combinations
 [point * orientation * conformation] that are free of atomic clashes are retained,
 and 3-nt conformers from the 3-nt library close to the corresponding ideal
 conformation are placed at the corresponding point * orientation combination.
Those points, associated with all their clash-free orientations and conformers,
are used as starting 3-nt positions for the docking with ATTRACT.


# Tactic of deepATTRACT


------------------------------------------
Get starting positions inside pockets
------------------------------------------
In principle, any grid of points can be used, but we only tested the usage of
POCASA. The pocket finder POCASA [4] identifies possible binding pockets
in/on a protein, and returns a grid of pocket points.

1.  Use POCASA (probe2A, 1A spacing grid), select all pockets
Merge all relevant pockets into pockets.pdb

2.  Select points with at least n neighboring points within x Angstrom
This ensure a minimum volume around the point to accomodate a 3-nt.
Recommended x is in range [7-10], depending if you dock purines or pyrimidines.
Recommended n is in range [500-1000].

./find_neighbored_points.py pockets.pdb $x $n > clusters-$xA-n$n

------------------------------------------
Filter and Dock
------------------------------------------

./deepATTRACT.sh

_ Create starting positions by applying 128 rotations at each point 
_ Cluster conformers at 3A, list their centers in clust3Ar.list
_ Score each conformer of clust3Ar.list at each position
_ Select poses (position + conformer) having a score < 1000
_ Distribute to each starting position the conformers in the same clust3Ar as the well-scored conformer
_ Score, retain the e7 best-scored poses
_ minimize vmax=100
_ keep top e6

------------------------------------------
Assemble
------------------------------------------
[redaction ongoing]
Use 1.3A cutoff for overlapping fragments
assemble 5 to 8 frag > ~ 1-2.e6 chains



[1] Martin Zacharias. Proteins 2003
[2] I. Chauvot de Beauchene, S.J. de Vries, M. Zacharias. PLoS comput 2016 & NAR 2016
[3] C. Singhal, Y. Ponty, I. Chauvot de Beauchene. RECOMB 2018 https://hal.inria.fr/hal-01925083/document
[4] Yu, Zhou, Tanaka, Yao. Bioinformatics 2010
