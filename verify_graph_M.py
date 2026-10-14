#!/usr/bin/env python3
"""
Companion verification code for

    Inga Johnson and Érika Roldán,
    "Solution Numbers for Eight Blocks to Madness, Part 1".

For the target cube Ba, this script independently checks the paper's structural
and numerical claims by enumerating all C(21,8) = 203,490 collections of eight
cubes drawn from the 21 cubes usable for Ba, and computing each collection's
solution number by two methods that share only their input data:

  A. the graph-theoretic formulas of the paper's two main theorems, applied to
     the component structure of the subgraph G_W of the graph M; and
  B. the prime-product algorithm of arXiv:2407.13208 (Section 7), reimplemented,
     which counts placements directly and uses none of the paper's graph theory.

It reports:
  1. the structure of M -- asserted, not merely printed;
  2. the distribution of solution numbers over the 133,680 solvable collections,
     compared against Table 2 of the paper (label SolnDist);
  3. agreement between methods A and B across all 203,490 collections;
  4. the two cases where the tree component has no edges (k = 0), which the
     paper's lemmas cover and which are easy to overlook;
  5. method C, which does not use the corner-number table: the 30 cubes rebuilt
     from the 720 face colorings and the 24 rotations, compared with the table
     as sets of corner numbers; and, for all 30 targets, the distribution of
     solution numbers and the 1 + 80 split of the 81 collections with solution
     number 16, computed by placing colored cubes in the corners of the 2x2x2
     block;
  6. for Ba, the 81 collections with solution number 16 (1 + 8 + 72, with
     72 = 6 x 12), and the corollary's p = 133680/5852925.

No randomness, no network access, and no dependencies outside the Python
standard library; every count is exact integer arithmetic, and the printed
output is the same on every run. Runtime is about 35 s.

Usage:  python3 verify_graph_M.py [--out PATH]
"""

def check(condition, message):
    """Verification gate. Unlike assert, this survives `python3 -O`."""
    if not condition:
        raise SystemExit("VERIFICATION FAILED: " + message)

import argparse
import csv
import sys
from itertools import combinations, permutations, product
from collections import defaultdict, deque
from fractions import Fraction
from math import comb

_parser = argparse.ArgumentParser(
    description="Verify the claims of 'Solution Numbers for Eight Blocks to Madness, Part 1'.")
_parser.add_argument("--out", metavar="PATH",
                     help="also write the distribution of solution numbers, by both methods "
                          "and as published, to the CSV file PATH")
ARGS = _parser.parse_args()

# ============================================================
# 1. THE 30 MACMAHON CUBES, in Conway's tableau naming.
#    Each cube is given by its eight corner numbers.
#    Taken from the authors' dataset: C36.csv in
#    github.com/IJohnson-math/Colored_Cube_Puzzles, also printed as Table 3 of
#    arXiv:2407.13208. Method C (section 7 below) rebuilds the 30 cubes from
#    their face colorings and compares them with this table.
# ============================================================

ALL_CUBES = {
    'Ab': ['143','345','235','132','126','256','465','164'],
    'Ac': ['153','134','142','125','265','246','364','356'],
    'Ad': ['243','123','152','254','456','165','136','346'],
    'Ae': ['354','145','124','234','263','162','156','365'],
    'Af': ['245','154','135','253','236','163','146','264'],
    'Ba': ['123','253','354','134','146','456','265','162'],
    'Bc': ['143','154','245','234','263','256','165','136'],
    'Bd': ['153','132','124','145','465','264','236','356'],
    'Be': ['152','135','345','254','246','364','163','126'],
    'Bf': ['243','235','125','142','164','156','365','346'],
    'Ca': ['152','124','143','135','365','346','264','256'],
    'Cb': ['243','254','145','134','163','156','265','236'],
    'Cd': ['235','345','154','125','162','146','364','263'],
    'Ce': ['245','253','123','142','164','136','356','465'],
    'Cf': ['153','354','234','132','126','246','456','165'],
    'Da': ['245','125','132','234','364','163','156','465'],
    'Db': ['154','142','123','135','365','263','246','456'],
    'Dc': ['152','145','354','253','236','346','164','126'],
    'De': ['153','235','243','134','146','264','256','165'],
    'Df': ['143','124','254','345','356','265','162','136'],
    'Ea': ['243','142','154','345','356','165','126','236'],
    'Eb': ['245','354','153','125','162','136','346','264'],
    'Ec': ['124','132','235','254','456','365','163','146'],
    'Ed': ['143','234','253','135','156','265','246','164'],
    'Ef': ['152','123','134','145','465','364','263','256'],
    'Fa': ['235','153','145','254','246','164','136','263'],
    'Fb': ['124','152','253','234','364','356','165','146'],
    'Fc': ['123','243','345','135','156','465','264','162'],
    'Fd': ['354','245','142','134','163','126','256','365'],
    'Fe': ['154','143','132','125','265','236','346','456'],
}

