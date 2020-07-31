#!/usr/bin/env python3
import sys, argparse
import numpy as np

# Select and write specific lines from the input file into an output file
#######################
parser = argparse.ArgumentParser(description=__doc__,
                        formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('data')
parser.add_argument('selection')
parser.add_argument("--dataorder",help="order along data file", action="store_true")
parser.add_argument("--reverse",help="take absent lines", action="store_true")
parser.add_argument("--indices",help="print line indices instead of lines", action="store_true")
parser.add_argument("--lines",help="selection is lines instead of indices", action="store_true")
parser.add_argument("--npy",help="use numpy", action="store_true")
args = parser.parse_args()
#######################

if args.npy:
    data = np.loadtxt(args.data)
    sel = np.loadtxt(args.selection, dtype=int)
else:
    data = [l.strip() for l in open(args.data).readlines()]
    selection = [l.strip() for l in open(args.selection).readlines()]
    if not args.lines:
        selection = [int(l.split()[0]) for l in selection]

def pprint(i, l):
    if args.indices:
        print(i+1)
    else:
        print(l),

if args.lines :
    if args.reverse:
        sset = set(selection)
        print(len(sset), file=sys.stderr)
        for nd, d in enumerate(data):
            if d not in sset:
                pprint(nd, d)
    else:
        if args.dataorder:
            sset = set(selection)
            for nd, d in enumerate(data):
                if d in sset:
                    pprint(nd, d)
        else:
            for s in selection:
                for nd, d in enumerate(data):
                    if d == s:
                        pprint(nd, d)
elif not args.npy:
    if args.reverse:
        sset = set(selection)
        print(len(sset))
        for nd, d in enumerate(data):
            if nd+1 not in sset:
                pprint(nd, d)
    else:
        if args.dataorder:
            sset = set(selection)
            for nd, d in enumerate(data):
                if nd+1 in sset:
                    pprint(nd, d)
        else:
            for s in selection:
                for nd, d in enumerate(data):
                    if nd+1 == s:
                        pprint(nd, d)
elif args.npy:
    if args.dataorder:
        sel = np.sort(sel, axis=0)
    if args.reverse:
        mask = np.ones(data.shape,dtype=bool) #np.ones_like(a,dtype=bool)
        mask[sel] = False
        new_data = data[mask]
    else:
        new_data = data[sel]
    for nd in range(new_data.shape[0]):
        print(nd, new_data[nd])
