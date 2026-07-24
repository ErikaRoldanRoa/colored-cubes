#!/usr/bin/env python3
"""
Companion verification code for

    I. Johnson and E. Roldan Roa,
    "Solution Numbers for Eight Blocks to Madness Puzzle".

For the target cube Ba, this script independently checks the paper's structural
and numerical claims by enumerating all C(21,8) = 203,490 collections of eight
cubes drawn from the 21 cubes usable for Ba, and computing each collection's
solution number by two methods that share only their input data:

  A. the graph-theoretic formulas of the paper's two main theorems, applied to
     the component structure of the subgraph G_W of the graph M; and
  B. the prime-product brute force of the authors' earlier preprint
     (arXiv:2407.13208), which counts placements directly and uses none of the
     paper's graph theory.

It reports:
  1. the structure of M -- asserted, not merely printed;
  2. the distribution of solution numbers over the 133,680 solvable collections,
     compared against the paper's distribution table (label SolnDist, which
     typesets as Table 2; Table 1 is ContainsT, the components table inside
     Theorem 2 -- the labels are the addresses, the numbers are not);
  3. agreement between methods A and B across all 203,490 collections;
  4. the two cases where the tree component has no edges (k = 0), which the
     paper's lemmas cover and which are easy to overlook.

The script is deterministic: no randomness, no network, no floating point, and
no dependencies outside the Python standard library. Runtime is about 30 s.
"""

def check(condition, message):
    """Verification gate. Unlike assert, this survives `python3 -O`."""
    if not condition:
        raise SystemExit("VERIFICATION FAILED: " + message)

from itertools import combinations, product
from collections import defaultdict, deque
from math import comb

# ============================================================
# 1. THE 30 MACMAHON CUBES, in Conway's tableau naming.
#    Each cube is given by its eight corner numbers.
#    Cross-checked against the cube data published alongside arXiv:2407.13208
#    at github.com/IJohnson-math/Colored_Cube_Puzzles (C_36all.csv): all 30
#    cubes agree.
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
            for u in adj[v]:
                if u not in color:
                    color[u] = 1 - color[v]; q.append(u)
                elif color[u] == color[v]:
                    return False, None, None
    return True, {v for v,c in color.items() if c==0}, {v for v,c in color.items() if c==1}

unique_edges_list = [(sorted(e)[0], sorted(e)[1]) for e in edge_to_cubes.keys()]
is_bip, part0, part1 = check_bipartite(BA_CORNERS, unique_edges_list)

print("="*70)
print("GRAPH M STRUCTURE")
print("="*70)
print(f"Vertices: {len(BA_CORNERS)} — {sorted(BA_CORNERS)}")
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
      f"every vertex of M must have degree 5, got {dict(degree)}")

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

print("\nStructural assertions on M: PASS "
      "(8 vertices, 20 edges, 4 parallel pairs, bipartite, 5-regular).")
print("Cube-data assertions: PASS "
      "(30 cubes; usable corner count 8 for Ba, 0 or 2 for the rest; 9 unusable, 20 usable).")

# ============================================================
# 3. GRAPH-BASED SOLUTION NUMBER (paper's formula)
# ============================================================

def get_components(vertex_set, edge_frozensets):
    adj = defaultdict(set)
    for e in edge_frozensets:
        v1, v2 = list(e)
        adj[v1].add(v2); adj[v2].add(v1)
    visited = set(); components = []
    for v in vertex_set:
        if v in visited: continue
        comp = set(); q = deque([v])
        while q:
            u = q.popleft()
            if u in visited: continue
            visited.add(u); comp.add(u)
            for w in adj[u]:
                if w not in visited and w in vertex_set: q.append(w)
        components.append(comp)
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
# 4. BRUTE-FORCE SOLUTION NUMBER (prime product, Section 5)
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
print("RESULT 1: BRUTE-FORCE DISTRIBUTION (ground truth)")
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
print("RESULT 3: COMPARISON WITH TABLE 1 IN PAPER")
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
    print("a counterexample to at least one of the paper's formulas.\n")
    for combo, sg, sb, nc, cd, nt, kt in mismatches[:5]:
        ed = sorted([ne for _, ne, _ in cd])
        print(f"  {combo}")
        print(f"    graph formula={sg}, prime-product={sb}, components={nc}, trees={nt}, k={kt}")
        print(f"    edge distribution: {ed}, component details: {cd}")
    if len(mismatches) > 5:
        print(f"  ... and {len(mismatches) - 5} more.")

# The headline claim of the paper's verification section. Gated AFTER the diagnostic
# block above, so a failing run shows its counterexamples before it exits non-zero.
check(len(mismatches) == 0,
      f"the graph formulas and the prime-product brute force disagree on {len(mismatches)} "
      f"collection(s); the paper claims they agree on all {total}")

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
if True:
    sols_3 = set(s for _, s, _ in cases_3comp_k0)
    print(f"Prime-product brute force gives: {sols_3}")
    ok3 = (sols_3 == {4})
    print(f"Agrees with 4(0+1) = 4 on every collection? {ok3}")
    check(ok3, f"Lemma wTarget3components fails at k=0: brute force gives {sols_3}, expected 4")
    print(f"Example: {cases_3comp_k0[0][0]}")
    print(f"  Components (vertices, edges, is_tree): {cases_3comp_k0[0][2]}")

