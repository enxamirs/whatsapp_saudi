# Copyright (c) 2023, ERPGulf.com and Contributors
# See license.txt

from frappe.tests.utils import FrappeTestCase
from whatsapp_saudi.overrides.whtatsapp_notification import (
    normalize_phone,
    normalize_phone_bavatel,
    _get_phone_from_doc,
)


class TestNormalizePhone(FrappeTestCase):
    """Unit tests for phone normalisation helpers."""

    def test_normalize_phone_strips_plus(self):
        self.assertEqual(normalize_phone("+966512345678"), "966512345678")

    def test_normalize_phone_strips_leading_zeros(self):
        self.assertEqual(normalize_phone("00966512345678"), "966512345678")

    def test_normalize_phone_expands_local_saudi(self):
        # 10-digit number starting with 0 → prepend 966 and drop leading 0
        self.assertEqual(normalize_phone("0512345678"), "966512345678")

    def test_normalize_phone_egypt(self):
        self.assertEqual(normalize_phone("+201222532827"), "201222532827")

    def test_normalize_phone_none_returns_empty(self):
        self.assertEqual(normalize_phone(None), "")

    def test_normalize_phone_empty_returns_empty(self):
        self.assertEqual(normalize_phone(""), "")

    def test_normalize_phone_invalid_short_returns_empty(self):
        # fewer than 7 digits → invalid
        self.assertEqual(normalize_phone("+123"), "")

    def test_normalize_phone_non_digit_returns_empty(self):
        self.assertEqual(normalize_phone("abc-xyz"), "")

    def test_normalize_phone_bavatel_adds_plus(self):
        result = normalize_phone_bavatel("966512345678")
        self.assertEqual(result, "+966512345678")

    def test_normalize_phone_bavatel_none_returns_empty(self):
        self.assertEqual(normalize_phone_bavatel(None), "")


class _MockDoc:
    """Minimal stand-in for a Frappe document."""
    def __init__(self, data):
        self._data = data

    def get(self, key, default=None):
        return self._data.get(key, default)


class TestGetPhoneFromDoc(FrappeTestCase):
    """Unit tests for _get_phone_from_doc smart detection."""

    def test_prefers_explicit_field(self):
        doc = _MockDoc({"mobile_no": "+966111111111", "whatsapp_number": "+966222222222"})
        self.assertEqual(_get_phone_from_doc(doc, preferred_field="mobile_no"), "+966111111111")

    def test_falls_back_when_preferred_field_empty(self):
        doc = _MockDoc({"mobile_no": "", "custom_whatsapp_number": "+966333333333"})
        result = _get_phone_from_doc(doc, preferred_field="mobile_no")
        self.assertEqual(result, "+966333333333")

    def test_falls_back_to_phone(self):
        doc = _MockDoc({"phone": "+966444444444"})
        result = _get_phone_from_doc(doc, preferred_field="mobile_no")
        self.assertEqual(result, "+966444444444")

    def test_returns_none_when_no_phone_fields(self):
        doc = _MockDoc({"customer_name": "Acme"})
        self.assertIsNone(_get_phone_from_doc(doc, preferred_field="mobile_no"))

    def test_returns_none_when_no_preferred_field_and_no_fallbacks(self):
        doc = _MockDoc({})
        self.assertIsNone(_get_phone_from_doc(doc))
