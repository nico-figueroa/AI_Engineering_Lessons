"""Local, irreversible PII redaction for the Banking77 teaching workflow.

Detection is best-effort, not an anonymity or compliance guarantee. No raw text,
matched values, offsets, or re-identification maps are returned or persisted.
"""

from __future__ import annotations

import csv
import logging
import re
import unicodedata
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import pandas as pd

NER_MODEL = "dslim/distilbert-NER"
# Pin reviewed Apache-2.0 weights so subsequent runs do not silently change policy.
NER_REVISION = "dfa2838a127384aabb82ed7719e16dab84c42a2a"
POLICY_VERSION = "banking77-en-us-uk-v1"
# Bound memory/latency per request. Oversized input is rejected, never truncated.
MAX_QUERY_CHARACTERS = 10_000
# Labels are public taxonomy, not free-form customer metadata suitable for logging.
BANKING77_INTENTS = frozenset("""
Refund_not_showing_up activate_my_card age_limit apple_pay_or_google_pay atm_support
automatic_top_up balance_not_updated_after_bank_transfer
balance_not_updated_after_cheque_or_cash_deposit beneficiary_not_allowed cancel_transfer
card_about_to_expire card_acceptance card_arrival card_delivery_estimate card_linking
card_not_working card_payment_fee_charged card_payment_not_recognised
card_payment_wrong_exchange_rate card_swallowed cash_withdrawal_charge
cash_withdrawal_not_recognised change_pin compromised_card contactless_not_working
country_support declined_card_payment declined_cash_withdrawal declined_transfer
direct_debit_payment_not_recognised disposable_card_limits edit_personal_details
exchange_charge exchange_rate exchange_via_app extra_charge_on_statement failed_transfer
fiat_currency_support get_disposable_virtual_card get_physical_card getting_spare_card
getting_virtual_card lost_or_stolen_card lost_or_stolen_phone order_physical_card
passcode_forgotten pending_card_payment pending_cash_withdrawal pending_top_up
pending_transfer pin_blocked receiving_money request_refund reverted_card_payment?
supported_cards_and_currencies terminate_account top_up_by_bank_transfer_charge
top_up_by_card_charge top_up_by_cash_or_cheque top_up_failed top_up_limits top_up_reverted
topping_up_by_card transaction_charged_twice transfer_fee_charged transfer_into_account
transfer_not_received_by_recipient transfer_timing unable_to_verify_identity
verify_my_identity verify_source_of_funds verify_top_up virtual_card_not_working
visa_or_mastercard why_verify_identity wrong_amount_of_cash_received
wrong_exchange_rate_for_cash_withdrawal
""".split())


@dataclass(frozen=True)
class PiiSpan:
    start: int
    end: int
    kind: str

# ----------------------------------------
# PII Detection Protocol
# ----------------------------------------
class EntityDetector(Protocol):
    def detect(self, texts: list[str]) -> list[list[PiiSpan]]: ...

