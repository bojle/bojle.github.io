Title: Typo Correction in LLVM
Date: 2025-09-07
Tags: compilers, LLVM

If you're in the business of writing code, you might have noticed that your
compiler is capable of identifying and suggesting fixes for the typos in your
programs.

For example, take the following code:

```cpp
int foo(int x, int y) {
  int pacman = x * y;
  return pamcan;
}
```
Compiling this generates an error identifying that `pamcan` is an undeclared
identifier and a valid identifier by the name `pacman` is available
```bash
$ clang -c a.c -o a.o
a.c:3:10: error: use of undeclared identifier 'pamcan'; did you mean 'pacman'?
    3 |   return pamcan;
      |          ^~~~~~
      |          pacman
a.c:2:7: note: 'pacman' declared here
    2 |   int pacman = x * y;
      |       ^
1 error generated.
```
We are interested in how the compiler figures out that `pacman` is a valid
correction for our typo. This article explains how the compiler (clang, to be
specific) does it.

## Parsing and Semantic Analysis

This type of error is detected by the compiler's [**Semantic
Analyzer**](https://users.sussex.ac.uk/~mfb21/compilers/slides/6-handout.pdf),
a component of the parser. In clang, the semantic analyzer is known as
[**Sema**](https://youtu.be/5kkMpJpIGYU?si=A_rhqKwLLspiG2Yd&t=1366)

Grepping for the diagnostic message "use of undeclared identifier" within the
[`llvm-project`](https://github.com/llvm/llvm-project/) monorepo leads to the
file `DiagnosticSemaKinds.td`. 

```bash
~/dev/llvm-project/clang $ rg "use of undeclared identifier" -g '!*test*' -g '!*docs*' -g '!*www*'
include/clang/Basic/DiagnosticSemaKinds.td
6111:def err_undeclared_var_use : Error<"use of undeclared identifier %0">;
6113:  "use of undeclared identifier %0; "
11285:  "use of undeclared identifier %0; did you mean %1?">;
```

This is a [*TableGen*](https://llvm.org/docs/TableGen/)  file, an abstraction
used by LLVM to maintain information files. It is compiled into the
`DiagnosticSemaKinds.inc` header file. The specific diagnostic is declared as
the following and can be found in the build directory:

```
DIAG(err_undeclared_var_use_suggest, CLASS_ERROR, (unsigned)diag::Severity::Error, "use of undeclared identifier %0; did you mean %1?", 0, SFINAE_SubstitutionFailure, false, true, true, false, 3)
```

Now, we can begin our detective hunt for the part of code we're interested in.
We'll use the trustworthy 'grep' again to search for `err_undeclared_var_use`.

We land on
[Sema::DiagnoseEmptyLookup](https://github.com/llvm/llvm-project/blob/e6c63d920dec3e8874ac1dc3c3f19fb822f0ab06/clang/lib/Sema/SemaExpr.cpp#L2513),
which uses the string we searched for. As the name suggests, this function
figures out what to do when a symbol is not present in the symbol table. It
first tries to check if this is an unqualified look up. If this fails, it tries
to correct for a typo. This is the snippet where the decision is made:

```cpp
  // We didn't find anything, so try to correct for a typo.
  TypoCorrection Corrected;
  if (S && (Corrected =
                CorrectTypo(R.getLookupNameInfo(), R.getLookupKind(), S, &SS,
                            CCC, CorrectTypoKind::ErrorRecovery, LookupCtx))) {
    std::string CorrectedStr(Corrected.getAsString(getLangOpts()));
    ...

```

It calls the function
[Sema::CorrectTypo](https://github.com/llvm/llvm-project/blob/be1e50f56af8e270a0396eef8f62626fbbb84996/clang/lib/Sema/SemaLookup.cpp#L5413)
which mainly sets thresholds for what results are acceptable as corrections or
fails otherwise. `CorrectTypo` calls
[Sema::makeTypoCorrectionConsumer](https://github.com/llvm/llvm-project/blob/be1e50f56af8e270a0396eef8f62626fbbb84996/clang/lib/Sema/SemaLookup.cpp#L5269).
`makeTypoCorrectionConsumer` iterates over available identifiers, calls
`FoundName` which adds a name if its edit distance is less than a particular
threshold. We ultimately land on the
[ComputeMappedEditDistance](https://github.com/llvm/llvm-project/blob/be1e50f56af8e270a0396eef8f62626fbbb84996/llvm/include/llvm/ADT/edit_distance.h#L44C1-L103C2)
function, which is the meat and potato of this operation. 

Following text will be discussing this. 

## Levenshtein Distance

The [**Levenshtein
Distance**](https://en.wikipedia.org/wiki/Levenshtein_distance), or edit
distance, quantifies the minimum number of single-character edits
(insertions, deletions, or substitutions) required to change one string into
another. LLVM implements a space-optimized, dynamic programming solution for
this in the `ComputeMappedEditDistance` function.

Here's an abridged but pure C++ implementation of the distance function implemented by LLVM:

```cpp
size_t edit_distance(const std::string &s1, const std::string &s2) {
  size_t m = s1.size();
  size_t n = s2.size();
  std::vector<size_t> row(n + 1);
  for (size_t i = 1; i < row.size(); ++i) {
    row.at(i) = i;
  }

  for (size_t y = 1; y <= m; ++y) {
    row.at(0) = y;
    size_t best_this_row = row.at(0);
    size_t previous = y - 1;
    auto cur_item = s1.at(y - 1);
    for (size_t x = 1; x <= n; ++x) {
      int old_row = row.at(x);
      row.at(x) = std::min(previous + ((cur_item == s2.at(x - 1)) ? 0u : 1u), std::min(row.at(x-1), row.at(x) + 1));
      previous = old_row;
      best_this_row = std::min(best_this_row, row.at(x));
    }
  }
  size_t res = row[n];
  return res;
}
```

The algorithm can be understood by visualizing a 2D grid, `D`, where
`D[i][j]` represents the Levenshtein distance between the first `i`
characters of the first string and the first `j` characters of the second.
The algorithm fills this table, and the final distance is the value in the
bottom-right cell, `D[m][n]`.

The code implements this by translating the recursive definition into an
iterative process. It maintains only the current and previous rows of the
conceptual table to save space.
  
* **Base Cases:** The costs for transforming an empty string into a prefix of
  another string are represented by the first row and column of the table. In
the code, this is handled by the initial loop that populates the `row` vector
and the line `row.at(0) = y;` within the main loop.
  
* **Recursive Step:** The calculation for `D[i][j]` is based on three smaller
  subproblems: deletion, insertion, and substitution. The code calculates the
value for `row.at(x)` (which corresponds to `D[i][j]`) by using values from
the previous row (`previous` and `old_row`) and the current row
(`row.at(x-1)`). This mirrors the recursive formula:

```cpp
1 + min({deletion}, {insertion}, {substitution}).
```

## Experiments with the Typo Correction System

Armed with the knowledge that suggestion for typo correction is based on
distance between two words, there should be a threshold after which
suggestions should be discarded. We can find the code for this in
`Sema::CorrectTypo`:

```cpp
  // Make sure the best edit distance (prior to adding any namespace qualifiers)
  // is not more that about a third of the length of the typo's identifier.
  unsigned ED = Consumer->getBestEditDistance(true);
  unsigned TypoLen = Typo->getName().size();
  if (ED > 0 && TypoLen / ED < 3)
    return FailedCorrection(Typo, TypoName.getLoc(), RecordFailure);

  TypoCorrection BestTC = Consumer->getNextCorrection();
  TypoCorrection SecondBestTC = Consumer->getNextCorrection();
  if (!BestTC)
    return FailedCorrection(Typo, TypoName.getLoc(), RecordFailure);

```
If the best edit distance "is not more than a third of the length of the
typo's identifier", it'll move to the next correction. If there are no other
corrections, it exits early. 

We can, in fact, trigger this by changing the variable name so that it's more
than 1/3 of typo's length. We need atleast `TypoLen` of 6 and an edit distance `ED`
of 2. 

Here's one example,

```cpp
int foo(int a) {
  int pacman = a + 1;
  return pamcaa;
}
```

Compiling this results in,
```bash
~/dev/llvm-project/build-clang $ ./bin/clang-22 -c a.c -o a -target riscv64
a.c:3:10: error: use of undeclared identifier 'pamcaa'
    3 |   return pamcaa;
      |          ^~~~~~
1 error generated.
```
No suggestions for this one! As expected.