BA_CORNERS = set(ALL_CUBES['Ba'])
ba_corners_ordered = ALL_CUBES['Ba']

# ============================================================
# 2. BUILD GRAPH M
# ============================================================

usable_cubes = {}
for name, corners in ALL_CUBES.items():
    if name == 'Ba':
        continue
    shared = set(corners) & BA_CORNERS
    if len(shared) == 2:
        usable_cubes[name] = shared

edges = {name: frozenset(shared) for name, shared in usable_cubes.items()}

edge_to_cubes = defaultdict(list)
for name, edge in edges.items():
    edge_to_cubes[edge].append(name)

# Bipartiteness check
def check_bipartite(verts, edge_list):
    adj = defaultdict(set)
    for v1, v2 in edge_list:
        adj[v1].add(v2); adj[v2].add(v1)
    color = {}
    for s in verts:
        if s in color: continue
        q = deque([s]); color[s] = 0
        while q:
            v = q.popleft()
            for u in sorted(adj[v]):
                if u not in color:
                    color[u] = 1 - color[v]; q.append(u)
                elif color[u] == color[v]:
                    return False, None, None
    return True, {v for v,c in color.items() if c==0}, {v for v,c in color.items() if c==1}

unique_edges_list = [(sorted(e)[0], sorted(e)[1]) for e in edge_to_cubes.keys()]
is_bip, part0, part1 = check_bipartite(sorted(BA_CORNERS), sorted(unique_edges_list))

print("="*70)
print("GRAPH M STRUCTURE")
print("="*70)
print(f"Vertices ({len(BA_CORNERS)}): {sorted(BA_CORNERS)}")
print(f"Edges (cubes): {len(edges)}")
print(f"Distinct vertex pairs: {len(edge_to_cubes)}")
print(f"Bipartite: {is_bip}")
if is_bip:
    print(f"  Partition A: {sorted(part0)}")
    print(f"  Partition B: {sorted(part1)}")

# Vertex degrees
degree = defaultdict(int)
for e in edges.values():
    for v in e: degree[v] += 1
print("Vertex degrees:", {v: degree[v] for v in sorted(degree)})

print("\nAll 20 edges:")
for name in sorted(edges):
    c1, c2 = sorted(edges[name])
    print(f"  {name:3s}: {c1} -- {c2}")

print("\nMulti-edges (pairs sharing same two corners):")
n_parallel_pairs = 0
for edge, cubes in sorted(edge_to_cubes.items(), key=lambda x: sorted(x[0])):
    if len(cubes) > 1:
        n_parallel_pairs += 1
        print(f"  {sorted(edge)}: {cubes}")

# Structural properties of M, asserted rather than merely printed.
# These are exactly the five properties claimed in the paper's
# "Computational verification" section; a failure here is a hard error.
check(len(BA_CORNERS) == 8, f"M must have 8 vertices, got {len(BA_CORNERS)}")
check(len(edges) == 20, f"M must have 20 edges, got {len(edges)}")
check(n_parallel_pairs == 4, f"M must have 4 pairs of parallel edges, got {n_parallel_pairs}")
check(is_bip, "M must be bipartite")
check(all(degree[v] == 5 for v in BA_CORNERS),
      f"every vertex of M must have degree 5, got {({v: degree[v] for v in sorted(degree)})}")

# Every edge joins two DISTINCT corner numbers, so M is loopless by construction.
# The substantive claim underneath that is about the cube data itself: for the target Ba,
# every other cube shares either 0 or exactly 2 corner numbers with it, and Ba shares 8
# with itself. That is what makes "edge" well defined, and it is checked here.
_ucc = {name: len(set(corners) & BA_CORNERS) for name, corners in ALL_CUBES.items()}
check(_ucc['Ba'] == 8, f"the target must share all 8 of its corner numbers with itself, got {_ucc['Ba']}")
check(all(u in (0, 2) for n, u in _ucc.items() if n != 'Ba'),
      f"every non-target cube must have usable corner count 0 or 2, got {_ucc}")
_n_unusable = sum(1 for n, u in _ucc.items() if n != 'Ba' and u == 0)
check(_n_unusable == 9, f"exactly 9 cubes must be unusable for Ba, got {_n_unusable}")
check(len(ALL_CUBES) == 30, f"there must be 30 MacMahon cubes, got {len(ALL_CUBES)}")
check(_n_unusable + len(edges) + 1 == 30, "unusable + usable + target must account for all 30 cubes")