# Triton Optional Notice Filter
class _OptionalTritonNotice(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage() != "triton not found; flop counting will not work for triton kernels"

# Local Name Detector
class LocalNameDetector:
    """Pinned English PER/LOC recognition; no remote inference or custom code."""

    def __init__(self, device: str = "cuda:0", batch_size: int = 64) -> None:
        if batch_size < 1:
            raise ValueError("PII batch size must be positive.")
        # The exact optional Windows capability notice is not a detection failure.
        logger = logging.getLogger("torch.utils.flop_counter")
        notice = _OptionalTritonNotice()
        logger.addFilter(notice)
        try:
            import torch
            from transformers import AutoModelForTokenClassification, AutoTokenizer
            from transformers.utils import logging as transformer_logging
        finally:
            logger.removeFilter(notice)
        self._torch = torch
        self._device = device
        self._batch_size = batch_size  # Short queries batch efficiently within 8 GiB VRAM.
        self._tokenizer = AutoTokenizer.from_pretrained(
            NER_MODEL, revision=NER_REVISION, use_fast=True, trust_remote_code=False,
            local_files_only=True,
        )
        if not self._tokenizer.is_fast:
            raise RuntimeError("PII detection requires a tokenizer with character offsets.")
        # Disable only the cached-weight progress widget, never warning/error logging.
        # This keeps stored outputs stable and avoids a stderr progress stream.
        progress_enabled = transformer_logging.is_progress_bar_enabled()
        transformer_logging.disable_progress_bar()
        try:
            self._model = AutoModelForTokenClassification.from_pretrained(
                NER_MODEL, revision=NER_REVISION, use_safetensors=True, trust_remote_code=False,
                local_files_only=True,
            ).eval()
        finally:
            if progress_enabled:
                transformer_logging.enable_progress_bar()
        self._labels = self._model.config.id2label

    def detect(self, texts: list[str]) -> list[list[PiiSpan]]:
        if not texts:
            return []
        torch = self._torch
        results: list[list[PiiSpan]] = [[] for _ in texts]
        self._model.to(self._device)
        try:
            for first in range(0, len(texts), self._batch_size):
                batch = texts[first:first + self._batch_size]
                # Unlike classifier truncation, privacy scanning must cover the entire
                # query. 256-token windows with 32-token overlap protect boundary names.
                encoded = self._tokenizer(
                    batch, padding=True, truncation=True, max_length=256, stride=32,
                    return_overflowing_tokens=True, return_offsets_mapping=True,
                    return_tensors="pt",
                )
                offsets = encoded.pop("offset_mapping").tolist()
                owners = encoded.pop("overflow_to_sample_mapping").tolist()
                # Windowing covers the complete query, including PII after token 256.
                for window in range(0, len(owners), self._batch_size):
                    inputs = {
                        name: value[window:window + self._batch_size].to(self._device)
                        for name, value in encoded.items()
                    }
                    with torch.inference_mode():
                        predicted = self._model(**inputs).logits.argmax(dim=-1).cpu().tolist()
                    for row, labels in enumerate(predicted, start=window):
                        spans = results[first + owners[row]]
                        for (start, end), label in zip(offsets[row], labels):
                            kind = self._labels[label].removeprefix("B-").removeprefix("I-")
                            # ORG/MISC are not blanket-masked: bank/product names help
                            # intent classification. PER and LOC reduce direct identifiers.
                            if end > start and kind in {"PER", "LOC"}:
                                spans.append(PiiSpan(start, end, "PERSON" if kind == "PER" else "LOCATION"))
        finally:
            # Release GPU residency before the two intent-model training searches.
            self._model.to("cpu")
        return results

# PII Detection Rules
_RULES: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (kind, re.compile(pattern, re.IGNORECASE))
    for kind, pattern in (
        ("EMAIL", r"(?<![\w.+-])[\w.+-]+@[\w-]+(?:\.[\w-]+)+"),
        ("URL", r"\b(?:https?://|www\.)[^\s<>]+"),
        ("US_SSN", r"\b\d{3}[- ]\d{2}[- ]\d{4}\b"),
        ("UK_NINO", r"\b[A-Z]{2}[ -]?\d{2}[ -]?\d{2}[ -]?\d{2}[ -]?[A-D]\b"),
        ("UK_POSTCODE", r"\b(?:GIR\s?0AA|[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2})\b"),
        ("US_ZIP", r"\b(?:zip(?:\s+code)?)[ :=]+(?P<value>\d{5}(?:-\d{4})?)\b"),
        ("SORT_CODE", r"\b\d{2}[- ]\d{2}[- ]\d{2}\b"),
        ("PHONE", r"(?<!\w)(?:\+?1[ .-]?)?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}\b"),
        ("PHONE", r"(?<!\w)(?:\+44[ .-]?(?:\(0\)[ .-]?)?|0)\d{2,4}[ .-]?\d{3,4}[ .-]?\d{3,4}\b"),
        # Do not require a valid checksum: mistyped customer identifiers still need protection.
        ("CARD", r"(?<!\w)(?:\d[ -]?){12,18}\d(?!\w)"),
        ("FINANCIAL_ID", r"(?<!\w)\d(?:[ -]?\d){6,11}(?!\w)"),
        ("ADDRESS", r"\b\d{1,6}\s+(?:[A-Z0-9.'-]+\s+){1,6}(?:street|st|road|rd|avenue|ave|lane|ln|drive|dr|boulevard|blvd|way|court|ct|place|pl|terrace|close)\b(?:[,.]?\s+(?:apt|apartment|flat|suite|unit)\s*[\w-]+)?"),
        ("DATE_OF_BIRTH", r"\b(?:date\s+of\s+birth|dob|born\s+on)\s*(?:is\s*)?[:=]?\s*(?P<value>\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4})\b"),
        ("CREDENTIAL", r"\b(?:pin|cvv|cvc|otp|passcode|password|security\s+code)\s*(?:is\s*)?[:=#]?\s*(?P<value>(?=[^\s,;.!?]{0,63}\d)[^\s,;.!?]{3,64})"),
        ("CREDENTIAL", r"\bpassword(?:\s+is\s+|\s*[:=]\s*)(?P<value>[^\s,;.!?]{3,64})"),
        ("ACCOUNT", r"\b(?:account|acct|passport|routing|licen[cs]e|customer|tax|national\s+id)\s*(?:number|no\.?|id|#)?\s*(?:is\s*)?[:=#]?\s*(?P<value>(?=[A-Z0-9-]*\d)[A-Z0-9][A-Z0-9-]{3,33})\b"),
        # Balances/amounts are sensitive financial facts even without a direct identifier.
        ("AMOUNT", r"[$£€]\s*\d[\d,]*(?:\.\d{1,2})?"),
    )
)
_KINDS = frozenset(kind for kind, _ in _RULES) | {"PERSON", "LOCATION", "IBAN"}
_IBAN_LENGTHS = {
    "AD": 24, "AE": 23, "AL": 28, "AT": 20, "AZ": 28, "BA": 20, "BE": 16,
    "BG": 22, "BH": 22, "BR": 29, "BY": 28, "CH": 21, "CR": 22, "CY": 28,
    "CZ": 24, "DE": 22, "DK": 18, "DO": 28, "EE": 20, "EG": 29, "ES": 24,
    "FI": 18, "FO": 18, "FR": 27, "GB": 22, "GE": 22, "GI": 23, "GL": 18,
    "GR": 27, "GT": 28, "HR": 21, "HU": 28, "IE": 22, "IL": 23, "IQ": 23,
    "IS": 26, "IT": 27, "JO": 30, "KW": 30, "KZ": 20, "LB": 28, "LC": 32,
    "LI": 21, "LT": 20, "LU": 20, "LV": 21, "MC": 27, "MD": 24, "ME": 22,
    "MK": 19, "MR": 27, "MT": 31, "MU": 30, "NL": 18, "NO": 15, "PK": 24,
    "PL": 28, "PS": 29, "PT": 25, "QA": 29, "RO": 24, "RS": 22, "SA": 24,
    "SC": 31, "SE": 24, "SI": 19, "SK": 24, "SM": 27, "ST": 25, "SV": 28,
    "TL": 23, "TN": 24, "TR": 26, "UA": 29, "VA": 22, "VG": 24, "XK": 20,
}
_PLACEHOLDER = re.compile(r"<(?:" + "|".join(sorted(_KINDS)) + r")>")
_PRIORITY = {kind: index for index, kind in enumerate(
    ("URL", "EMAIL", "IBAN", "ADDRESS", "US_SSN", "UK_NINO", "UK_POSTCODE",
     "US_ZIP", "SORT_CODE", "PHONE", "CARD", "CREDENTIAL", "ACCOUNT", "DATE_OF_BIRTH",
     "AMOUNT", "FINANCIAL_ID", "PERSON", "LOCATION")
)}

