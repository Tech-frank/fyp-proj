# Dataset labelling guide

Written **before** any sample was created and frozen with the dataset. Paste
the rules into chapter 3 (dataset construction) and cite this file in
chapter 4.3.

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

## 4. Metadata columns

`sample_id, path, group_id, sqli_label, hcc_label, kind, source, cwe,
label_reason, rule_expectation, reviewed`

- `rule_expectation` is the drafter's prediction, from the pattern alone (the
  rules were not run on the samples), of whether the rules were designed for
  this form. It supports the chapter 4 discussion and is never used in
  training or evaluation.
- `reviewed` is filled in by the researcher (`yes` plus initials) after
  reading the sample and agreeing with both labels. A sample whose label is
  disputed is fixed or removed **before** the dataset is frozen.

## 5. Provenance and disclosure

Samples with `source = ai-drafted` were drafted with an AI assistant from a
written pattern list, then reviewed and labelled by the researcher. Chapter
4.3 must say so. Samples with `source = handwritten` or `creddata` are marked
accordingly.

## 6. Freezing

After review: commit, tag `dataset-v1`, and do not edit samples or labels
after any training or evaluation result has been seen. Static rules are
developed only against `tests/test_static_rules.py`, never against these
files.