# The Conway names, checked against the structure of Conway's tableau (from the table
# alone). Cube Xy sits in row X and column y of the tableau, and its mirror cube is Yx.
# For every cube Xy: the cubes sharing no corner number with it are exactly the other
# cubes of row X and of column y, and Yx; the corner numbers of Yx are those of Xy read
# the other way round (abc -> acb). Each row and each column holds all 40 corner numbers.
# This catches a name attached to the wrong cube; it cannot tell the letters A to F apart
# beyond this structure.
_LETTERS = "ABCDEF"
check(set(ALL_CUBES) == {X + y.lower() for X, y in permutations(_LETTERS, 2)},
      f"the cubes must be named Xy for distinct letters X, y in A..F, got {sorted(ALL_CUBES)}")
_name_errors = []
for _t, _cs in sorted(ALL_CUBES.items()):
    _X, _y = _t[0], _t[1]
    _mirror = _y.upper() + _X.lower()
    _disjoint = {n for n, c in ALL_CUBES.items() if n != _t and not set(c) & set(_cs)}
    _expected = {n for n in ALL_CUBES if n != _t and (n[0] == _X or n[1] == _y)} | {_mirror}
    if _disjoint != _expected:
        _name_errors.append(f"{_t}: cubes sharing no corner number {sorted(_disjoint)}, "
                            f"expected row, column and mirror {sorted(_expected)}")
    if set(ALL_CUBES[_mirror]) != {c[0] + c[2] + c[1] for c in _cs}:
        _name_errors.append(f"{_t}: {_mirror} is not its mirror cube")
for _L in _LETTERS:
    for _what, _line in (("row", [n for n in ALL_CUBES if n[0] == _L]),
                         ("column", [n for n in ALL_CUBES if n[1] == _L.lower()])):
        _c = [c for n in _line for c in ALL_CUBES[n]]
        if not (len(_line) == 5 and len(set(_c)) == len(_c) == 40):
            _name_errors.append(f"{_what} {_L} does not hold the 40 corner numbers once each")
check(not _name_errors,
      f"the Conway names do not fit the tableau ({len(_name_errors)} problem(s)), "
      f"first: {_name_errors[:1]}")

print("\nStructural assertions on M: PASS "
      "(8 vertices, 20 edges, 4 parallel pairs, bipartite, 5-regular).")
print("Cube-data assertions: PASS "
      "(30 cubes; usable corner count 8 for Ba, 0 or 2 for the rest; 9 unusable, 20 usable).")
print("Conway-name assertions: PASS (for each cube Xy, the cubes sharing no corner number")
print("  with it are the rest of row X and column y and its mirror cube Yx, whose corner")
print("  numbers are those of Xy read the other way round; each row and each column of")
print("  the tableau holds all 40 corner numbers).")

# ============================================================
# 3. GRAPH-BASED SOLUTION NUMBER (paper's formula)
# ============================================================

def get_components(vertex_set, edge_frozensets):
    adj = defaultdict(set)
    for e in edge_frozensets:
        v1, v2 = list(e)
        adj[v1].add(v2); adj[v2].add(v1)
    visited = set(); components = []
    for v in sorted(vertex_set):
        if v in visited: continue
        comp = set(); q = deque([v])
        while q:
            u = q.popleft()
            if u in visited: continue
            visited.add(u); comp.add(u)
            for w in sorted(adj[u]):
                if w not in visited and w in vertex_set: q.append(w)
        components.append(comp)
    components.sort(key=min)
    return components

def analyze_subgraph(cube_names, ba_included):
    """Return (solution_number, n_components, comp_details, n_trees, k_tree)."""
    n_edges = len(cube_names)
    edge_set = [edges[name] for name in cube_names]
    components = get_components(BA_CORNERS, edge_set)
    n_comp = len(components)

    comp_details = []
    for comp in components:
        nv = len(comp)
        ne = sum(1 for e in edge_set if e.issubset(comp))
        is_tree = (ne == nv - 1)
        comp_details.append((nv, ne, is_tree))

    n_trees = sum(1 for _,_,t in comp_details if t)
    k_tree = None
    for nv, ne, t in comp_details:
        if t:
            k_tree = ne
            break

    # Compute solution number per paper's formulas
    if not ba_included:
        if n_edges != 8: return (0, n_comp, comp_details, n_trees, k_tree)
        if n_trees > 0: return (0, n_comp, comp_details, n_trees, k_tree)
        return (2**n_comp, n_comp, comp_details, n_trees, k_tree)
    else:
        if n_edges != 7: return (0, n_comp, comp_details, n_trees, k_tree)
        if n_trees > 1: return (0, n_comp, comp_details, n_trees, k_tree)
        if n_trees == 0: return (0, n_comp, comp_details, n_trees, k_tree)
        if n_comp == 1: sol = 8
        elif n_comp == 2: sol = 2*(k_tree+1)
        elif n_comp == 3: sol = 4*(k_tree+1)
        elif n_comp == 4: sol = 8 * (k_tree + 1)  # Lemma wTfourcomponents: k in {0,1}.
        else: sol = 0
        return (sol, n_comp, comp_details, n_trees, k_tree)

