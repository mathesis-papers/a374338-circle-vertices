# Shannon's circle vertices and collinear triangular growth

The note proves Shannon's three vertex-count formulas in OEIS A374338, Markey's recorded three- and four-seed formulas, and the Markey–Pfoertner five-seed difference relation in OEIS A400701. A strip-clipped hexagon gives the growth set for every collinear seed length m >= 2 and iteration n >= 2. The strip becomes redundant exactly when n >= m-3. Counts include retained sites; the circle result applies to every distinct starting pair.

Further corollaries give the eventual width-three seed-count difference, Markey's periodic second differences, and algebraic relations with Barker's 2015 circle-addition and petal generating functions. The petal coefficients are defined by Barker's displayed rational series; independent geometric petal enumeration is a separate question.

## Build

Use Tectonic 0.17.0:

```sh
tectonic note.tex
```

Alternatively, use a current TeX Live installation with `amsmath`, `amssymb`, `amsthm`, `geometry`, `fontenc`, `lmodern`, `booktabs`, `tabularx`, and `hyperref`:

```sh
pdflatex -interaction=nonstopmode -halt-on-error note.tex
pdflatex -interaction=nonstopmode -halt-on-error note.tex
```

The bibliography is embedded in `note.tex`; no BibTeX step or external bibliography file is required.

## Exact finite checks

Python 3.10 or later, standard library only:

```sh
python3 verify.py --output verification-new.json
```

The checker uses exact integers. It compares the four named sequences through iteration 40 and arbitrary-seed shapes for m = 2 through 20 through iteration 30, including the exact stabilization threshold and the six-seed step-two obstruction. It checks the hexagon boundary identity over its stated finite parameter box and generating-function and sibling-series coefficients through the indices specified in the JSON. These finite checks supplement the written all-iteration proof.

## Formal scope

The PDF links three `.lean` files at commit `2f8421f6b90d37b4815b887f6c60987553831b20`. `ShannonA374338.result` proves the all-iteration Euclidean circle counts; `AxialGrowth.exact_shape` covers seed sizes 2 and 5 and n >= 2; `CircleGrowth.intersection_lattice` gives the geometric bridge; `HexShapeCounts.count_difference` gives the width-three polygon-count difference; `MarkeyA400701.result` proves the five-seed difference relation for n > 1. The all-seed extension, three- and four-seed results, periodic differences and series identities have written proofs in the note, beyond those declarations' scopes.

## Files

- `note.tex`: complete mathematical source and embedded references.
- `note.pdf`: readable note.
- `metadata.json`: title, creators, license, problem identifiers, and formal-source links.
- `verify.py`, `verification.json`: finite checker and its exact output.
- `LICENSE.txt`: CC BY 4.0 statement.

Creators: Haobo Ma (ChronoAI Pte Ltd, Singapore), then Wenlin Zhang (National University of Singapore; ChronoAI Pte Ltd, Singapore).

License: Creative Commons Attribution 4.0 International, `cc-by-4.0`.
