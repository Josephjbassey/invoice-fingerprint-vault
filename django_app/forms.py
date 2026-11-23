import hashlib
import re

from django import forms

HEX_SHA256_RE = re.compile(r"^[a-fA-F0-9]{64}$")


class DocumentUploadForm(forms.Form):
    document = forms.FileField(required=False, help_text="Upload invoice or receipt (PDF, PNG, JPG up to 10MB)")
    fingerprint = forms.CharField(max_length=64, required=False, widget=forms.HiddenInput())
    document_name = forms.CharField(max_length=255, required=False, widget=forms.HiddenInput())
    submitter_address = forms.CharField(max_length=255, required=False, widget=forms.HiddenInput())
    tx_hash = forms.CharField(max_length=255, required=False, widget=forms.HiddenInput())

    def clean_document(self):
        doc = self.cleaned_data.get("document")
        if doc:
            if doc.size > 10 * 1024 * 1024:
                raise forms.ValidationError("File size must not exceed 10MB.")
            ext = doc.name.split(".")[-1].lower() if "." in doc.name else ""
            allowed = ["pdf", "png", "jpg", "jpeg", "txt"]
            if ext not in allowed:
                raise forms.ValidationError("Allowed formats: PDF, PNG, JPG, JPEG, TXT.")
        return doc

    def clean(self):
        cleaned_data = super().clean()
        doc = cleaned_data.get("document")
        fp = (cleaned_data.get("fingerprint") or "").strip().lower()

        if not doc and not fp:
            raise forms.ValidationError("Please provide either an invoice document or a pre-computed SHA-256 fingerprint.")

        if fp and not HEX_SHA256_RE.match(fp):
            raise forms.ValidationError("Invalid SHA-256 fingerprint format: must be 64 hexadecimal characters.")

        return cleaned_data

    def compute_sha256(self):
        doc = self.cleaned_data.get("document")
        if doc:
            hasher = hashlib.sha256()
            for chunk in doc.chunks():
                hasher.update(chunk)
            return hasher.hexdigest()
        return (self.cleaned_data.get("fingerprint") or "").strip().lower()


class VerificationForm(forms.Form):
    fingerprint = forms.CharField(
        max_length=64,
        min_length=64,
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter 64-character SHA-256 hash (e.g. e3b0c44298fc1c14...)",
                "class": "w-full px-4 py-3 bg-zinc-900 border border-zinc-700 rounded-lg text-white font-mono text-sm focus:outline-none focus:border-amber-500",
            }
        ),
    )
    document = forms.FileField(
        required=False, widget=forms.FileInput(attrs={"class": "hidden", "id": "verify-file-input"})
    )

    def clean(self):
        cleaned_data = super().clean()
        fp = cleaned_data.get("fingerprint")
        doc = cleaned_data.get("document")
        if not fp and not doc:
            raise forms.ValidationError("Please provide either a fingerprint or upload a file.")
        if doc and not fp:
            hasher = hashlib.sha256()
            for chunk in doc.chunks():
                hasher.update(chunk)
            cleaned_data["fingerprint"] = hasher.hexdigest()
        return cleaned_data