# ============================================================
# 4. BRUTE-FORCE SOLUTION NUMBER (prime-product algorithm, arXiv:2407.13208 Section 7)
# ============================================================

PRIMES = [2, 3, 5, 7, 11, 13, 17, 19]
PRIME_PRODUCT = 2*3*5*7*11*13*17*19

def compute_brute(collection):
    """Brute-force solution count for a collection of 8 cubes targeting Ba."""
    cube_to_prime = {name: PRIMES[i] for i, name in enumerate(collection)}
    corner_primes = []
    for corner in ba_corners_ordered:
        cp = [cube_to_prime[name] for name in collection if corner in ALL_CUBES[name]]
        if not cp: return 0
        corner_primes.append(cp)
    count = 0
    for assignment in product(*corner_primes):
        p = 1
        for q in assignment: p *= q
        if p % PRIME_PRODUCT == 0: count += 1
    return count

# ============================================================
# 5. ENUMERATE ALL C(21,8) COLLECTIONS
# ============================================================

usable_names = sorted(usable_cubes.keys())
all_21 = usable_names + ['Ba']

print("\n" + "="*70)
print("ENUMERATING ALL COLLECTIONS")
print("="*70)
print(f"C(30,8) = {comb(30,8)}")
print(f"C(21,8) = {comb(21,8)} (only usable cubes for Ba)")

dist_graph = defaultdict(int)
dist_brute = defaultdict(int)
mismatches = []
cases_3comp_k0 = []
cases_4comp_0223 = []
cases_4comp_1222 = []
all_4comp_ba = []
sol16 = []   # (collection, contains Ba, number of components, k)

total = 0
for combo in combinations(all_21, 8):
    total += 1
    ba_in = 'Ba' in set(combo)
    edge_cubes = [c for c in combo if c != 'Ba']

    sol_g, ncomp, cdet, ntrees, ktree = analyze_subgraph(edge_cubes, ba_in)
    sol_b = compute_brute(list(combo))

    dist_graph[sol_g] += 1
    dist_brute[sol_b] += 1

    if sol_g != sol_b:
        mismatches.append((combo, sol_g, sol_b, ncomp, cdet, ntrees, ktree))

    if sol_b == 16:
        sol16.append((combo, ba_in, ncomp, ktree))

    if ba_in and sol_b > 0:
        edge_dist = sorted([ne for _,ne,_ in cdet])
        if ncomp == 3 and ntrees == 1 and ktree == 0:
            cases_3comp_k0.append((combo, sol_b, cdet))
        if ncomp == 4:
            all_4comp_ba.append((combo, sol_b, cdet, edge_dist, ntrees))
            if edge_dist == [0,2,2,3] and ntrees == 1:
                cases_4comp_0223.append((combo, sol_b, cdet))
            if edge_dist == [1,2,2,2] and ntrees == 1:
                cases_4comp_1222.append((combo, sol_b, cdet))

    if total % 50000 == 0:
        print(f"  Processed {total}...")

check(total == comb(21, 8) == 203490, f"expected C(21,8)=203,490 collections, enumerated {total}")

nonzero_graph = sum(v for k,v in dist_graph.items() if k > 0)
nonzero_brute = sum(v for k,v in dist_brute.items() if k > 0)

# ============================================================
# 6. RESULTS
# ============================================================

print("\n" + "="*70)
print("RESULT 1: BRUTE-FORCE DISTRIBUTION (prime-product method)")
print("="*70)
print(f"Total non-zero: {nonzero_brute}")
for sn in sorted(dist_brute):
    if sn > 0:
        print(f"  Solution number {sn:3d}: {dist_brute[sn]:6d}")

print("\n" + "="*70)
print("RESULT 2: GRAPH FORMULA DISTRIBUTION")
print("="*70)
print(f"Total non-zero: {nonzero_graph}")
for sn in sorted(dist_graph):
    if sn > 0:
        print(f"  Solution number {sn:3d}: {dist_graph[sn]:6d}")

# The distribution published in the paper (table label SolnDist), transcribed for comparison.
paper = {2: 93000, 4: 15987, 6: 2664, 8: 19860, 10: 792, 12: 1296, 16: 81}

print("\n" + "="*70)
print("RESULT 3: COMPARISON WITH TABLE 2 (SolnDist) OF THE PAPER")
print("="*70)
print(f"{'Sol#':>5} {'Paper':>8} {'BruteF':>8} {'Graph':>8} {'Paper=BF':>9} {'Paper=Gr':>9}")
print(f"{'-'*5} {'-'*8} {'-'*8} {'-'*8} {'-'*9} {'-'*9}")
all_sns = sorted(set(list(paper.keys()) + [k for k in dist_brute if k>0] + [k for k in dist_graph if k>0]))
for sn in all_sns:
    pv = paper.get(sn, 0)
    bv = dist_brute.get(sn, 0)
    gv = dist_graph.get(sn, 0)
    m1 = "YES" if pv == bv else "**NO**"
    m2 = "YES" if pv == gv else "**NO**"
    print(f"{sn:5d} {pv:8d} {bv:8d} {gv:8d} {m1:>9} {m2:>9}")
