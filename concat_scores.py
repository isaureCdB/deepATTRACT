#!/usr/bin/env python3

import numpy as np, sys, os

inplist = sys.argv[1]
outpnpy = sys.argv[2]
threshold = 100
if len(sys.argv) > 2:
    threshold = float(sys.argv[3])
outpbool = outpnpy.split(".npy")[0] + "-inf%i.npy"%threshold

if not os.path.exists(outpnpy):
    scores = []
    for nl, l in enumerate(open(inplist).readlines()):
        print("processing scoresfile %i"%(nl+1), file=sys.stderr)
        s = []
        for ll in open(l.split()[0]).readlines():
            if ll.split()[0] == "Energy:":
                s.append(float(ll.split()[1]))
            elif len(ll.split()) == 1 :
                continue
            if ll.split()[1] == "Energy:":
                s.append(float(ll.split()[2]))
        scores.append(s)
    scores=np.array(scores).T
    np.save(outpnpy, scores)
else:
    scores = np.load(outpnpy)

c = scores<threshold
print(c.sum())

np.save(outpbool, c)
