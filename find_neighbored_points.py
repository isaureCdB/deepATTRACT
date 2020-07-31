#!/usr/bin/env python3

import sys
import numpy as np
import scipy.spatial

grid = np.array([[float(i) for i in l.split()[6:9]] for l in open(sys.argv[1]).readlines()])
cutoff = float(sys.argv[2])
Nlim = int(sys.argv[3])

print(grid.shape, file=sys.stderr)
Y = scipy.spatial.cKDTree(grid)
nlist = []
#search for neighbors
for nc, coor in enumerate(grid):
    distances, indices = Y.query(coor, k=+99999, distance_upper_bound = cutoff)
    nr_neighbors = (distances<np.inf).sum()
    #print(nr_neighbors, file=sys.stderr)
    if nr_neighbors >= Nlim:
        print(nc+1)
