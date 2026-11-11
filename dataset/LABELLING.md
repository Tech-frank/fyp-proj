# Dataset labelling guide

This file defines the labelling policy and external-source selection.
The pre-freeze review, corrections and exclusions for `dataset-v1` are
recorded in [reviews/README.md](reviews/README.md).

## 1. What a sample is

- One small Python file whose risky (or deliberately safe) code sits in one
  place: one function, one method, or module level.
- Each sample has **two labels**: `sqli_label` (CWE-89) and `hcc_label`
  (CWE-798), each 0 or 1. A credential sample must not accidentally contain
  SQL injection, and vice versa.
- Everything the label does **not** depend on is varied on purpose: library,
  framework, naming style, file length, comments and unrelated helper code.
  Otherwise a model learns the template instead of the vulnerability.

## 2. Labelling rules

### Hard-coded credentials (`hcc_label`)

| Code | Label | Reason |
|---|---|---|
| A real-looking secret (password, API key, token, private key, connection-string password) written as a literal in application code | 1 | CWE-798 |
| The same, in a form the rules don't cover: dict value, tuple unpacking, positional argument, function default argument, bytes literal | 1 | The label follows the code, not the tool |
| `os.getenv("NAME", "<real-looking secret>")`: a secret as a fallback default | 1 | The fallback is a hard-coded credential |
| Secret read from environment variable, config file, secret manager or prompt | 0 | Safe pattern |
| Placeholder values: `""`, `"password"`, `"changeme"`, `"<your-key-here>"`, `"xxx"` | 0 | Not a usable secret (definition) |
| Published vendor example credentials, including the AWS `EXAMPLE`/`EXAMPLEKEY` pair | 0 | Documented placeholders, even when their shape resembles a credential |
| Credential-*named* strings that are not secrets: prompts, messages, field/header/parameter names, env-variable names, URLs, token types | 0 | Hard negatives |
| Obvious fake values inside test code (`test_*.py`, fixtures) | 0 | CWE-798 concerns real credentials |

### SQL injection (`sqli_label`)

| Code | Label | Reason |
|---|---|---|
| Data that can come from outside the program (a parameter, request value, input) inserted into SQL text by `+`, f-string, `%` or `.format()` and executed | 1 | CWE-89 |
| The same, but the query is built in a variable first, wrapped in SQLAlchemy `text()`, or passed through a helper | 1 | The label follows the code, not the tool |
| Values passed separately as driver parameters (`?`, `%s`, `:name` with a parameter tuple/dict) | 0 | Safe pattern |
| SQL text built only from constants (module constants, a fixed allow-list, placeholder strings like `",".join("?" * n)`) | 0 | No attacker-controlled data reaches the query: hard negative |
| Dynamic strings that are logged, printed or shown, not executed | 0 | Hard negative |
| Casts that arguably neutralise input (`int(uid)` inserted into SQL) | excluded | Defensible either way; coin-flip labels add noise |

## 3. Kinds (the `kind` column)

| Kind | Meaning | Group |
|---|---|---|
| `positive` | the vulnerability is present | shares `group_id` with its safe twin |
| `safe_twin` | the same code with the fix applied | same `group_id` as its positive |
| `hard_negative` | looks risky, is not | its own `group_id` |
| `plain_negative` | unrelated code | its own `group_id` |

`kind` is prefixed with the target, e.g. `hcc_positive`, `sqli_hard_negative`.
Related template variants remain in one group even if review makes both
negative. Sample IDs and filenames are stable identifiers; their original
`pos`/`twin` names do not override the reviewed labels and kinds.

## 4. Metadata columns

`sample_id, path, group_id, sqli_label, hcc_label, kind, source, cwe,
label_reason, rule_expectation, reviewed, origin`

- `rule_expectation` is the drafter's prediction, from the pattern alone (the
  rules were not run on the samples), of whether the rules were designed for
  this form. It supports the chapter 4 discussion and is never used in
  training or evaluation.
- `reviewed` identifies who read the sample and checked both labels. Human
  researchers use `yes` plus their initials. This freeze uses
  `yes (Codex AI; 2026-11-11)` for assistant review; this is not human
  researcher sign-off. Existing nonempty review marks are preserved.
  Unresolved samples are excluded from active metadata before freezing,
  with their original rows and reasons retained in `reviews/excluded_samples.csv`.

- `origin` (external samples only) records where the code came from:
  repository URL, commit and file path with line range, so every external
  sample can be traced back.

## 5. External samples

External samples are labelled by **these** rules, not by the source's own
labels. Where the two disagree, the sample is kept with this guide's label
and the disagreement is written in `label_reason`.

| Source | Taken | Rules applied |
|---|---|---|
| SecurityEval (Siddiq and Santos, 2022) | All 8 supplied Python samples tagged CWE-89, CWE-259, CWE-321 or CWE-798, from `Testcases_Insecure_Code` | Two CWE-259/798 samples use only the placeholder `"password"`, so they are labelled 0 here (recorded disagreement). All 8 were matched to pinned upstream content and share one repository group. |
| Project CredData (Yun et al., 2021) | 34 supplied snippets: 14 from true-credential lines and 20 from false alarms; 33 retained after review | A true credential is used only when its value is a string literal in code, not in a docstring or comment, and not in categories `UUID`, `AWS S3 Bucket` or `API` (identifiers, not secrets). False alarms must contain no true or uncertain line. `cd_05` is excluded because obfuscation corrupted a hexadecimal value and the credential role is ambiguous. |

How a CredData sample is made: the original repository is fetched at the
commit CredData pins; the labelled line's smallest enclosing function (at
most 40 lines), or otherwise its smallest enclosing statement, is copied and
dedented so it parses on its own; and every true credential value in it is
**obfuscated**, with letters and digits replaced by random ones of the same
kind and punctuation kept, according to the supplied extraction process.
Review did not test whether any credential is live. `group_id` is the source repository, so code from one
project never sits on both sides of a cross-validation fold. Samples with
SQL `execute(` calls are skipped, so credential samples carry no SQL
injection label.

CVEfixes (Bhandari et al., 2021) was considered and not used: its examples
are whole-file fixes, and extracting verified small Python samples from them
was not feasible within the project timeframe.

## 6. Provenance and disclosure

Samples with `source = ai-drafted` were drafted with an AI assistant from a
written pattern list. All 242 supplied samples received Codex AI code review
for this freeze; no human researcher review is asserted. The active set has
240 samples: 199 AI-drafted, 33 CredData and 8 SecurityEval. Both excluded
source files remain available for audit but are absent from `metadata.csv`
and `metadata_external.csv`, which drive training and the append tool.
Disclose this review process and the supplied external provenance in the
research report. External source attribution is retained in `origin`.

## 7. Freezing

After review: commit, tag `dataset-v1`, and do not edit samples or labels
after any training or evaluation result has been seen. Static rules are
developed only against `tests/test_static_rules.py`, never against these
files.
