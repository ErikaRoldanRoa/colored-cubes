# Colored Cubes · solution numbers for the *Eight Blocks to Madness* puzzle

Companion verification code for

> Inga Johnson and Érika Roldán, *Solution Numbers for Eight Blocks to Madness, Part 1*.

The results checked here first appeared in the preprint
[arXiv:2407.13208](https://arxiv.org/abs/2407.13208). This code follows the statements of the paper
above; where the paper corrects the preprint, the corrected statements are the ones checked.

`verify_graph_M.py` re-computes the paper's structural and numerical claims about the graph $M$ and
the distribution of solution numbers, by two methods that share only their input data (a table of
corner numbers), and by a third that rebuilds the cubes from their colorings and does not use that
table.

---

## The problem, in one paragraph

The 30 **MacMahon cubes** are the cubes whose six faces are painted with six colors, each color
appearing at least once (up to rotation there are exactly $6!/24 = 30$). Fix one of them as the
**target** $T$. The $2\times2\times2$ **target puzzle** asks for eight distinct MacMahon cubes that
can be assembled into a $2\times2\times2$ block whose exterior is colored like a magnified $T$;
interior faces need not match. A collection's **solution number** is the number of distinct ways its
eight cubes can be arranged to do this. Of the $\binom{30}{8} = 5{,}852{,}925$ possible collections,
exactly $133{,}680$ have a nonzero solution number for a given target.

The paper answers this with a graph. Taking $T = \mathrm{Ba}$ (any target reduces to this one by
recoloring), $M$ is the graph whose 8 vertices are $\mathrm{Ba}$'s corner numbers and whose 20 edges
are the 20 cubes sharing exactly two corner numbers with it. For a collection $W$, the subgraph
$G_W \subseteq M$ determines the solution number from its component structure: throughout, **$n$** is
the number of connected components of $G_W$, and **$k$** is the number of edges of its unique tree
component (a tree with $k = 0$ is a single vertex, occupied by the target itself).

---

## What the script checks

It enumerates all $\binom{21}{8} = 203{,}490$ collections of eight cubes drawn from the 21 cubes
usable for $\mathrm{Ba}$: the 20 above together with $\mathrm{Ba}$ itself. ($\binom{21}{8}$ counts
*every* such collection; only $\binom{20}{7} = 77{,}520$ of them contain $\mathrm{Ba}$.)

| Claim | How it is checked |
|---|---|
| $M$ has 8 vertices, 20 edges, four pairs of parallel edges, is bipartite, and is 5-regular | Built from the table of corner numbers; **checked**, so a failure stops the run. ($M$ is loopless by construction: an edge joins the two *distinct* corner numbers a cube shares with the target.) |
| The cube data: the target shares all 8 of its corner numbers with itself, every other cube shares exactly 0 or 2, and exactly 9 of the 30 cubes are unusable for the target | Computed from the table; **checked** |
| The Conway names fit the tableau: for each cube $\mathrm{Xy}$, the cubes sharing no corner number with it are the rest of row $\mathrm{X}$ and column $\mathrm{y}$ and its mirror cube $\mathrm{Yx}$, whose corner numbers are those of $\mathrm{Xy}$ read the other way round; each row and each column holds all 40 corner numbers | Computed from the table; **checked**. This catches a name attached to the wrong cube; it checks the names against this structure only. |
| The distribution of solution numbers over the $133{,}680$ solvable collections (Table 2 of the paper) | Full enumeration by the prime-product method, compared entry by entry; **checked** |
| The theorem for target-free collections: solution number $= 2^{n}$ | Graph component/tree analysis vs. brute force on every collection; agreement is **checked** |
| The theorem for target-containing collections: $8$, $2(k{+}1)$, $4(k{+}1)$, $8(k{+}1)$ for $n = 1,2,3,4$ | Graph component/tree analysis vs. brute force on every collection; agreement is **checked** |
| The three-component lemma at $k = 0$: exactly $1{,}728$ collections, with edge distributions $(0,2,5)$ and $(0,3,4)$, all with solution number $4$ | Filtered from the enumeration; the count, the edge distributions and the value are **checked** |
| The four-component lemma at $k = 0$: exactly $24$ collections, all with solution number $8$ | Filtered from the enumeration; both the count and the value are **checked** |
| **Method C (C1).** The 30 MacMahon cubes: rebuilt from all $6! = 720$ colorings with six distinct colors, up to the 24 rotations, they are exactly the 30 cubes of the table | Compared as sets of corner numbers; **checked**. This does not check the reading direction of corner numbers (reading them the other way turns each cube into its mirror cube, also one of the 30); the Conway names are checked only against the tableau, as in the third row. |
| **Method C (C2).** The same distribution (Table 2) for every one of the 30 targets, with 1 of the 81 maximal collections avoiding the target and 80 containing it | Every target solved by placing the colored cubes in the corners of the $2\times2\times2$ block; **checked**. For every target, the distribution over the collections containing it is also compared with the one methods A and B give over the collections containing $\mathrm{Ba}$. |
| **For Ba (D1).** The 81 collections with solution number $16$: $1$ avoids $\mathrm{Ba}$ (the four diagonal pairs) and $80$ contain it, $80 = 8 + 72$, and $72 = 6 \times 12$ (two diagonal pairs, then a path of three cubes spanning the other four corner numbers) | Filtered from the enumeration, and the 72 rebuilt from $M$ as in the paper; **checked** |
| **For Ba (D2).** The corollary: $p = 133{,}680 / 5{,}852{,}925 \approx 0.0228$ | Exact fraction; **checked** |

**Scope.** This repository covers the paper above only. It does not cover the companion work on
universal sets and buildability distributions.

**Where the cube data comes from.** The table of the 30 cubes in `verify_graph_M.py` (each cube's
Conway name and its eight corner numbers) is taken from the authors' dataset: `C36.csv` in
[IJohnson-math/Colored_Cube_Puzzles](https://github.com/IJohnson-math/Colored_Cube_Puzzles), also
printed as Table 3 of [arXiv:2407.13208](https://arxiv.org/abs/2407.13208).

**On independence.** The two methods are independent in their *logic*, not in their *input*. Method A
applies the paper's graph-theoretic formulas to the component structure of $G_W$. Method B is the
prime-product algorithm of [arXiv:2407.13208](https://arxiv.org/abs/2407.13208) (Section 7),
reimplemented here, which counts placements directly and uses none of the paper's graph theory. Both
read the same table of corner numbers, so that table is a shared assumption. Method C removes it:
it rebuilds the 30 cubes from their face colorings, compares them with the table, and then solves
every target by trying each cube in each corner of the $2\times2\times2$ block in each of its 24
orientations; this count uses neither corner numbers nor graph theory. Along the way it checks that a
cube fits a corner of the block exactly when it carries the target's corner number there, which is
the rule methods A and B rely on.

---

## Running it

```
python3 verify_graph_M.py
```

Standard library only (no NumPy, no NetworkX), no network access, no randomness. Tested with
Python 3.9.6 and 3.11.5; it runs in about half a minute on a laptop.

Every check is a hard gate: a failure aborts the run with `VERIFICATION FAILED: …` and a non-zero
exit status. A failure on an unmodified copy means the script and the paper disagree somewhere;
please report it (see below). (The gates are ordinary conditionals, not `assert`, so they are not
removed by `python3 -O`.)

The printed output is the same, byte for byte, on every run, under Python 3.9 and 3.11 and
whatever the hash seed; `expected_output.txt` is a committed copy of it:

```
python3 verify_graph_M.py | diff - expected_output.txt
```

With `--out PATH` the run also writes the distribution of solution numbers by both methods,
alongside the published values, as a CSV file; **`solution_number_distribution.csv`** is the
committed copy. A plain run writes no file, so the committed copy is never overwritten:

```
python3 verify_graph_M.py --out /tmp/run.csv && cmp /tmp/run.csv solution_number_distribution.csv
```

### One command per claim

Each command runs the full verification and prints the lines that state one claim. To check them
all at once, run `python3 verify_graph_M.py > run.txt` once and apply each filter to `run.txt`.

| Claim | Command |
|---|---|
| Structure of $M$ | `python3 verify_graph_M.py \| grep 'Structural assertions'` |
| Cube data (0 or 2 shared corners, 9 unusable) | `python3 verify_graph_M.py \| grep 'Cube-data assertions'` |
| The Conway names fit the tableau | `python3 verify_graph_M.py \| grep -A3 'Conway-name assertions'` |
| Table 2 | `python3 verify_graph_M.py \| sed -n '/^RESULT 3/,/^Total/p'` |
| Both theorems, on every collection | `python3 verify_graph_M.py \| grep 'Total mismatches'` |
| The $1{,}728$ and $24$ collections with $k = 0$ | `python3 verify_graph_M.py \| grep -A7 'tree with k=0'` |
| The 30 cubes rebuilt from the colorings | `python3 verify_graph_M.py \| grep -A2 '^C1\.'` |
| Table 2 and the 1 + 80 split for all 30 targets | `python3 verify_graph_M.py \| grep -A4 '^C2\.'` |
| The 81 collections with solution number 16, and $72 = 6 \times 12$ | `python3 verify_graph_M.py \| grep -A3 '^D1\.'` |
| The corollary's $p$ | `python3 verify_graph_M.py \| grep '^D2\.'` |

---

## What's here

```
verify_graph_M.py                  The verifier: builds M, enumerates, cross-validates (methods A, B, C).
solution_number_distribution.csv   Expected --out file: the distribution by methods A and B.
expected_output.txt                Expected output: everything the verifier prints.
README.md                          This file.
LICENSE                            Tiered: code MIT · documentation CC-BY 4.0 · data CC-BY 4.0.
```

## Related code

[IJohnson-math/Colored_Cube_Puzzles](https://github.com/IJohnson-math/Colored_Cube_Puzzles) holds
the original research notebooks behind the preprint, covering both the solution-number results and
the companion work on universal sets, for cube sets $C_{3,n}$ with $n = 2, \dots, 6$, and the cube
data this repository uses. This repository is narrower by design: a self-contained,
dependency-free re-derivation of the claims in the paper above.

---

## Citing

**The paper.** Until the paper is published, please cite the preprint:

```bibtex
@misc{johnson2024solutionnumbers,
  title         = {Solution Numbers for Eight Blocks to Madness Puzzle},
  author        = {Inga Johnson and Erika Roldan},
  year          = {2024},
  eprint        = {2407.13208},
  archivePrefix = {arXiv},
  primaryClass  = {math.CO},
  note          = {Preprint},
  url           = {https://arxiv.org/abs/2407.13208}
}
```

**This code.** Please cite the repository URL together with the commit you ran
(`git rev-parse HEAD`).

## Authors

**Inga Johnson**, Department of Mathematics, Willamette University ·
ijohnson@willamette.edu

**Érika Roldán**, Max Planck Institute for Mathematics in the Sciences, Leipzig ·
ScaDS.AI, Leipzig University · Section de mathématiques, Université de Genève ·
roldan@mis.mpg.de · [erikaroldan.net](https://erikaroldan.net)

Authors listed alphabetically; equal contribution throughout.

## Reporting a discrepancy

If a run disagrees with the paper, please open an issue with your Python version and the output of

```
python3 verify_graph_M.py 2>&1 | tail -40
```
