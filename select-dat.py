#!/usr/bin/env python2

import sys, os, argparse
sys.path.insert(0, os.environ["ATTRACTTOOLS"])
from _read_struc import read_struc
'''
write the top-ranked poses (dat file) from an unsorted dat file
If the energies are not written in the main dat file, supply the scores file"
'''
########################
parser =argparse.ArgumentParser(description=__doc__,
                        formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('dat', help="structures in ATTRACT format")
parser.add_argument('--rank', help="number of structures to select")
parser.add_argument('--score', help="select structures with scores below threshold")
parser.add_argument('--list', help="file list of indices of structures to select")
parser.add_argument('--indices', help="indices of structure to select")
parser.add_argument('--percent', help="percentage of structures to select")
parser.add_argument('--inpscores', help="list of input scores in attract format")
parser.add_argument('--energies', help="write energy in output", action='store_true')

args = parser.parse_args()
########################

def write_structures(header, structures, indices, scores=None, energies=False):
    for l in header:
        print l
    n = 1
    for nr, (l1,l2) in enumerate(structures):
        s = scores[nr]
        if s < cutoff:
            print "#%i"%n
            n += 1
            for l in l1:
                if not l.startswith("## Energy"):
                    print l
            if args.energies:
                print "## Energy: %.3f"%s
            for l in l2:
                print l

header,structures = read_struc(args.dat)
structures = list(structures)

if args.rank:
    rank = int(args.rank)
    if rank >= len(structures):
        print >> sys.stderr, "There are no more than %i structures"%rank
        os.system("cat %s"%args.dat)
        sys.exit()

scores = None
if args.inpscores:
    scores = []
    for l in  open(args.inpscores).xreadlines():
        ll = l.split()
        if ll[0] == "Energy:":
            s = float(ll[1])
            scores.append(s)
    assert(len(scores) == len(structures)), (len(scores), len(structures))


if args.list:
    indices = [int(l.split()[0]) for l in open(args.list).readlines]

if args.indices:
    indices = list(args.indices)

if args.indices or args.list:
    assert(max(indices) <= len(structures)), (max(indices), len(structures))
    write_structures(header, structures, indices, scores, outscores)
    sys.exit()

if not args.inpscores:
    scores = []
    for l1,l2 in structures:
        for ll in l1:
            if ll.startswith("## Energy:"):
                ene = ll[10:].strip()
                if ene.startswith("nan"):
                    s = 100000
                else:
                    s = float(ene)
                scores.append(s)

sorted_scores = sorted(scores)
if args.percent:
    rank = int(round(float(args.percent) * len(sorted_scores)/100))
    print >> sys.stderr, rank
    print >> sys.stderr, "select top %i structures"%rank

if args.score:
    cutoff = float(args.score)
else:
    cutoff = sorted_scores[rank]
print >> sys.stderr, "select structures with score inf to %f"%cutoff

indices = [ nr for nr,s in enumerate(scores) if s < cutoff ]
write_structures(header, structures, indices, scores, args.energies)
