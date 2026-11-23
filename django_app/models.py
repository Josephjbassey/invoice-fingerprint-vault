from django.contrib.auth.models import User
from django.db import models


class InvoiceVaultEntry(models.Model):
    """Off-chain record of an invoice fingerprint registered on Gno.land testnet."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vault_entries")
    document_name = models.CharField(max_length=255)
    fingerprint = models.CharField(max_length=64, db_index=True)  # SHA-256 hex
    timestamp = models.DateTimeField(auto_now_add=True)
    submitter_address = models.CharField(max_length=255)  # Adena wallet address
    tx_hash = models.CharField(max_length=255, blank=True)  # Gno.land testnet tx
    gnoscan_link = models.URLField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        unique_together = (("user", "fingerprint"),)

    def __str__(self):
        return f"{self.document_name} ({self.fingerprint[:16]}...)"