# ----------------------------------------
# Normalization and Span Detection
# ----------------------------------------
def _normalize(text: str) -> str:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("PII protection requires non-empty text.")
    if len(text) > MAX_QUERY_CHARACTERS:
        raise ValueError("Query exceeds the privacy policy length limit; do not truncate or bypass detection.")
    # Remove format/zero-width controls that can hide identifiers from recognizers.
    normalized = "".join(
        char for char in unicodedata.normalize("NFKC", text)
        if unicodedata.category(char) != "Cf"
    )
    if not normalized.strip():
        raise ValueError("Query contains no usable text.")
    return normalized

# IBAN Span Detection
def _iban_spans(text: str) -> list[PiiSpan]:
    # Country-specific lengths avoid greedily consuming intent words after spaced IBANs.
    spans: list[PiiSpan] = []
    for match in re.finditer(r"\b([A-Z]{2})\s?\d{2}", text, re.IGNORECASE):
        length = _IBAN_LENGTHS.get(match.group(1).upper())
        if length is None:
            continue
        count = 0
        end = match.start()
        while end < len(text) and count < length:
            character = text[end]
            if character.isascii() and character.isalnum():
                count += 1
            elif character not in " -":
                break
            end += 1
        if count == length:
            spans.append(PiiSpan(match.start(), end, "IBAN"))
    return spans

