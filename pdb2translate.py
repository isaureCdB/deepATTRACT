#!/usr/bin/env python3

import sys

pdb = sys.argv[1]
rec = sys.argv[2]

count = 0
ll = []
for l in open(pdb).readlines():
    if not l.startswith("ATOM"):
        continue
    count += 1
    ll.append("ATOM%4.0i  POSI PRO%5.0i"%(count, count) + l[26:54])
print(len(ll))
for l in ll:
    print(l)

print("TER")

for l in open(rec).readlines():
    print(l[:54])
print("TER")

'''
ATOM      1  H   747 A 166     -12.665  28.291  80.566  1.00  0.00           H
ATOM      1  POSI PRO    1      24.493  36.731 121.249
'''
#/home/isaure/projets/ssRNA/noanchors/4pmw/dock_pocket_lib2018/pdb2translate.py
