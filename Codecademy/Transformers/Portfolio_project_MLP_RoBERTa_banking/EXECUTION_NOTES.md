# Execution and Maintenance Notes

This document contains setup instructions, implementation-change notes, verification
evidence, and historical runs. The [project README](./README.md) describes the business
purpose, modeling and privacy approach, and final protected-data results.

## Environment and dependencies

The verified environment is Windows, Python 3.14.6, PyTorch 2.14.1+cu126,
Transformers 5.20.2, PEFT 0.21.2, and an NVIDIA GeForce RTX 2070 Super with 8 GiB VRAM.
The notebook requires CUDA explicitly rather than silently falling back to CPU.

[environment_requirements.txt](./environment_requirements.txt) is the canonical
dependency manifest. The original lesson dependencies remain in
[Codecademy_environment_requirements.txt](./Codecademy_environment_requirements.txt);
do not install both manifests into the same environment.

The original list mixed incompatible PyTorch-family releases and omitted PEFT,
Accelerate, and Datasets. The tested manifest declares the notebook's direct
dependencies. The privacy work adds `wordcloud==1.9.6`, which was already installed
locally. This is the word-cloud visualization package, not `wordspace`.

PII detection reuses Transformers, PyTorch, and Hugging Face Hub. Its additional
asset is a pinned NER model, not another pip package. Rules and audit handling use
Python standard-library modules. No additional spaCy/Presidio dependency or remote
redaction API is required. Cryptography was not added merely to imply encryption:
managed storage encryption and secure transport remain deployment requirements.

## Installation and public model-cache setup

From this project directory, install the CUDA build before the notebook dependencies:

```powershell
python -m pip install torch==2.14.1 --index-url https://download.pytorch.org/whl/cu126
python -m pip install -r environment_requirements.txt
```

Cache the reviewed public weights in a separate connected setup process, before
loading any customer data:

```powershell
python -c "from huggingface_hub import snapshot_download; snapshot_download('dslim/distilbert-NER', revision='dfa2838a127384aabb82ed7719e16dab84c42a2a', allow_patterns=['*.json', 'vocab.txt', 'model.safetensors', 'README.md'])"
python -c "from huggingface_hub import snapshot_download; snapshot_download('roberta-base', revision='e2da8e2f811d1448a5b465c236feacd80ffbac7b', allow_patterns=['*.json', 'merges.txt', 'vocab.json', 'model.safetensors', 'README.md'])"
```

The notebook sets `HF_HUB_OFFLINE=1` before model imports. Both model revisions are
pinned and loaded from local caches. The detector uses `trust_remote_code=False`
and safetensors; unavailable weights cause an explicit failure, not a weaker fallback.
Model/package licensing and supply-chain approval remain institutional responsibilities.

## Notebook execution

Open [banking_classification_BERT.ipynb](./banking_classification_BERT.ipynb), select
the CUDA-enabled Python kernel, restart it, and run all cells in order. The working
directory may be this project directory or the repository root.

The approximately ten-minute target includes PII protection, preprocessing, both
model searches, validation, plots, test evaluation, saving, and inference. It excludes
initial installations and public-weight downloads. Runtime is measured rather than
enforced by silently truncating training; shared GPU load can affect it.

The supplied input CSV files are never overwritten, edited, or deleted. Redaction,
decontamination, and splitting operate on in-memory text and DataFrames only.

## Implementation and change notes

- Preserved all six original visualizations, explanatory comments, intermediate
  inspections, epoch printouts, classification reports, and intent comparisons.
  Added an aggregate PII-count chart and a protected-training-text word cloud.
- Fixed the intent-index plotting failure, source-level Pylance diagnostics, and
  undefined-metric warnings. Missing-class metrics are explicitly zero, and classes
  receiving no predictions are reported.
- Replaced test-driven checkpoint selection with shared stratified validation data.
  TF-IDF vocabulary is fitted on the training partition only.
- Added small validation-only MLP and LoRA searches, FP16, dynamic padding, and
  parameter-decision explanations. Preliminary validation improvement and runtime
  headroom motivated the expanded LoRA search, not test results.
- Added [pii_protection.py](./pii_protection.py) as a common local ingestion/inference
  boundary, plus [privacy regression tests](./test_pii_protection.py).
- Added protected inference examples, synthetic privacy release gates, and an
  aggregate-only policy/version manifest.
- Pretrained encoder loading is strict; the banking classifier is deliberately
  initialized rather than treating expected head mismatches as unexplained warnings.
- The exact Windows notice about unavailable optional Triton FLOP accounting is
  translated to a visible informational message during import. Other warnings and
  logs remain enabled; no global warning or diagnostic suppression is used.
- PEFT's automatic vocabulary check originally attempted a hub lookup while saving.
  Checkpoint saves now use the cached base configuration, preserving the vocabulary
  comparison without network requests. Final adapter metadata uses the portable
  `roberta-base` identifier and pinned revision, not the machine-specific cache path.

## Artifacts and retention