# Merge Overlapping Spans
def _merge(spans: Sequence[PiiSpan], text: str) -> list[PiiSpan]:
    # Union overlapping spans instead of allowing one recognizer to expose part of
    # another's match. Only the replacement category uses deterministic priority.
    protected = [(match.start(), match.end()) for match in _PLACEHOLDER.finditer(text)]
    ordered = sorted(set(spans), key=lambda span: (span.start, span.end))
    merged: list[PiiSpan] = []
    for span in ordered:
        if span.kind not in _KINDS or not 0 <= span.start < span.end <= len(text):
            raise ValueError("PII detector returned an invalid span; refusing unprotected output.")
        if any(start <= span.start and span.end <= end for start, end in protected):
            continue
        if merged and (
            span.start < merged[-1].end
            or (span.kind == merged[-1].kind and (
                span.start == merged[-1].end or text[merged[-1].end:span.start].isspace()
            ))
        ):
            previous = merged.pop()
            kind = min((previous.kind, span.kind), key=lambda value: _PRIORITY[value])
            merged.append(PiiSpan(previous.start, max(previous.end, span.end), kind))
        else:
            merged.append(span)
    return merged


@dataclass(frozen=True)
class ProtectedBatch:
    texts: list[str]
    counts: dict[str, int]
    changed_rows: int


class PiiProtector:
    def __init__(self, detector: EntityDetector) -> None:
        self._detector = detector

    def protect(self, texts: list[str]) -> ProtectedBatch:
        normalized = [_normalize(text) for text in texts]
        # Detector failure propagates: no regex-only fallback silently weakens protection.
        learned_spans = self._detector.detect(normalized)
        if len(learned_spans) != len(normalized):
            raise RuntimeError("PII detector returned an incomplete batch; refusing unprotected output.")
        output: list[str] = []
        counts: Counter[str] = Counter()
        changed_rows = 0
        for text, spans in zip(normalized, learned_spans):
            spans = list(spans) + _iban_spans(text)
            for kind, pattern in _RULES:
                for match in pattern.finditer(text):
                    start, end = match.span("value") if "value" in match.groupdict() else match.span()
                    spans.append(PiiSpan(start, end, kind))
            merged = _merge(spans, text)
            changed_rows += bool(merged)
            # Work right-to-left so replacing one span does not invalidate earlier offsets.
            # Counters contain categories only; never retain matched values or raw snippets.
            for span in reversed(merged):
                text = text[:span.start] + f"<{span.kind}>" + text[span.end:]
                counts[span.kind] += 1
            output.append(text)
        return ProtectedBatch(output, dict(counts), changed_rows)


def read_protected_banking_csv(path: Path, protector: PiiProtector) -> tuple[pd.DataFrame, dict[str, int]]:
    """Raw rows stay local to this function; only protected text leaves it."""
    texts: list[str] = []
    labels: list[str] = []
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, strict=True)
            if reader.fieldnames != ["text", "category"]:
                raise ValueError("Expected exactly the Banking77 text/category schema.")
            for row in reader:
                if set(row) != {"text", "category"} or row["category"] not in BANKING77_INTENTS:
                    raise ValueError("Unexpected columns or intent labels; refusing raw previews.")
                texts.append(row["text"])
                labels.append(row["category"])
    except (csv.Error, UnicodeError):
        raise ValueError("Source CSV is malformed; raw row contents are not logged.") from None
    if not texts:
        raise ValueError("Source CSV contains no queries.")
    protected = protector.protect(texts)
    return pd.DataFrame({"text": protected.texts, "category": labels}), {
        **protected.counts, "changed_rows": protected.changed_rows, "rows": len(texts)
    }