print(f"{'Total':>5} {sum(paper.values()):8d} {nonzero_brute:8d} {nonzero_graph:8d}")

print("\n" + "="*70)
print("RESULT 4: GRAPH vs BRUTE FORCE MISMATCHES")
print("="*70)
print(f"Total mismatches: {len(mismatches)}")
if mismatches:
    print("\nThe two methods disagree on the collections below. Each such collection is")
    print("inconsistent with at least one of the paper's formulas.\n")
    for combo, sg, sb, nc, cd, nt, kt in mismatches[:5]:
        ed = sorted([ne for _, ne, _ in cd])
        print(f"  {combo}")
        print(f"    graph formula={sg}, prime-product={sb}, components={nc}, trees={nt}, k={kt}")
        print(f"    edge distribution: {ed}, component details: {cd}")
    if len(mismatches) > 5:
        print(f"  ... and {len(mismatches) - 5} more.")

# The main statement of the paper's verification section. Checked after the
# diagnostic block above, so a failing run lists the disagreements before it exits.
check(len(mismatches) == 0,
      f"the graph formulas and the prime-product brute force disagree on {len(mismatches)} "
      f"collection(s); the paper states that they agree on all {total}")

print("\n" + "="*70)
print("RESULT 5: THE ZERO-EDGE TREE CASES (k = 0)")
print("="*70)
print("A tree component with no edges is a single vertex, occupied by the target")
print("Ba itself. These cases contribute the factor k+1 = 1 and are the easiest to")
print("overlook, so they are checked here explicitly against the paper's lemmas.")

print("\n--- Three components, tree with k=0 ---")
print("Paper's Lemma wTarget3components: solution number = 4(k+1), so 4 when k=0.")
print(f"Collections found: {len(cases_3comp_k0)}")
check(len(cases_3comp_k0) == 1728,
      f"expected 1,728 three-component k=0 collections, found {len(cases_3comp_k0)}")
sols_3 = set(s for _, s, _ in cases_3comp_k0)
print(f"Prime-product brute force gives: {sols_3}")
ok3 = (sols_3 == {4})
print(f"Agrees with 4(0+1) = 4 on every collection? {ok3}")
check(ok3, f"Lemma wTarget3components does not hold at k=0: brute force gives {sols_3}, expected 4")
print(f"Example: {cases_3comp_k0[0][0]}")
print(f"  Components (vertices, edges, is_tree): {cases_3comp_k0[0][2]}")

print("\n--- Four components, tree with k=1, distribution (1,2,2,2) ---")
print("Paper's Lemma wTfourcomponents: solution number = 8(k+1), so 16 when k=1.")
print(f"Collections found: {len(cases_4comp_1222)}")
check(len(cases_4comp_1222) == 8,
      f"expected 8 collections of distribution (1,2,2,2), found {len(cases_4comp_1222)}")
sols_1222 = set(s for _, s, _ in cases_4comp_1222)
print(f"Prime-product brute force gives: {sols_1222}")
ok1222 = (sols_1222 == {16})
print(f"Agrees with 8(1+1) = 16 on every collection? {ok1222}")
check(ok1222, f"Lemma wTfourcomponents does not hold at k=1: brute force gives {sols_1222}, expected 16")
print(f"Example: {cases_4comp_1222[0][0]}")
print(f"  Components (vertices, edges, is_tree): {cases_4comp_1222[0][2]}")

print("\n--- Four components, tree with k=0, distribution (0,2,2,3) ---")
print("Paper's Lemma wTfourcomponents: solution number = 8(k+1), so 8 when k=0.")
print("Structure: Ba sits on the isolated vertex (1 way); two 2-cycles and one")
print("3-edge unicyclic component each contribute a factor of 2, giving 1*2*2*2 = 8.")
print(f"Collections found: {len(cases_4comp_0223)}")
check(len(cases_4comp_0223) == 24,
      f"expected 24 collections of distribution (0,2,2,3), found {len(cases_4comp_0223)}")
sols_0223 = set(s for _, s, _ in cases_4comp_0223)
print(f"Prime-product brute force gives: {sols_0223}")
ok0223 = (sols_0223 == {8})
print(f"Agrees with 8(0+1) = 8 on every collection? {ok0223}")
check(ok0223, f"Lemma wTfourcomponents does not hold at k=0: brute force gives {sols_0223}, expected 8")
print(f"Example: {cases_4comp_0223[0][0]}")
print(f"  Components (vertices, edges, is_tree): {cases_4comp_0223[0][2]}")

