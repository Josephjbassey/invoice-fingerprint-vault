"""
Invoice Fingerprint Vault — Comprehensive Test Suite
Validates authentication, access controls, input sanitization, file limits,
proof-of-existence queries, and on-chain RPC integration.
"""

import hashlib
import json

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from .models import InvoiceVaultEntry


class InvoiceVaultSecurityAndIntegrationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testauditor", password="SecurePassword123!")
        self.client = Client()
        self.client.login(username="testauditor", password="SecurePassword123!")

    # -------------------------------------------------------------
    # 1. Document Upload & File Validation Tests
    # -------------------------------------------------------------
    def test_upload_valid_invoice(self):
        content = b"INVOICE #INV-2026-999\nClient: Global Tech\nTotal: $12,500.00"
        expected_hash = hashlib.sha256(content).hexdigest()
        uploaded = SimpleUploadedFile("invoice_999.pdf", content, content_type="application/pdf")

        response = self.client.post(
            reverse("upload"),
            {
                "document": uploaded,
                "submitter_address": "g1ryq6ldrlwtsvp0mhs5r8g7qflp2upe4lw57zk2",
                "tx_hash": "8891AF70E1FAE545BA99C37DCE627E0357B94415C2BC3B7CA349ADAFF4F487D3",
            },
        )
        self.assertEqual(response.status_code, 200)

        entry = InvoiceVaultEntry.objects.get(fingerprint=expected_hash)
        self.assertEqual(entry.document_name, "invoice_999.pdf")
        self.assertEqual(entry.submitter_address, "g1ryq6ldrlwtsvp0mhs5r8g7qflp2upe4lw57zk2")
        self.assertIn(expected_hash, response.content.decode("utf-8"))

    def test_upload_precomputed_fingerprint_without_file(self):
        """Allows anchoring pre-computed SHA-256 fingerprint without re-uploading file."""
        fp = "c" * 64
        response = self.client.post(
            reverse("upload"),
            {
                "fingerprint": fp,
                "document_name": "prehashed_invoice.pdf",
                "submitter_address": "g1ryq6ldrlwtsvp0mhs5r8g7qflp2upe4lw57zk2",
                "tx_hash": "tx-precomputed-123",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(InvoiceVaultEntry.objects.filter(fingerprint=fp).exists())
        entry = InvoiceVaultEntry.objects.get(fingerprint=fp)
        self.assertEqual(entry.document_name, "prehashed_invoice.pdf")

    def test_upload_disallowed_file_extension(self):
        """Ensures non-document files (.exe, .sh) are rejected."""
        malicious_content = b"#!/bin/bash\necho hack"
        uploaded = SimpleUploadedFile("script.sh", malicious_content, content_type="application/x-sh")

        response = self.client.post(
            reverse("upload"),
            {
                "document": uploaded,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(InvoiceVaultEntry.objects.filter(document_name="script.sh").exists())

    def test_upload_file_size_exceeds_limit(self):
        """Rejects files larger than 10MB."""
        oversized = SimpleUploadedFile("large_invoice.pdf", b"x" * (11 * 1024 * 1024), content_type="application/pdf")
        response = self.client.post(reverse("upload"), {"document": oversized})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(InvoiceVaultEntry.objects.filter(document_name="large_invoice.pdf").exists())

    # -------------------------------------------------------------
    # 2. Access Control & Authentication Gating
    # -------------------------------------------------------------
    def test_unauthenticated_access_redirects(self):
        anon_client = Client()
        # Upload route requires authentication
        resp_upload = anon_client.get(reverse("upload"))
        self.assertEqual(resp_upload.status_code, 302)
        self.assertIn(reverse("login"), resp_upload.url)

        # Dashboard requires authentication
        resp_dash = anon_client.get(reverse("dashboard"))
        self.assertEqual(resp_dash.status_code, 302)
        self.assertIn(reverse("login"), resp_dash.url)

        # Public verification is accessible to anyone
        resp_verify = anon_client.get(reverse("verify"))
        self.assertEqual(resp_verify.status_code, 200)

    # -------------------------------------------------------------
    # 3. Public Verification Portal
    # -------------------------------------------------------------
    def test_verify_by_hash_query(self):
        test_hash = "53ed60e76da28e574e533a9dd80a8dc13012aafaee8652e488c0bb5287b54d4c"
        InvoiceVaultEntry.objects.create(
            user=self.user,
            document_name="apex_design.pdf",
            fingerprint=test_hash,
            submitter_address="g1ryq6ldrlwtsvp0mhs5r8g7qflp2upe4lw57zk2",
            tx_hash="8891AF70E1FAE545BA99C37DCE627E0357B94415C2BC3B7CA349ADAFF4F487D3",
        )

        response = self.client.get(reverse("verify") + f"?hash={test_hash}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, test_hash)
        self.assertContains(response, "apex_design.pdf")
        self.assertContains(response, "VERIFIED PROOF OF EXISTENCE")

    def test_verify_invalid_hash_format(self):
        """Ensures malformed or non-hex hashes display a friendly validation error."""
        response = self.client.get(reverse("verify") + "?hash=not-a-valid-sha256")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid SHA-256 fingerprint format")

    def test_verify_by_file_upload(self):
        content = b"TEST RECEIPT #4411"
        computed_hash = hashlib.sha256(content).hexdigest()
        uploaded = SimpleUploadedFile("receipt.pdf", content, content_type="application/pdf")

        response = self.client.post(
            reverse("verify"),
            {
                "document": uploaded,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, computed_hash)

    # -------------------------------------------------------------
    # 4. Adena Wallet API & Passwordless Login
    # -------------------------------------------------------------
    def test_wallet_login_success(self):
        valid_gno_addr = "g1ryq6ldrlwtsvp0mhs5r8g7qflp2upe4lw57zk2"
        anon_client = Client()
        response = anon_client.post(
            reverse("api_wallet_login"), data={"address": valid_gno_addr}, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("redirect"), "/dashboard/")
        self.assertTrue(User.objects.filter(username=valid_gno_addr).exists())

    def test_wallet_login_invalid_address(self):
        anon_client = Client()
        # Invalid prefix
        resp = anon_client.post(
            reverse("api_wallet_login"),
            data={"address": "0x71C63F56434419A65F3480D61D2B9D6F7C85"},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

        # Too short
        resp2 = anon_client.post(
            reverse("api_wallet_login"), data={"address": "g1short"}, content_type="application/json"
        )
        self.assertEqual(resp2.status_code, 400)

    # -------------------------------------------------------------
    # 5. Cryptographic Proof Receipt Download
    # -------------------------------------------------------------
    def test_certificate_download_schema(self):
        test_hash = "e" * 64
        entry = InvoiceVaultEntry.objects.create(
            user=self.user,
            document_name="cloud_infrastructure.pdf",
            fingerprint=test_hash,
            submitter_address="g1ryq6ldrlwtsvp0mhs5r8g7qflp2upe4lw57zk2",
            tx_hash="8891AF70E1FAE545BA99C37DCE627E0357B94415C2BC3B7CA349ADAFF4F487D3",
        )
        response = self.client.get(reverse("certificate_download", args=[entry.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/json", response["Content-Type"])
        self.assertIn(f"proof-{test_hash[:12]}.json", response["Content-Disposition"])

        payload = json.loads(response.content.decode("utf-8"))
        self.assertEqual(payload["sha256_fingerprint"], test_hash)
        self.assertEqual(payload["document_name"], "cloud_infrastructure.pdf")
        self.assertEqual(payload["status"], "VALID_ON_CHAIN")

    # -------------------------------------------------------------
    # 6. AJAX Hash & Entry Recording APIs
    # -------------------------------------------------------------
    def test_api_compute_hash(self):
        sample_data = b"SAMPLE TEST INVOICE CONTENT"
        expected = hashlib.sha256(sample_data).hexdigest()
        uploaded = SimpleUploadedFile("sample.txt", sample_data, content_type="text/plain")

        response = self.client.post(reverse("api_compute_hash"), {"document": uploaded})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("fingerprint"), expected)

    def test_api_record_entry_validation(self):
        # Valid entry
        valid_data = {
            "fingerprint": "b" * 64,
            "document_name": "audit_contract.pdf",
            "submitter_address": "g1ryq6ldrlwtsvp0mhs5r8g7qflp2upe4lw57zk2",
            "tx_hash": "tx-123",
        }
        resp = self.client.post(reverse("api_record_entry"), data=valid_data, content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(InvoiceVaultEntry.objects.filter(fingerprint="b" * 64).exists())

        # Invalid fingerprint format
        invalid_data = {
            "fingerprint": "invalid-hash",
            "document_name": "bad.pdf",
        }
        resp_err = self.client.post(reverse("api_record_entry"), data=invalid_data, content_type="application/json")
        self.assertEqual(resp_err.status_code, 400)

    # -------------------------------------------------------------
    # 7. Persistence & Dashboard Visibility Lifecycle Tests
    # -------------------------------------------------------------
    def test_dashboard_visibility_after_logout_and_relogin(self):
        """
        Validates the critical bugfix:
        1. User creates entry via wallet address
        2. Logs out
        3. Logs back in with Adena wallet login OR password login
        4. Entry persists and is visible on dashboard
        """
        adena_addr = "g1ryq6ldrlwtsvp0mhs5r8g7qflp2upe4lw57zk2"
        test_hash = "d" * 64
        InvoiceVaultEntry.objects.create(
            user=self.user,
            document_name="critical_tax_audit.pdf",
            fingerprint=test_hash,
            submitter_address=adena_addr,
            tx_hash="tx-verified-onchain-999",
        )

        # Confirm visible while logged in as username
        resp1 = self.client.get(reverse("dashboard"))
        self.assertEqual(resp1.status_code, 200)
        self.assertContains(resp1, "critical_tax_audit.pdf")

        # 1. Log out
        self.client.logout()

        # 2. Log in using Adena wallet
        resp_login = self.client.post(
            reverse("api_wallet_login"),
            data={"address": adena_addr},
            content_type="application/json",
        )
        self.assertEqual(resp_login.status_code, 200)

        # 3. Check dashboard again: must display the entry!
        resp2 = self.client.get(reverse("dashboard"))
        self.assertEqual(resp2.status_code, 200)
        self.assertContains(resp2, "critical_tax_audit.pdf")
        self.assertContains(resp2, test_hash[:10])

        # 4. Log out again, log back in as original username user
        self.client.logout()
        self.client.login(username="testauditor", password="SecurePassword123!")

        resp3 = self.client.get(reverse("dashboard") + f"?wallet={adena_addr}")
        self.assertEqual(resp3.status_code, 200)
        self.assertContains(resp3, "critical_tax_audit.pdf")

    def test_api_wallet_connect_linking(self):
        """Validates that connecting a wallet associates orphaned entries."""
        wallet = "g1ryq6ldrlwtsvp0mhs5r8g7qflp2upe4lw57zk2"
        other_user = User.objects.create_user(username="otheruser", password="password")
        entry = InvoiceVaultEntry.objects.create(
            user=other_user,
            document_name="linked_receipt.pdf",
            fingerprint="f" * 64,
            submitter_address=wallet,
        )

        resp = self.client.post(
            reverse("api_wallet_connect"),
            data={"address": wallet},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        entry.refresh_from_db()
        self.assertEqual(entry.user, self.user)

    def test_api_sync_onchain_proof(self):
        """Tests importing an on-chain verified hash into user's vault."""
        sample_hash = "53ed60e76da28e574e533a9dd80a8dc13012aafaee8652e488c0bb5287b54d4c"
        resp = self.client.post(
            reverse("api_sync_onchain"),
            data={"fingerprint": sample_hash},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get("success"))
        self.assertTrue(InvoiceVaultEntry.objects.filter(fingerprint=sample_hash).exists())

    # -------------------------------------------------------------
    # 7. Public Content & Educational View Tests
    # -------------------------------------------------------------
    def test_landing_page_renders_with_sample_fixtures(self):
        anon_client = Client()
        response = anon_client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tamper-Proof Document")
        self.assertContains(response, "invoice_apex_design_101.pdf")
        self.assertContains(response, "receipt_nexus_cloud_202.pdf")
        self.assertContains(response, "contract_retainer_zenith_303.pdf")
        self.assertContains(response, "53ed60e76da28e574e533a9dd80a8dc13012aafaee8652e488c0bb5287b54d4c")

    def test_how_it_works_architecture_page(self):
        anon_client = Client()
        response = anon_client.get(reverse("how_it_works"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Security Architecture")
        self.assertContains(response, "SHA-256")
        self.assertContains(response, "gno.land/p/demo/avl")

    def test_privacy_and_terms_pages(self):
        anon_client = Client()
        resp_priv = anon_client.get(reverse("privacy"))
        self.assertEqual(resp_priv.status_code, 200)
        self.assertContains(resp_priv, "Zero-Knowledge")

        resp_terms = anon_client.get(reverse("terms"))
        self.assertEqual(resp_terms.status_code, 200)
        self.assertContains(resp_terms, "Proof-of-Existence Disclaimers")