def decontaminate_training(train: pd.DataFrame, test: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """Remove protected-text collisions without changing the official test set."""
    train = train.copy()
    train["_key"] = train["text"].str.casefold().str.split().str.join(" ")
    test_keys = set(test["text"].str.casefold().str.split().str.join(" "))
    overlaps = train["_key"].isin(test_keys)
    remaining = train.loc[~overlaps].copy()
    # Redaction can collapse different original queries to the same protected query.
    # Remove ambiguous groups and duplicates before splitting, not after fitting TF-IDF.
    conflicts = remaining.groupby("_key")["category"].transform("nunique").gt(1)
    unambiguous = remaining.loc[~conflicts]
    distinct = unambiguous.drop_duplicates("_key")
    return distinct.drop(columns="_key").reset_index(drop=True), {
        "train_rows_matching_protected_test": int(overlaps.sum()),
        "ambiguous_protected_train_rows": int(conflicts.sum()),
        "duplicate_protected_train_rows": len(unambiguous) - len(distinct),
    }


def wordcloud_frequencies(texts: Sequence[str], minimum_documents: int = 5) -> dict[str, int]:
    """Document-frequency gate reduces singleton exposure; not differential privacy."""
    if minimum_documents < 2:
        raise ValueError("Word-cloud terms must occur in at least two protected documents.")
    # Five documents is a teaching safeguard against rare tokens, not a formal
    # anonymity guarantee. Word clouds must still undergo an authorized output review.
    counts: Counter[str] = Counter()
    for text in texts:
        counts.update(set(re.findall(r"\b[a-z]{3,}\b", _PLACEHOLDER.sub(" ", text).lower())))
    return {term: count for term, count in counts.items() if count >= minimum_documents}


def synthetic_privacy_checks(protector: PiiProtector) -> pd.DataFrame:
    """Release gate using invented fixtures, never real customer identities."""
    fixtures = [
        ("PERSON", "My name is Jane Doe and I need a replacement card.", ("Jane", "Doe")),
        ("ADDRESS", "Send the card to 42 Maple Street, London SW1A 1AA.",
         ("42 Maple Street", "London", "SW1A 1AA")),
        ("EMAIL", "Email jane@example.com about the missing card.", ("jane@example.com",)),
        ("PHONE", "Call +1 (202) 555-0123 or +44 7700 900123.", ("202", "555-0123", "7700")),
        ("CARD", "My card 4111 1111 1111 1111 was declined.", ("4111",)),
        ("IBAN", "My transfer to GB82 WEST 1234 5698 7654 32 is pending.", ("GB82", "WEST")),
        ("US_SSN", "My SSN is 123-45-6789.", ("123-45-6789",)),
        ("UK_NINO", "NI number QQ123456C needs updating.", ("QQ123456C",)),
        ("ACCOUNT", "Account AB123456 has a balance of £1,234.56.", ("AB123456", "1,234.56")),
        ("CREDENTIAL", "My PIN is 1234 and DOB is 1990-01-02.", ("1234", "1990-01-02")),
        ("LONG_QUERY", ("I need help with a card payment. " * 150) + "My name is John Smith.",
         ("John", "Smith")),
        ("UNICODE", "My card is ４１１１\u200b１１１１１１１１１１１１.", ("4111",)),
    ]
    result = protector.protect([text for _, text, _ in fixtures])
    rows: list[dict[str, object]] = []
    for (kind, _, secrets), text in zip(fixtures, result.texts):
        # Check removal of every fixture identifier, not just that a tag appeared.
        passed = all(secret.casefold() not in text.casefold() for secret in secrets)
        rows.append({"Synthetic scenario": kind, "All expected identifiers removed": passed})
    benign = ["How do I change my pin?", "My card has not arrived in 10 days."]
    benign_result = protector.protect(benign)
    rows.append({
        "Synthetic scenario": "BENIGN_INTENT_PRESERVED", "All expected identifiers removed": benign_result.texts == benign
    })
    if not all(bool(row["All expected identifiers removed"]) for row in rows):
        raise RuntimeError("Synthetic PII checks failed; do not preview data or train models.")
    if protector.protect(result.texts).texts != result.texts:
        raise RuntimeError("PII redaction is not stable on the synthetic release fixtures.")
    return pd.DataFrame(rows)
