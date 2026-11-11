# Dataset-v1 review record

Review date: 2026-11-11 (Africa/Lagos). Reviewer: Codex AI, with parallel
source-code reviews and coordinating review of disputed cases. The review
marks do not represent human researcher sign-off. All review fields were
blank on receipt; existing nonempty marks would have been preserved.

All 242 supplied Python files were read against `dataset/LABELLING.md` and
checked for both SQL injection and hard-coded credentials. Labels were
adjudicated from source code and the guide, without using detector outputs
to choose labels. No sample code was executed. No model training or dataset
evaluation pipeline was run during this freeze; the training tests use
separate synthetic arrays.

## Coverage and decisions

| Review file | Supplied samples | Scope |
|---|---:|---|
| `hcc_review.csv` | 100 | Original credential samples and both labels |
| `sqli_review.csv` | 100 | Original SQL samples and both labels |
| `external_review.csv` | 42 | 34 CredData and 8 SecurityEval samples |

Each report contains one source-grounded decision per supplied sample.
`accept` means the original labels were accepted; `change` records an
applied label, kind or metadata correction; `exclude` means the sample
is not used for training or evaluation. Blank labels in excluded review
rows mean that the disputed target was not assigned an active label.

| Item | Applied decision |
|---|---|
| `hcc_pos_06` | HCC 1 to 0: it uses the exact AWS published example credential pair, which is a placeholder under the guide. Reclassified as a hard negative. |
| `hcc_twin_06` | Both labels remain 0; reclassified as a hard negative. The two AWS variants retain their shared `hcc_g06` to prevent template leakage. |
| `sqli_pos_28` | Excluded: `int(size)` executes before raw `size` interpolation. Malicious ordinary strings fail validation, making this the guide's excluded cast-neutralisation ambiguity rather than a clean positive. |
| `sqli_twin_28` | Retained with both labels 0 and reclassified as a hard negative after its counterpart was excluded. |
| `cd_05` | Excluded: the obfuscated value passed to `unhexlify` contains non-hexadecimal characters, so it fails before cryptographic use; the published GPP decryption constant also has an ambiguous credential role. |
| `cd_02`, `cd_07` | Retained as HCC positives after pinned upstream context confirmed that the literal keys are used for HMAC-SHA256 signing and verification. Their UUID-like shape alone is not a reason to relabel them as identifiers. |
| `se_01` through `se_08` | Labels retained. Added verified full commit and line ranges to `origin`; all eight share `se_securityeval`, conservatively keeping repeated connection/query templates in one fold. |

The two excluded original rows, including their original proposed labels,
are preserved in `excluded_samples.csv` with exclusion reasons. Their source
files remain unchanged in `dataset/samples/` for audit. Active training and
evaluation must use `dataset/metadata.csv`, not every file found recursively.
`metadata_external.csv` contains only the 41 retained external rows, so
rerunning `tools/add_external_samples.py` does not reintroduce an exclusion.

## Active frozen set

| Source | Active samples |
|---|---:|
| AI-drafted | 199 |
| CredData | 33 |
| SecurityEval | 8 |
| Total | 240 |

There are 166 groups, 31 SQLI positives and 46 HCC positives. The remaining
163 samples have neither label; no sample has both labels. Each target's
negative count also includes positives for the other target. Safe twins and
related variants stay grouped; CredData snippets from one repository share
their repository group. These sources include benchmark, tutorial, CTF and
exploit examples as well as application/library code; they are not all
production applications. Source-specific performance must be reported with
sample counts, especially for the small external SQLI subset.

## Provenance checks

- AWS placeholder classification was checked against
  [AWS access-key documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html).
- All eight SecurityEval snippets exactly matched upstream text after line
  ending normalization at commit
  `6f4fb70f782c6d47b02ea24341e8ef8c1eb04a6a`. Commit, path, line range and
  content hashes are recorded in `securityeval_provenance.json`.
- The two CodeQL key contexts were fetched at supplied pinned commit
  `4f4cdf434b12`; their URLs and HMAC-use rationale are in
  `external_review.csv`. Obfuscated local literal values were preserved.
- Other CredData origins and obfuscation are supplied add-on provenance;
  they were retained without claiming a fresh upstream audit of every
  original repository or a check that any credential is live. The large
  repository-fetch/extraction scripts were inspected but not run.

## Freeze verification

All supplied files parse, IDs and paths are unique, every supplied file has
a review, and active plus excluded metadata accounts for all 242 files.
There are no identical source texts or identical ASTs in the supplied set.
The append tool was checked for idempotence and review-mark preservation.
The code test suite passed with 72 tests passing and four original helper
contract tests explicitly skipped because their helpers are not implemented.

`manifest.json` records SHA-256 hashes for the dataset and review files,
with UTF-8 BOMs removed and line endings normalized to LF so the freeze can
be checked across Git's Windows line-ending conversion. It also records
the original add-on archive hash. The Git tag `dataset-v1` identifies the
complete frozen tree; future dataset corrections require a new version.