print("\n--- Four components, tree with k=1, distribution (1,2,2,2) ---")
print("Paper's Lemma wTfourcomponents: solution number = 8(k+1), so 16 when k=1.")
print(f"Collections found: {len(cases_4comp_1222)}")
check(len(cases_4comp_1222) == 8,
      f"expected 8 collections of distribution (1,2,2,2), found {len(cases_4comp_1222)}")
if True:
    sols_1222 = set(s for _, s, _ in cases_4comp_1222)
    print(f"Prime-product brute force gives: {sols_1222}")
    ok1222 = (sols_1222 == {16})
    print(f"Agrees with 8(1+1) = 16 on every collection? {ok1222}")
    check(ok1222, f"Lemma wTfourcomponents fails at k=1: brute force gives {sols_1222}, expected 16")
    print(f"Example: {cases_4comp_1222[0][0]}")
    print(f"  Components (vertices, edges, is_tree): {cases_4comp_1222[0][2]}")

print("\n--- Four components, tree with k=0, distribution (0,2,2,3) ---")
print("Paper's Lemma wTfourcomponents: solution number = 8(k+1), so 8 when k=0.")
print("Structure: Ba sits on the isolated vertex (1 way); two 2-cycles and one")
print("3-edge unicyclic component each contribute a factor of 2, giving 1*2*2*2 = 8.")
print(f"Collections found: {len(cases_4comp_0223)}")
check(len(cases_4comp_0223) == 24,
      f"expected 24 collections of distribution (0,2,2,3), found {len(cases_4comp_0223)}")
if True:
    sols_0223 = set(s for _, s, _ in cases_4comp_0223)
    print(f"Prime-product brute force gives: {sols_0223}")
    ok0223 = (sols_0223 == {8})
    print(f"Agrees with 8(0+1) = 8 on every collection? {ok0223}")
    check(ok0223, f"Lemma wTfourcomponents fails at k=0: brute force gives {sols_0223}, expected 8")
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

# Post-correction consistency check
print()
print("CONSISTENCY CHECK:")
match_direct = all(paper.get(sn,0) == dist_brute.get(sn,0) for sn in all_sns)
print(f"  Paper distribution table == brute force? {match_direct}")
check(match_direct, "Paper distribution table (SolnDist) does NOT match brute force. Did it drift?")

print("\n" + "="*70)
# ============================================================
# Emit the machine-readable data behind the paper's distribution table,
# so a reader can diff a run against the published numbers directly.
# ============================================================
import csv as _csv
import os as _os

_out = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "solution_number_distribution.csv")
try:
    _fh = open(_out, "w", newline="")
except OSError as _e:
    print(f"\n(Could not write {_os.path.basename(_out)}: {_e}. Verification itself is unaffected.)")
    _fh = None
if _fh is not None:
  with _fh:
    _w = _csv.writer(_fh)
    _w.writerow(["solution_number", "num_collections_brute_force",
                 "num_collections_graph_formula", "num_collections_in_paper"])
    for _sn in sorted(k for k in dist_brute if k > 0):
        _w.writerow([_sn, dist_brute[_sn], dist_graph.get(_sn, 0), paper.get(_sn, "")])
    _w.writerow(["total", nonzero_brute, nonzero_graph, sum(paper.values())])
    print(f"\nWrote {_os.path.basename(_out)} "
          f"({len(paper)} solution numbers, {nonzero_brute:,} solvable collections).")

print("FINAL SUMMARY")
print("="*70)
_table_ok = all(paper[sn] == dist_brute.get(sn, 0) for sn in paper) and \
            sum(paper.values()) == nonzero_brute
print(f"""
1. GRAPH M: {len(BA_CORNERS)} vertices, {len(edges)} edges (cubes),
   {n_parallel_pairs} pairs of parallel edges, bipartite={is_bip},
   every vertex of degree {min(degree.values())}. Asserted above.

2. Distribution table of the paper (label SolnDist): reproduced on all {len(paper)} solution numbers?
   {_table_ok}. Total solvable collections = {nonzero_brute:,}.

3. Lemma wTfourcomponents, solution number 8(k+1):
   - k=0, distribution (0,2,2,3): {len(cases_4comp_0223):,} collections, all sol=8.
   - k=1, distribution (1,2,2,2): {len(cases_4comp_1222):,} collections, all sol=16.

4. Lemma wTarget3components, solution number 4(k+1):
   - k=0, distribution (0,a,7-a), a in {{2,3}}: {len(cases_3comp_k0):,} collections, all sol=4.

5. CROSS-VALIDATION: graph-theoretic formulas vs the prime-product brute force of
   arXiv:2407.13208, over all {total:,} usable-for-Ba collections.
   Mismatches: {len(mismatches)}.
""")
