## Featured Projects

# **Banking Intent Classification**

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![Hugging Face Transformers](https://img.shields.io/badge/Hugging_Face-Transformers-FFD21E?style=for-the-badge)
![PEFT LoRA](https://img.shields.io/badge/PEFT-LoRA-6C3483?style=for-the-badge)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![CUDA](https://img.shields.io/badge/NVIDIA-CUDA-76B900?style=for-the-badge&logo=nvidia&logoColor=white)
![Matplotlib and Seaborn](https://img.shields.io/badge/Visualization-Matplotlib_%7C_Seaborn_%7C_WordCloud-2874A6?style=for-the-badge)

## Business Understanding following CRISP-DM framework

### Project Overview

Financial institutions receive thousands of customer inquiries every day through chatbots, mobile apps, email, and support portals. Efficiently routing these inquiries to the correct department or automated workflow is critical for maintaining customer satisfaction and reducing operational costs.

This project focuses on building an AI-powered banking intent classification system using the Banking77 dataset. The system automatically categorizes customer banking queries into one of 77 predefined intent classes. Examples include card delivery issues, cash withdrawal questions, balance inquiries, transfer problems, and account verification requests.

By accurately identifying customer intent, banks can automate customer support workflows, reduce response times, improve service quality, and help customers resolve issues more quickly.

---

### Business Problem

Manual classification of customer support requests is time-consuming, expensive, and difficult to scale. Incorrect routing can result in:

- Increased customer wait times
- Higher operational costs
- Reduced customer satisfaction
- Lower support team efficiency
- Increased workload for customer service agents

The goal is to develop a machine learning solution capable of understanding customer requests and automatically assigning the correct banking intent category.

---

### Business Objectives

The primary business objectives are:

1. Automate the classification of customer banking inquiries.
2. Reduce the need for manual ticket routing.
3. Improve response times for customer support requests.
4. Increase routing accuracy across banking service categories.
5. Establish a scalable NLP solution suitable for deployment in production environments.

---

### Machine Learning Objectives

To achieve the business goals, this project will:

- Explore and analyze customer query text data.
- Develop a traditional text classification baseline using a Multi-Layer Perceptron (MLP).
- Fine-tune a transformer-based RoBERTa model using Low-Rank Adaptation (LoRA).
- Compare model performance, computational cost, and training efficiency.
- Evaluate performance across all 77 intent classes.
- Demonstrate production-oriented handling of sensitive customer information.

---

### Success Criteria

The project will be considered successful if:

- The model accurately predicts customer intent categories.
- The comparison measures whether the transformer improves over the baseline, without assuming which model wins.
- The system generalizes well to previously unseen customer queries.
- The local PII-protection layer runs before previews, training and inference; production deployment additionally requires domain validation and operational controls described below.
- Model evaluation provides actionable insights into strengths and weaknesses across intent categories.

Key evaluation metrics include:

- Accuracy
- Precision
- Recall
- F1 Score
- Per-Class Performance Analysis
- Confusion Matrix Analysis

---

### Stakeholders

The primary stakeholders include:

| Stakeholder | Interest |
|------------|----------|
| Customers | Faster issue resolution and improved support experience |
| Customer Support Teams | Reduced manual routing workload |
| Operations Management | Lower support costs and increased efficiency |
| AI/ML Engineers | Development of scalable NLP systems |
| Compliance & Security Teams | Protection of sensitive customer information |

---

### Project Constraints

Several practical constraints must be considered:

- Customer queries contain sensitive financial information.
- The dataset contains 77 intent classes, creating a multi-class classification challenge.
- Class distributions may be imbalanced.
- Models should balance prediction accuracy with computational efficiency.
- The solution should be suitable for deployment in regulated financial environments.

---

### Expected Business Impact

A successful intent classification system can:

- Reduce support ticket triage time.
- Increase automation rates in customer service workflows.
- Improve customer satisfaction through faster responses.
- Decrease operational costs associated with manual processing.
- Provide a foundation for intelligent banking chatbots and virtual assistants.

Ultimately, this project demonstrates how modern NLP techniques such as transformer fine-tuning with LoRA can be applied to solve real-world business problems in the financial services industry while maintaining security and scalability requirements.

## Modeling and Evaluation Approach

The [project notebook](./banking_classification_BERT.ipynb) compares a lexical
TF-IDF + MLP model with contextual RoBERTa-base + LoRA on the same protected data.
Its learning objective is to connect parameter selection and model choice to
validation quality, compute cost, privacy risk, and responsible data management.

### Data understanding and preparation

Banking77 supplies 10,003 training queries and 3,080 test queries across 77 intents.
**The supplied CSV files remain unchanged.** Protection, collision handling, and
splitting operate on in-memory text and DataFrames, not on the given input files.

Exploratory visualizations examine intent counts, word-count distributions and
average query length. A protected-training-text word cloud highlights vocabulary,
and an aggregate recognizer-count chart describes privacy detections without
showing identities. Word-cloud terms must occur in at least five training documents;
placeholder labels are excluded. This reduces rare-token exposure but is not an
anonymity guarantee or a substitute for output review.

After privacy protection, training queries matching protected test inputs are
excluded from training. Ambiguous protected training groups and duplicate protected
queries are removed before a seeded, stratified 85/15 training/validation split.
The official test rows remain intact. These text-only rules prevent redaction-created
leakage without using test labels to select settings.

### Models and parameter selection

| Component | Approach | Selection rationale |
| --- | --- | --- |
| TF-IDF | Word unigrams/bigrams, 12,000-feature cap, sublinear term frequency, float32, no stop-word deletion | Capture banking phrases and negation while bounding dense MLP memory |
| MLP | 512/256 hidden units; learning-rate/dropout pairs (0.001, 0.2) and (0.002, 0.3); batches of 256 | Compare two learning/generalization tradeoffs with inexpensive GPU training |
| MLP stopping | Up to 24 epochs, patience 4; restore the best validation checkpoint | Avoid continued training after sustained validation non-improvement |
| RoBERTa + LoRA | RoBERTa-base; rank 16, alpha 32, query/value adapters, dropout 0.05 | Preserve contextual knowledge while updating less than 1% of total parameters |
| LoRA search | Learning rates 0.0003 and 0.0005; up to 10 epochs, patience 2; 80 warmup steps, weight decay 0.01 | Use adapter-appropriate rates and validation curves to balance convergence and cost |
| Transformer efficiency | FP16; train/evaluation batches 32/64; 64-token limit; dynamic padding to multiples of 8 | Target 8-GiB GPU memory and approximately ten-minute end-to-end runtime; inspect protected training token-length coverage |

TF-IDF is fitted only on the training partition. Both classifiers use a shared label
encoder and identical splits. Validation macro F1 selects settings and checkpoints;
test labels do not select models, privacy policy, or preprocessing parameters.
Feature cap, architecture, LoRA rank, and adapter targets are engineering priors,
not globally optimized choices. The notebook explains which settings were searched
and which would require further validation experiments.

### Evaluation and inference

The selected models are evaluated on the same test queries using accuracy, weighted
precision/recall/F1, macro F1, and per-intent comparisons. A paired bootstrap interval
describes uncertainty in their test accuracy difference. It does not capture
training-seed or hyperparameter-selection uncertainty.

Resource comparisons include training/search time, prediction time, total/trainable
parameters, and peak allocated GPU memory. LoRA reduces trainable weights, not the
underlying encoder's total size or inference cost.

Realistic synthetic banking questions demonstrate both models' predictions,
agreement, and uncalibrated softmax scores. Sensitive examples pass through the
same privacy boundary as training inputs, and only protected queries are displayed.
Softmax scores are not calibrated probabilities of correctness. This closed-set
demonstration does not detect out-of-domain requests or authorize banking actions.

## PII Protection and Responsible Data Management

The [local privacy boundary](./pii_protection.py) combines a pinned, Apache-2.0
[DistilBERT NER model](https://huggingface.co/dslim/distilbert-NER) with structured
recognizers. Detection runs locally on English text; customer queries are not sent
to a remote redaction API. Its scope includes US/UK identifiers and supported
international IBAN formats.

### Protection workflow

1. **Validate and normalize.** Check the exact CSV schema and public intent-label
   catalog. Apply Unicode NFKC normalization and remove common zero-width controls
   that could conceal identifiers.
2. **Detect complementary entity types.** The pretrained model detects people and
   locations. Rules cover standard street addresses, emails/URLs, phone patterns,
   card candidates, contextual account/routing/passport/licence-like values,
   known-country-length IBANs, US SSNs, UK NINOs/sort codes/postcodes, contextual
   US ZIP codes, dates of birth, credentials, and currency-prefixed amounts.
   Potential identifiers are protected even when their checksums are invalid.
3. **Scan the complete query.** Privacy detection uses 256-token windows with a
   32-token overlap and batches of 64. Unlike classifier truncation, it scans all
   windows so tail identifiers are not skipped. Queries exceeding 10,000 characters
   are rejected explicitly rather than silently truncated.
4. **Redact irreversibly.** Merge overlapping spans and replace them right-to-left
   with typed placeholders such as `<PERSON>`, `<CARD>`, and `<AMOUNT>`.
   Placeholders preserve useful intent cues without retaining an identity mapping.
   Only protected text and category-level counters leave the boundary; raw matches,
   offsets, per-person hashes, and reversible mappings are not exported.
5. **Protect every downstream surface.** Previews, plots, TF-IDF, tokenization,
   model training, and inference receive protected text. Persistent datasets-map
   caching is disabled, and no training-corpus CSV/Arrow export is requested.
   Source CSVs themselves are not modified or deleted.
6. **Fail closed and record safe evidence.** Missing detector assets, invalid spans,
   malformed data, and detector failures stop processing rather than triggering an
   unprotected fallback. Synthetic removal, benign-intent-preservation, idempotence,
   and long-tail checks precede previews. The audit manifest records aggregate counts,
   policy/model revisions, package versions, timing, and split/collision counts,
   not customer identities.

The NER model's smaller size supports the runtime/memory budget, but its news-domain
training does not establish banking-specific privacy recall. All predicted person
and location tokens are considered without an additional confidence cutoff to favor
recall; organizations are not blanket-masked because bank/product names can carry
intent. Entity-specific thresholds and coverage require independent privacy validation,
not selection based on classifier accuracy.

### Limits and production requirements

**Redaction is not guaranteed anonymization or regulatory certification.** Detection
can miss ambiguous names, unusual addresses, unsupported languages/country IDs,
obfuscation, and financial facts outside the covered patterns. Over-redaction can
also remove useful intent cues. Residual context or trained weights may remain
sensitive, and Python cannot guarantee secure erasure of immutable strings in RAM.

Before processing live customer data, a regulated deployment additionally needs:

- Approved purpose/lawful basis, data inventory and classification, and institutional
  privacy-risk/DPIA and compliance review.
- Least-privilege access, MFA, scoped service identities, managed secrets, and audited
  access; no retention of PINs, CVVs, OTPs, or passwords for this classification task.
- KMS-managed encryption at rest, encrypted transport, restricted egress, key rotation,
  and reviewed model/package supply chains.
- Enforced retention/deletion schedules for sources, caches, outputs, logs,
  checkpoints, weights, backups, swap, and crash dumps.
- An authorized annotated banking-domain privacy holdout, entity-specific
  precision/recall and false-negative analysis by subgroup/format/language,
  adversarial tests, and independently approved release thresholds.
- Residual-PII and memorization review, aggregate-only monitoring, incident response,
  human escalation, and the same versioned privacy boundary in serving.

Synthetic checks are regression safeguards, not estimates of real-world detection
recall. A notebook alone does not satisfy GDPR/UK GDPR, GLBA, or PCI DSS obligations.

## Conclusion: Protected-Data Results

On an NVIDIA RTX 2070 Super with 8 GiB VRAM, the complete protected workflow took
**530.1 seconds (8.83 minutes)**, including **24.4 seconds** for PII protection and
its checks, within the approximately ten-minute target. Initial dependency/model
downloads are outside that budget.

| Test metric / resource | TF-IDF + MLP | RoBERTa + LoRA |
| --- | ---: | ---: |
| Accuracy | 87.86% | **93.21%** |
| Weighted precision | 88.54% | **93.43%** |
| Weighted recall | 87.86% | **93.21%** |
| Weighted / macro F1 | 87.85% | **93.20%** |
| Search/training/validation/selection time | **4.06 s** | 479.06 s |
| Test prediction time, including batching | **0.11 s** | 2.73 s |
| Peak allocated GPU memory during training phase | **0.61 GiB** | 1.44 GiB |
| Total parameters | 6,295,629 | 125,944,474 |
| Trainable parameters | 6,295,629 | **1,239,629** |

Peak memory is process-wide during the named phase, including resident tensors and
models, not an isolated per-model hardware requirement. Macro and weighted F1
coincide because the test set contains 40 examples per intent.

Validation selected MLP learning rate/dropout **(0.002, 0.3)** and RoBERTa learning
rate **0.0005**. RoBERTa's accuracy advantage was **5.36 percentage points**, with a
paired bootstrap 95% interval of **[4.25, 6.43] points**. Its contextual accuracy gain
comes with substantially higher training and prediction cost; MLP remains a useful
choice when latency and compute dominate.

The privacy policy redacted detected spans in **418 training-source queries** and
**114 test-source queries**. These are recognizer counts, not ground-truth PII
prevalence or recall. In-memory decontamination excluded seven protected
training/test matches and six training duplicates, leaving **8,491 training** and
**1,499 validation** queries while retaining all **3,080 test** queries. The given
CSV files remain unchanged.

All nine code cells completed without errors or warning/stderr output, and all eight
visualizations rendered. Eight privacy unit tests and 13 real-detector synthetic
scenarios passed. Protected inference and saved-model reload checks reproduced the
displayed predictions without exposing the synthetic identifiers.

The results demonstrate a practical accuracy/resource/privacy tradeoff for an AI
engineer in training, not global optimization or readiness to process live financial
records. Larger multi-seed studies, real-domain privacy validation, and institutional
deployment controls remain necessary.

For installation, execution instructions, maintenance changes, historical runs, and
detailed verification evidence, see [Execution and Maintenance Notes](./EXECUTION_NOTES.md).
