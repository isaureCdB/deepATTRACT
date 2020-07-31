#!/usr/bin/env python2

from __future__ import print_function
import sys, argparse
from math import *
from _read_struc import read_struc
import random, numpy as np

print ("Usage: ensemblize <DOF file> <boolean matrix><clusterfile>", file = sys.stderr)

############
parser =argparse.ArgumentParser(description=__doc__,
                        formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('datfile', help="ATTRACT rotations-translations dat file")
parser.add_argument('--output', help="output name")
parser.add_argument('--nconf', help="ATTRACT rotations-translations dat file")
parser.add_argument('--max', help="max number of structures per output")
parser.add_argument('--clusters', help="ATTRACT clusterfile. Distribute to all members of the clusters in input")
parser.add_argument("--selection", help='npy boolean matrix of structures selection' )
args = parser.parse_args()
############

header,structures = read_struc(args.datfile)
stnr = 1

if args.max:
    max = int(args.max)
    j = 1
    outp = open(args.output + '-%i'%j + '.dat', 'w')
    print(args.output + '-%i'%j)
else:
    outp = open(args.output + '.dat', 'w')

if args.clusters:
    clustfile = args.clusters
    clusters = [ l.split()[3:] for l in open(clustfile).readlines()]
    for h in header:
        outp.write(h + '\n')
    for ns, s in enumerate(structures):
        l1, l2 = s
        clust = int(l2[1][0]) - 1
        for c in clusters[clust]:
            outp.write("#"+str(stnr) + '\n' )
            outp.write(l2[0] + '\n' )
            outp.write(c + " " + " ".join(l2[1].split()[-6:]) + '\n' )
            stnr += 1
            if args.max:
                if stnr == max+1:
                    outp.close()
                    j+=1
                    outp = open(args.output + '-%i'%j + '.dat', 'w')
                    for h in header:
                        outp.write(h + '\n')
                    print(args.output + '-%i'%j)
                    stnr = 1
    outp.close()
    sys.exit()

nconf = int(args.nconf)

for h in header:
    outp.write(h + '\n')
for ns, (l1, l2) in enumerate(structures):
    for n in range(nconf):
        outp.write("#"+str(stnr) + '\n' )
        outp.write(l2[0] + '\n' )
        outp.write("%i "%(n+1) + " ".join(l2[1].split()[-6:]) + '\n')
        stnr += 1
        if args.max:
            if stnr == max+1:
                outp.close()
                j+=1
                outp = open(args.output + '-%i'%j + '.dat', 'w')
                for h in header:
                    outp.write(h + '\n')
                print(args.output + '-%i'%j)
                stnr = 1
outp.close()


if args.selection and args.clusters:
    matrix = np.load(args.selection)
    assert len(matrix) == ns+1, (len(matrix), ns+1)
    stnr = 1
    for h in header: print(h)
    for ns, s in enumerate(structures):
        l1, l2 = s
        col = matrix[ns]
        for nclust, clust in enumerate(clusters):
            if col[nclust]:
                for c in clust:
                    print("#"+str(stnr))
                    for l in l1:
                        print(l)
                        print(l2[0])
                        print(c + " " + " ".join(l2[1].split()[1:])),
                        stnr += 1