print(f"\n--- ALL 4-component Ba-included collections ---")
print(f"Total: {len(all_4comp_ba)}")
edge_dist_summary = defaultdict(lambda: defaultdict(int))
for _, sol, _, ed, nt in all_4comp_ba:
    edge_dist_summary[tuple(ed)][(sol, nt)] += 1
for ed in sorted(edge_dist_summary):
    print(f"  Edge distribution {ed}:")
    for (sol, nt), count in sorted(edge_dist_summary[ed].items()):
        print(f"    sol={sol}, trees={nt}: {count} collections")

# Consistency check: Table 2 of the paper equals the brute-force distribution.
print()
print("CONSISTENCY CHECK:")
match_direct = all(paper.get(sn,0) == dist_brute.get(sn,0) for sn in all_sns)
print(f"  Table 2 of the paper == brute-force distribution? {match_direct}")
check(match_direct, "Table 2 of the paper (SolnDist) does not match the brute-force distribution")

# ============================================================
# 7. METHOD C AND FURTHER COUNTS
#    C1, C2 (method C): the 30 cubes are rebuilt from their face colorings, and
#    every target is solved by placing colored cubes in the corners of the
#    2x2x2 block. Nothing in C1 and C2 reads the corner-number table above,
#    except to compare with it at the end of C1.
#    C3, C4: the counts of the 81 collections with solution number 16 and the
#    corollary.
# ============================================================

print("\n" + "="*70)
print("METHOD C (C1, C2: from the face colorings) AND FURTHER COUNTS (C3, C4)")
print("="*70)

# --- C1. The 30 MacMahon cubes, rebuilt -------------------------------------
# A coloring lists the colors 1..6 of the faces in the directions of FACES.
FACES = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
FACE_INDEX = {f: i for i, f in enumerate(FACES)}
OCTANTS = list(product((1, -1), repeat=3))   # the 8 corners of a cube, and of the block

def _det3(m):
    return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
            - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
            + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))

# The rotations of the cube: the signed permutation matrices of determinant +1,
# each written as the permutation it induces on the six face directions.
FACE_PERMS = []
for _p in permutations(range(3)):
    for _s in product((1, -1), repeat=3):
        _m = [[0] * 3 for _ in range(3)]
        for _i in range(3):
            _m[_i][_p[_i]] = _s[_i]
        if _det3(_m) == 1:
            FACE_PERMS.append(tuple(
                FACE_INDEX[tuple(sum(_m[i][j] * f[j] for j in range(3)) for i in range(3))]
                for f in FACES))
check(len(set(FACE_PERMS)) == 24, f"expected 24 rotations of the cube, got {len(set(FACE_PERMS))}")

def rotate(coloring, perm):
    out = [0] * 6
    for i in range(6):
        out[perm[i]] = coloring[i]
    return tuple(out)

def corner_number(coloring, s):
    """The colors around corner s, read clockwise as seen from outside the cube,
    starting with the smallest. (Reading counterclockwise instead turns each cube
    into its mirror cube, which is also one of the 30, so the comparison with the
    table in C1 does not depend on the reading direction.)"""
    a = coloring[FACE_INDEX[(s[0], 0, 0)]]
    b = coloring[FACE_INDEX[(0, s[1], 0)]]
    c = coloring[FACE_INDEX[(0, 0, s[2])]]
    if s[0] * s[1] * s[2] == 1:   # here x, y, z run counterclockwise
        b, c = c, b
    t = [a, b, c]
    i = t.index(min(t))
    return "".join(str(x) for x in t[i:] + t[:i])

# All 6! = 720 colorings with six distinct colors, grouped into rotation classes.
_classes = {}
for _col in permutations(range(1, 7)):
    _orbit = frozenset(rotate(_col, p) for p in FACE_PERMS)
    _classes[min(_orbit)] = _orbit
check(len(_classes) == 30, f"expected 30 rotation classes of the 720 colorings, got {len(_classes)}")
check(all(len(o) == 24 for o in _classes.values()), "every rotation class must have 24 colorings")
REBUILT = [sorted(_classes[r]) for r in sorted(_classes)]   # 30 cubes, each as its 24 colorings

def corner_set(cube):
    sets = {frozenset(corner_number(col, s) for s in OCTANTS) for col in cube}
    check(len(sets) == 1, "corner numbers must not depend on how the cube is turned")
    return next(iter(sets))

rebuilt_sets = [corner_set(cube) for cube in REBUILT]
table_sets = {frozenset(c) for c in ALL_CUBES.values()}
check(len(set(rebuilt_sets)) == 30 and set(rebuilt_sets) == table_sets,
      "the 30 cubes rebuilt from the colorings differ from the 30 cubes of the table")
