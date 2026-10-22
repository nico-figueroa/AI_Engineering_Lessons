import tempfile
import unittest
from pathlib import Path

import pandas as pd

from pii_protection import (
    BANKING77_INTENTS, MAX_QUERY_CHARACTERS, PiiProtector, PiiSpan,
    decontaminate_training, read_protected_banking_csv, wordcloud_frequencies,
)


class NoEntities:
    def detect(self, texts: list[str]) -> list[list[PiiSpan]]:
        return [[] for _ in texts]


class KnownSyntheticEntities:
    def detect(self, texts: list[str]) -> list[list[PiiSpan]]:
        return [
            [PiiSpan(text.index(value), text.index(value) + len(value), kind)
             for value, kind in [("Jane", "PERSON"), ("Doe", "PERSON"), ("London", "LOCATION")]
             if value in text]
            for text in texts
        ]


class PiiProtectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.protector = PiiProtector(NoEntities())

    def test_structured_coverage(self) -> None:
        examples = [
            ("Email jane@example.com about my card", "jane@example.com", "<EMAIL>"),
            ("Call +1 (202) 555-0123", "+1 (202) 555-0123", "<PHONE>"),
            ("Call +44 7700 900123", "+44 7700 900123", "<PHONE>"),
            ("Card 4111 1111 1111 1111 was declined", "4111 1111 1111 1111", "<CARD>"),
            ("Card 4111111111111112 was declined", "4111111111111112", "<CARD>"),
            ("SSN 123-45-6789", "123-45-6789", "<US_SSN>"),
            ("NI number QQ123456C", "QQ123456C", "<UK_NINO>"),
            ("Sort code 12-34-56", "12-34-56", "<SORT_CODE>"),
            ("Account AB123456 is blocked", "AB123456", "<ACCOUNT>"),
            ("Passport 123456789", "123456789", "<ACCOUNT>"),
            ("PIN is 1234", "1234", "<CREDENTIAL>"),
            ("password: syntheticsecret", "syntheticsecret", "<CREDENTIAL>"),
            ("DOB: 1990-01-02", "1990-01-02", "<DATE_OF_BIRTH>"),
            ("Send to 42 Maple Street, flat 3", "42 Maple Street, flat 3", "<ADDRESS>"),
            ("My postcode is SW1A 1AA", "SW1A 1AA", "<UK_POSTCODE>"),
            ("My balance is £1,234.56", "£1,234.56", "<AMOUNT>"),
            ("Visit https://bank.example/reset?token=secret", "https://bank.example/reset?token=secret", "<URL>"),
            ("IBAN GB82 WEST 1234 5698 7654 32 transfer", "GB82 WEST 1234 5698 7654 32", "<IBAN>"),
            ("IBAN DE89370400440532013000 transfer", "DE89370400440532013000", "<IBAN>"),
        ]
        for text, secret, tag in examples:
            with self.subTest(tag=tag):
                result = self.protector.protect([text])
                self.assertNotIn(secret, result.texts[0])
                self.assertIn(tag, result.texts[0])
                self.assertGreater(result.changed_rows, 0)
        self.assertTrue(self.protector.protect([examples[-1][0]]).texts[0].endswith(" transfer"))

    def test_named_entities_and_idempotence(self) -> None:
        protector = PiiProtector(KnownSyntheticEntities())
        first = protector.protect(["I am Jane Doe in London; email jane@example.com."])
        self.assertEqual(first.texts, ["I am <PERSON> in <LOCATION>; email <EMAIL>."])
        self.assertEqual(protector.protect(first.texts).texts, first.texts)
        self.assertEqual(first.counts, {"EMAIL": 1, "LOCATION": 1, "PERSON": 1})

    def test_unicode_and_overlap(self) -> None:
        result = self.protector.protect(["card ４１１１\u200b１１１１１１１１１１１１"])
        self.assertEqual(result.texts, ["card <CARD>"])
        self.assertEqual(result.counts, {"CARD": 1})

    def test_preserves_non_sensitive_intent(self) -> None:
        queries = [
            "How do I change my pin?", "My pin is blocked", "My passcode for the app stopped working",
            "My card has not arrived in 10 days", "A refund is pending for 3 days",
        ]
        self.assertEqual(self.protector.protect(queries).texts, queries)

    def test_fail_closed_and_empty_batch(self) -> None:
        self.assertEqual(self.protector.protect([]).texts, [])
        for invalid in ["", " ", "\u200b", "x" * (MAX_QUERY_CHARACTERS + 1)]:
            with self.subTest(length=len(invalid)), self.assertRaises(ValueError):
                self.protector.protect([invalid])

        class BrokenDetector:
            def detect(self, texts: list[str]) -> list[list[PiiSpan]]:
                _ = texts  # Fault injection deliberately ignores the supplied batch.
                raise RuntimeError("PII detector unavailable")
        with self.assertRaises(RuntimeError):
            PiiProtector(BrokenDetector()).protect(["A customer query"])

        class TruncatedDetector:
            def detect(self, texts: list[str]) -> list[list[PiiSpan]]:
                _ = texts
                return []
        with self.assertRaises(RuntimeError):
            PiiProtector(TruncatedDetector()).protect(["A customer query"])

        class BadOffsets:
            def detect(self, texts: list[str]) -> list[list[PiiSpan]]:
                _ = texts
                return [[PiiSpan(0, 1000, "PERSON")]]
        with self.assertRaises(ValueError):
            PiiProtector(BadOffsets()).protect(["A customer query"])

    def test_safe_ingestion_and_label_allowlist(self) -> None:
        self.assertEqual(len(BANKING77_INTENTS), 77)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.csv"
            path.write_text("text,category\nEmail jane@example.com,card_arrival\n", encoding="utf-8")
            frame, audit = read_protected_banking_csv(path, self.protector)
            self.assertEqual(frame["text"].tolist(), ["Email <EMAIL>"])
            self.assertEqual(audit["EMAIL"], 1)
            path.write_text("text,category\nquery,secret@example.com\n", encoding="utf-8")
            with self.assertRaises(ValueError) as raised:
                read_protected_banking_csv(path, self.protector)
            self.assertNotIn("secret@example.com", str(raised.exception))

    def test_collision_policy(self) -> None:
        train = pd.DataFrame({
            "text": ["same", "same", "ambiguous", "ambiguous", "test collision", "kept"],
            "category": ["a", "a", "a", "b", "a", "a"],
        })
        test = pd.DataFrame({"text": ["Test Collision"], "category": ["a"]})
        cleaned, audit = decontaminate_training(train, test)
        self.assertEqual(cleaned["text"].tolist(), ["same", "kept"])
        self.assertEqual(sum(audit.values()), 4)
        self.assertEqual(test["text"].tolist(), ["Test Collision"])

    def test_wordcloud_excludes_placeholders_and_rare_terms(self) -> None:
        frequencies = wordcloud_frequencies(
            ["card <EMAIL> <PERSON> raretoken", "card <EMAIL>", "card <PHONE>"], minimum_documents=2
        )
        self.assertEqual(frequencies, {"card": 3})


if __name__ == "__main__":
    unittest.main()
