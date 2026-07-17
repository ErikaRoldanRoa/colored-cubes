# Colored Cubes · solution numbers for the *Eight Blocks to Madness* puzzle

Companion verification code for

> Inga Johnson and Erika Roldán Roa, *Solution Numbers for Eight Blocks to Madness Puzzle*.

The results verified here first appeared in the preprint
[arXiv:2407.13208](https://arxiv.org/abs/2407.13208); the journal version is in preparation, and this
code tracks the journal version's statements, which differ from the preprint in the four-component
case and in one table. Where the two disagree, this repository follows the journal version.

`verify_graph_M.py` independently re-computes the paper's structural and numerical claims about the
graph $M$ and the distribution of solution numbers, by two methods that share only their input data.

---

## The problem, in one paragraph

The 30 **MacMahon cubes** are the cubes whose six faces are painted with six colours, each colour
appearing at least once (up to rotation there are exactly $6!/24 = 30$). Fix one of them as the
**target** $T$. The $2\times2\times2$ **target puzzle** asks for eight distinct MacMahon cubes that
can be assembled into a $2\times2\times2$ block whose exterior is coloured like a magnified $T$ —
interior faces need not match. A collection's **solution number** is the number of distinct ways its
eight cubes can be arranged to do this. Of the $\binom{30}{8} = 5{,}852{,}925$ possible collections,
exactly $133{,}680$ have a nonzero solution number for a given target.

The paper answers this with a graph. Taking $T = \mathrm{Ba}$ (any target reduces to this one by
recolouring), $M$ is the graph whose 8 vertices are $\mathrm{Ba}$'s corner numbers and whose 20 edges
are the 20 cubes sharing exactly two corner numbers with it. For a collection $W$, the subgraph
$G_W \subseteq M$ determines the solution number from its component structure: throughout, **$n$** is
the number of connected components of $G_W$, and **$k$** is the number of edges of its unique tree
component (a tree with $k = 0$ is a single vertex, occupied by the target itself).

---

## What the script checks

Enumerating all $\binom{21}{8} = 203{,}490$ collections of eight cubes drawn from the 21 cubes usable
for $\mathrm{Ba}$ — the 20 above together with $\mathrm{Ba}$ itself. (Note that $\binom{21}{8}$ counts
*every* such collection; only $\binom{20}{7} = 77{,}520$ of them actually contain $\mathrm{Ba}$.)

| Claim | How it is checked |
|---|---|
| $M$ has 8 vertices, 20 edges, four pairs of parallel edges, is bipartite, and is 5-regular | Built from the cube colourings; **checked**, so a failure stops the run. ($M$ is loopless by construction: an edge joins the two *distinct* corner numbers a cube shares with the target.) |
| The cube data itself: the target shares all 8 of its corner numbers with itself, every other cube shares exactly 0 or 2, and exactly 9 of the 30 cubes are unusable for the target | Computed from the colourings; **checked** |
| The distribution of solution numbers over the $133{,}680$ solvable collections (the paper's distribution table — Table 2 in the current draft) | Full enumeration by the prime-product method, compared entry by entry |
| The theorem for target-free collections: solution number $= 2^{n}$ | Graph component/tree analysis vs. brute force on every collection; agreement is **checked**, not merely reported |
| The theorem for target-containing collections: $8$, $2(k{+}1)$, $4(k{+}1)$, $8(k{+}1)$ for $n = 1,2,3,4$ | Graph component/tree analysis vs. brute force, on every collection |
| The three-component lemma at $k = 0$: exactly $1{,}728$ collections, all with solution number $4$ | Filtered from the enumeration; both the count and the value are **checked** |
| The four-component lemma at $k = 0$: exactly $24$ collections, all with solution number $8$ | Filtered from the enumeration; both the count and the value are **checked** |

**Scope.** This repository covers the paper above only. It does not cover the companion work on
universal sets and buildability distributions, nor does it re-derive every incidental number in the
text (for example the count of spanning paths used in the maximum-solution argument, or the
probability in the corollary) — those are short hand computations stated in the paper itself.

**On independence.** The two methods are independent in their *logic*, not in their *input*. Method A
applies the paper's graph-theoretic formulas to the component structure of $G_W$. Method B is the
prime-product brute force of [arXiv:2407.13208](https://arxiv.org/abs/2407.13208), which counts
placements directly and uses none of the paper's graph theory. Both read the same table of 30 cube
colourings, so that table is a shared assumption — it has been cross-checked, cube by cube, against
the independently produced dataset in
[IJohnson-math/Colored_Cube_Puzzles](https://github.com/IJohnson-math/Colored_Cube_Puzzles)
(`C_36all.csv`); all 30 cubes agree.

---

## Running it

```
python3 verify_graph_M.py
```

Python 3.8 or later. No dependencies — standard library only, no NumPy, no NetworkX. Deterministic:
no randomness, no network access, no floating-point arithmetic.

It is single-threaded and CPU-bound: about 30 s on an idle Apple M2, and proportionally longer on a
busy or thermally throttled machine (we have measured the same build at anything from 28 s to 80 s
on one laptop depending only on how warm it was). Expect roughly a minute; nothing is wrong if it
takes two.

You should see, in order: the structure of $M$, then `Structural assertions on M: PASS` and
`Cube-data assertions: PASS`; the distribution table with a `YES` in every comparison column;
`Total mismatches: 0`; the $k = 0$ case counts ($1{,}728$ and $24$); and a final summary. Every
check is a hard gate — a failure aborts the run with `VERIFICATION FAILED: …` and a non-zero exit
status, and is a genuine disagreement with the paper worth reporting. (The gates are ordinary
conditionals, not `assert`, so they are not silently removed by `python3 -O`.)

The run also writes **`solution_number_distribution.csv`** — the distribution by both methods
alongside the published values, so a run can be diffed against the paper directly. A committed copy
of that file is the expected output.

---

## What's here

```
verify_graph_M.py                  The verifier: builds M, enumerates, cross-validates.
solution_number_distribution.csv   Expected output — the distribution by both methods.
README.md                          This file.
LICENSE                            Tiered: code MIT · documentation CC-BY 4.0 · data CC-BY 4.0.
```

## Related code

[IJohnson-math/Colored_Cube_Puzzles](https://github.com/IJohnson-math/Colored_Cube_Puzzles) holds
the original research notebooks behind the preprint, covering both the solution-number results and
the companion work on universal sets, for cube sets $C_{3,n}$ with $n = 2, \dots, 6$. This repository
is narrower by design: a self-contained, dependency-free re-derivation of the claims in the paper
above.

---

## Citing

Please cite the paper:

```bibtex
@misc{johnson2024solutionnumbers,
  title         = {Solution Numbers for Eight Blocks to Madness Puzzle},
  author        = {Inga Johnson and Erika Rold\'an},
  year          = {2024},
  eprint        = {2407.13208},
  archivePrefix = {arXiv},
  primaryClass  = {math.CO},
  url           = {https://arxiv.org/abs/2407.13208}
}
```

Journal citation details will replace this on publication, and the repository will be archived on
Zenodo at that point so the verification corresponds to a frozen commit.

## Authors

**Inga Johnson** — Department of Mathematics, Willamette University, Salem, Oregon ·
ijohnson@willamette.edu

**Erika Roldán Roa** — Max Planck Institute for Mathematics in the Sciences, Leipzig ·
ScaDS.AI, Leipzig University · Section de mathématiques, Université de Genève ·
roldan@mis.mpg.de · [erikaroldan.net](https://erikaroldan.net)

Authors listed alphabetically; equal contribution throughout.

## Reporting a discrepancy

If a run disagrees with the paper, please open an issue with your Python version and the output of

```
python3 verify_graph_M.py 2>&1 | tail -40
```