print("C1. 720 colorings / 24 rotations = 30 cubes; their corner-number sets equal the")
print("    30 cubes of the table: PASS. (This checks the cubes as sets of corner numbers,")
print("    not the direction in which corner numbers are read: the other direction gives")
print("    the mirror cubes, also among the 30. The Conway names are checked only against")
print("    the row, column and mirror structure of the tableau, above.)")

# --- C2. Every target, solved by placing colored cubes -----------------------
# In the 2x2x2 block, the small cube at corner s shows its faces in the directions
# s[0]x, s[1]y, s[2]z on the outside; they must carry the target's colors there.
def fits(target, cube, s):
    """Number of orientations in which `cube` can sit at corner s of the block."""
    faces = [FACE_INDEX[(s[0], 0, 0)], FACE_INDEX[(0, s[1], 0)], FACE_INDEX[(0, 0, s[2])]]
    return sum(1 for col in cube if all(col[f] == target[f] for f in faces))

def solution_distribution(target_index):
    """Distribution of solution numbers over all collections of eight cubes for one
    target, split by whether the collection contains the target."""
    target = REBUILT[target_index][0]
    usable, masks = [], []
    for j, cube in enumerate(REBUILT):
        f = [fits(target, cube, s) for s in OCTANTS]
        check(all(x in (0, 1) for x in f), "a cube fits a corner of the block in at most one way")
        tcorners = [corner_number(target, s) for s in OCTANTS]
        check(all((f[i] == 1) == (tcorners[i] in rebuilt_sets[j]) for i in range(8)),
              "a cube fits a corner exactly when it carries the target's corner number there")
        if any(f):
            usable.append(j)
            masks.append(sum(1 << i for i in range(8) if f[i]))
    dist = defaultdict(int)
    with_target = defaultdict(int)
    t_pos = usable.index(target_index)

    # Choose the cubes one at a time; ways[used] counts the placements of the cubes
    # chosen so far into the set `used` of corners. A branch whose cubes cannot all
    # be placed is abandoned, since every collection extending it has no solution.
    def extend(start, depth, ways, has_target):
        if depth == 8:
            sol = ways.get(255, 0)
            if sol:
                dist[sol] += 1
                if has_target:
                    with_target[sol] += 1
            return
        for j in range(start, len(usable) - (8 - depth) + 1):
            new = {}
            for used, w in ways.items():
                free = masks[j] & ~used
                while free:
                    bit = free & -free
                    free ^= bit
                    new[used | bit] = new.get(used | bit, 0) + w
            if new:
                extend(j + 1, depth + 1, new, has_target or j == t_pos)

    extend(0, 0, {0: 1}, False)
    return len(usable), dict(dist), dict(with_target)

_bad_targets = []
for _t in range(30):
    _nu, _d, _w = solution_distribution(_t)
    if not (_nu == 21 and _d == paper and _w.get(16, 0) == 80 and _d[16] - _w.get(16, 0) == 1):
        _bad_targets.append((_t, _nu, _d, _w))
check(not _bad_targets,
      f"{len(_bad_targets)} target(s) do not reproduce Table 2 and the 1/80 split, "
      f"first: {_bad_targets[:1]}")
print("C2. For each of the 30 targets: 21 usable cubes, and the distribution of solution")
print("    numbers equals Table 2; of its 81 collections with solution number 16, 1 avoids")
print("    the target and 80 contain it: PASS (all 30 targets).")

# --- C3. The 81 collections with solution number 16, for the target Ba --------
# (From the enumeration above and the graph M.)
diagonal_pairs = sorted(sorted(c) for c in edge_to_cubes.values() if len(c) == 2)
diagonals = sorted(c for pair in diagonal_pairs for c in pair)
sol16_without = [c for c, has_ba, _, _ in sol16 if not has_ba]
sol16_n4 = [c for c, has_ba, n, k in sol16 if has_ba and n == 4 and k == 1]
sol16_n3 = [c for c, has_ba, n, k in sol16 if has_ba and n == 3 and k == 3]
check(len(sol16) == 81, f"expected 81 collections with solution number 16, found {len(sol16)}")
check(len(sol16_without) == 1 and sorted(sol16_without[0]) == diagonals,
      f"expected exactly one collection without Ba, the four diagonal pairs; found {sol16_without}")
check(len(sol16_n4) == 8 and len(sol16_n3) == 72 and len(sol16_n4) + len(sol16_n3) == 80,
      f"expected 80 = 8 + 72 collections with Ba, found {len(sol16_n4)} + {len(sol16_n3)}")