Protected model weights, preprocessing, comparison CSVs, and the
aggregate-only privacy manifest are saved under `optimized_banking77_protected`.
That generated directory is gitignored. No training-corpus CSV or Arrow export is
requested, and persistent datasets-map caching is disabled.

Only the latest protected run's final artifacts are retained. At the user's request,
the superseded `optimized_banking77`, `roberta_lora_results`, and
`banking77_roberta_lora` directories were removed, along with intermediate learning-rate
checkpoints inside `optimized_banking77_protected`. The exported adapter is sufficient
for inference; those training checkpoints are not required to reload it.

Subsequent executions reuse the same output directory and named final artifacts,
rather than creating a separate directory per run. Each learning-rate trial uses
a system temporary directory for validation-based checkpoint selection. Trainer
loads the best weights into memory before that directory is automatically removed,
including cleanup when training raises an exception. No training checkpoints are
retained for resumption. Final artifacts overwrite the same named files; the
`roberta_lora` subdirectory is part of the single output bundle, not another run.
An interrupted rerun can leave partially updated final artifacts; it is not an
atomic replacement of the previous run. A forcibly terminated kernel or machine
cannot execute normal temporary-directory cleanup.
Existing source CSVs remain given inputs; apply institutional storage and retention
controls around them rather than modifying them.

Only load trusted joblib/PyTorch artifacts. The adapter directory includes label
configuration, tokenizer, classifier, and LoRA weights. Reloading these artifacts
alone does not apply redaction: serving must also use the versioned privacy boundary.
Deleting in-memory references does not guarantee secure RAM erasure.

## Final protected-run verification

- Fully offline clean-kernel execution: **530.1 seconds (8.83 minutes)** inside
  the notebook; **539.2 seconds** including kernel startup/shutdown.
- PII protection and synthetic checks: **24.4 seconds**.
- All nine code cells completed with **zero errors and zero warning/stderr output**;
  all eight plots rendered.
- Eight unit tests and 13 scenarios using the real pinned detector passed.
  The save-path fix also passed with warnings treated as errors.
- Source-cell diagnostics were clean. The Pylance workspace MCP endpoint separately
  reports `reportWildcardImportFromLibrary` in its generated `pylancePrefixCell`
  (`from IPython.display import *`), not notebook source. Analysis settings were
  not weakened to hide it.
- Checks verified that the invented sensitive identifiers were absent from stored
  outputs, that manifest/metric shapes were correct, and that no corpus export was
  created.
- Saved classifiers and preprocessing reloaded successfully; protected inference
  reproduced the displayed sensitive-example predictions without echoing identifiers.
- All existing comment tokens and original plots were retained.

Run the persistent privacy regression suite from this project directory:

```powershell
python -m unittest test_pii_protection -v
```

Tests cover structured identifiers, overlap/Unicode handling, entity merging,
idempotence, schema/label validation, explicit failures, benign-intent preservation,
collision policy, and word-cloud eligibility without downloading a model. The
notebook separately runs the real detector on synthetic fixtures, including PII
after the classifier's truncation length. These checks are not a real-domain
privacy-recall estimate or a regulatory certification.

## Historical runs

### Earlier unprotected baseline

This run predates the PII boundary and is retained for engineering history, not as
the final project result.

Runtime was **492.9 seconds (8.22 minutes)** inside the notebook, or 503.9 seconds
including kernel startup/shutdown. Eight code cells and six plots completed with
zero errors/stderr. Saved models and preprocessing reloaded successfully.

| Metric / resource | TF-IDF + MLP | RoBERTa + LoRA |
| --- | ---: | ---: |
| Accuracy | 87.60% | 93.47% |
| Weighted precision | 88.31% | 93.74% |
| Weighted recall | 87.60% | 93.47% |
| Weighted / macro F1 | 87.53% | 93.47% |
| Search/training/validation/selection | 4.74 s | 454.43 s |
| Test prediction, including batching | 0.12 s | 2.45 s |
| Peak allocated GPU memory, training phase | 0.62 GiB | 1.44 GiB |
| Total parameters | 6,295,629 | 125,944,474 |
| Trainable parameters | 6,295,629 | 1,239,629 |

Validation selected RoBERTa learning rate 0.0005: macro F1 0.93137 versus 0.92909
at 0.0003. Test accuracy improved by 5.88 percentage points, with a paired bootstrap
95% interval of [4.77, 6.98] points. Neither model left an intent unpredicted.

### Initial protected run and saving warning

An initial protected run finished in 510.0 seconds (8.50 minutes), with about
23.2 seconds for privacy protection/checks. It produced the same protected accuracy
scores as the final run: MLP 87.86%, RoBERTa 93.21%. Verification found two PEFT
warnings caused by a failed remote base-config lookup while saving; these prevented
claiming a warning-free result. The cached-config save correction was verified
before the final offline rerun.

Historical unprotected and protected results are not a controlled causal estimate
of redaction's utility cost: the protected workflow also removes collision rows.
Neither the small single-seed search nor its test bootstrap interval measures
training-seed or hyperparameter-selection uncertainty.