# The paper's count of the 72: two of the four diagonal pairs (6 ways), then a path
# of three cubes spanning the other four corner numbers (12 ways for each choice).
_built72 = set()
_paths_per_choice = []
for _two in combinations(diagonal_pairs, 2):
    _rest = BA_CORNERS - set().union(*(edges[p[0]] for p in _two))
    _inside = sorted(c for c in edges if edges[c] <= _rest)
    _n_paths = 0
    for _three in combinations(_inside, 3):
        _es = [edges[c] for c in _three]
        _deg = [sum(v in e for e in _es) for v in _rest]
        if len(set(_es)) == 3 and min(_deg) >= 1 and max(_deg) <= 2:
            _n_paths += 1
            _built72.add(tuple(sorted(list(_two[0]) + list(_two[1]) + list(_three) + ['Ba'])))
    _paths_per_choice.append(_n_paths)
check(len(_paths_per_choice) == 6 and _paths_per_choice == [12] * 6,
      f"expected 12 spanning paths for each of the 6 choices, got {_paths_per_choice}")
check(_built72 == {tuple(sorted(c)) for c in sol16_n3},
      "the 72 collections built as two diagonal pairs + a spanning path + Ba differ from "
      "the 72 found by the enumeration")
print("C3. Target Ba: 81 collections with solution number 16 = 1 without Ba (the four")
print(f"    diagonal pairs {', '.join(diagonals)}) + 8 with four components + 72 with")
print("    three components; 72 = 6 x 12 (two diagonal pairs, then a spanning path of")
print("    three cubes), and these are exactly the 72 found: PASS.")

# --- C4. The corollary ----------------------------------------------------------
p_build = Fraction(sum(paper.values()), comb(30, 8))
check(sum(paper.values()) == 133680 and comb(30, 8) == 5852925,
      "the corollary uses 133,680 solvable collections out of C(30,8) = 5,852,925")
check(round(p_build, 4) == Fraction(228, 10000), f"p = {p_build} does not round to 0.0228")
print(f"C4. p = 133680/5852925 = {p_build} = {float(p_build):.6f}, about 0.0228: PASS.")

print("\n" + "="*70)
print("FINAL SUMMARY")
print("="*70)
_table_ok = all(paper[sn] == dist_brute.get(sn, 0) for sn in paper) and \
            sum(paper.values()) == nonzero_brute
print(f"""
1. GRAPH M: {len(BA_CORNERS)} vertices, {len(edges)} edges (cubes),
   {n_parallel_pairs} pairs of parallel edges, bipartite={is_bip},
   every vertex of degree {min(degree.values())}. Asserted above.

2. Table 2 of the paper (label SolnDist): reproduced on all {len(paper)} solution numbers?
   {_table_ok}. Total solvable collections = {nonzero_brute:,}.

3. Lemma wTfourcomponents, solution number 8(k+1):
   - k=0, distribution (0,2,2,3): {len(cases_4comp_0223):,} collections, all sol=8.
   - k=1, distribution (1,2,2,2): {len(cases_4comp_1222):,} collections, all sol=16.

4. Lemma wTarget3components, solution number 4(k+1):
   - k=0, distribution (0,a,7-a), a in {{2,3}}: {len(cases_3comp_k0):,} collections, all sol=4.

5. CROSS-VALIDATION: graph-theoretic formulas vs the prime-product algorithm of
   arXiv:2407.13208 (Section 7), over all {total:,} usable-for-Ba collections.
   Mismatches: {len(mismatches)}.

6. METHOD C AND FURTHER COUNTS, all asserted above:
   - the 30 cubes rebuilt from the 720 colorings equal the table's 30 cubes
     as sets of corner numbers (the Conway names are checked only against the
     tableau's rows, columns and mirror cubes, and the reading direction of
     corner numbers is not checked);
   - all 30 targets give the distribution of Table 2, and for each, 1 of its
     81 collections with solution number 16 avoids the target and 80 contain it;
   - for Ba: 81 = 1 + 8 + {len(sol16_n3)}, with {len(sol16_n3)} = 6 x 12;
   - p = 133680/5852925 = {float(p_build):.4f}.
""")

# ============================================================
# 8. OPTIONAL CSV: the data behind the paper's distribution table, so a run can
#    be compared with solution_number_distribution.csv. Written only with --out;
#    the message goes to stderr, so the printed output does not depend on it.
# ============================================================
if ARGS.out:
    try:
        with open(ARGS.out, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["solution_number", "num_collections_brute_force",
                        "num_collections_graph_formula", "num_collections_in_paper"])
            for sn in sorted(k for k in dist_brute if k > 0):
                w.writerow([sn, dist_brute[sn], dist_graph.get(sn, 0), paper.get(sn, "")])
            w.writerow(["total", nonzero_brute, nonzero_graph, sum(paper.values())])
    except OSError as e:
        sys.exit(f"Verification passed, but {ARGS.out} could not be written: {e}")
    print(f"Wrote {ARGS.out} ({len(paper)} solution numbers, "
          f"{nonzero_brute:,} solvable collections).", file=sys.stderr)
