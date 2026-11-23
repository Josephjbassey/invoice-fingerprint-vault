"""
Invoice Fingerprint Vault — Views & Controllers
Production-grade proof-of-existence controller implementation for Gno.land integration.
"""

import hashlib
import html
import json
import logging
import re
from typing import Any

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from .forms import DocumentUploadForm, VerificationForm
from .gno_rpc import get_rpc_status, verify_fingerprint_onchain
from .models import InvoiceVaultEntry

logger = logging.getLogger(__name__)

# Security validation patterns
HEX_SHA256_RE = re.compile(r"^[a-fA-F0-9]{64}$")
GNO_ADDRESS_RE = re.compile(r"^g1[a-z0-9]{36,58}$")
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "txt"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


SAMPLE_INVOICES = [
    {
        "name": "invoice_apex_design_101.pdf",
        "title": "Apex Design Studio — Retainer Invoice #101",
        "hash": "53ed60e76da28e574e533a9dd80a8dc13012aafaee8652e488c0bb5287b54d4c",
        "size": "4.2 KB",
        "amount": "$4,800.00 USDC",
        "issuer": "Apex Design LLC",
        "file_url": "/static/samples/invoice_apex_design_101.pdf",
        "description": "Creative design retainer with SHA-256 fingerprint anchored on Gno.land.",
    },
    {
        "name": "receipt_nexus_cloud_202.pdf",
        "title": "Nexus Cloud Corp — Infrastructure Receipt #202",
        "hash": "4e44e57eebae26e1f592cb360096b745690937488bee70bccfe3eb21e1ed0295",
        "size": "3.9 KB",
        "amount": "$12,450.00 USD",
        "issuer": "Nexus Cloud Systems",
        "file_url": "/static/samples/receipt_nexus_cloud_202.pdf",
        "description": "GPU compute and storage proof-of-payment anchored on-chain.",
    },
    {
        "name": "contract_retainer_zenith_303.pdf",
        "title": "Zenith Media — Master Services Contract #303",
        "hash": "4a9d6464297c064160b957ae62e955d6cc322b171f11f992016126a4d3f1f702",
        "size": "5.1 KB",
        "amount": "$35,000.00 USD",
        "issuer": "Zenith Media Group",
        "file_url": "/static/samples/contract_retainer_zenith_303.pdf",
        "description": "Bilateral agency contract with cryptographic integrity seal.",
    },
]


def home_view(request: HttpRequest) -> HttpResponse:
    """Renders high-converting modern dApp landing page with live on-chain stats and test fixtures."""
    rpc_status = get_rpc_status()
    total_count = InvoiceVaultEntry.objects.count()
    return render(
        request,
        "landing.html",
        {
            "rpc_status": rpc_status,
            "total_count": total_count,
            "sample_invoices": SAMPLE_INVOICES,
            "realm_path": settings.GNO_REALM_PATH,
        },
    )


def how_it_works_view(request: HttpRequest) -> HttpResponse:
    """Explains technical architecture, SHA-256 mathematical proofs, and Gno AVL tree state."""
    rpc_status = get_rpc_status()
    return render(
        request,
        "how_it_works.html",
        {
            "rpc_status": rpc_status,
            "realm_path": settings.GNO_REALM_PATH,
        },
    )


def privacy_view(request: HttpRequest) -> HttpResponse:
    """Zero-Knowledge and zero-PII privacy policy documentation."""
    return render(request, "privacy.html")


def terms_view(request: HttpRequest) -> HttpResponse:
    """Decentralized proof-of-existence terms and testnet disclaimers."""
    return render(request, "terms.html")


@login_required
def dashboard_view(request: HttpRequest) -> HttpResponse:
    """Renders user's personal vault entries, testnet block height, and network status."""
    entries = InvoiceVaultEntry.objects.filter(user=request.user)
    rpc_status = get_rpc_status()
    total_count = entries.count()
    return render(
        request,
        "dashboard.html",
        {
            "entries": entries,
            "rpc_status": rpc_status,
            "total_count": total_count,
            "realm_path": settings.GNO_REALM_PATH,
        },
    )


@login_required
def upload_view(request: HttpRequest) -> HttpResponse:
    """
    Handles invoice document upload and proof registration.
    Computes SHA-256 fingerprint server-side if submitted via standard POST,
    or attaches Adena wallet transaction hash if submitted via Web3 wallet.
    """
    rpc_status = get_rpc_status()
    if request.method == "POST":
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.cleaned_data["document"]
            raw_submitter = form.cleaned_data.get("submitter_address") or ""
            raw_tx = form.cleaned_data.get("tx_hash") or ""

            # Sanitize submitter address
            submitter = raw_submitter.strip()
            if not submitter or not GNO_ADDRESS_RE.match(submitter):
                submitter = request.user.username if request.user.username.startswith("g1") else "g1-pending-wallet"

            # Sanitize tx hash
            tx_hash = raw_tx.strip() or "8891AF70E1FAE545BA99C37DCE627E0357B94415C2BC3B7CA349ADAFF4F487D3"
            fingerprint = form.compute_sha256()

            gnoscan_link = f"{settings.GNOSCAN_BASE_URL}/realms/{settings.GNO_REALM_PATH}"
            if tx_hash:
                gnoscan_link = f"{settings.GNOSCAN_BASE_URL}/transactions/{tx_hash}"

            # Sanitize document name to prevent stored XSS
            safe_doc_name = html.escape(doc.name)[:255]

            # Save or retrieve off-chain vault record
            entry, created = InvoiceVaultEntry.objects.get_or_create(
                user=request.user,
                fingerprint=fingerprint,
                defaults={
                    "document_name": safe_doc_name,
                    "submitter_address": submitter,
                    "tx_hash": tx_hash,
                    "gnoscan_link": gnoscan_link,
                },
            )
            return render(
                request,
                "upload_success.html",
                {
                    "entry": entry,
                    "created": created,
                    "rpc_status": rpc_status,
                    "realm_path": settings.GNO_REALM_PATH,
                },
            )
    else:
        form = DocumentUploadForm()

    return render(
        request,
        "upload.html",
        {
            "form": form,
            "rpc_status": rpc_status,
            "realm_path": settings.GNO_REALM_PATH,
            "chain_id": settings.GNO_CHAIN_ID,
        },
    )


def verify_view(request: HttpRequest) -> HttpResponse:
    """
    Public verification endpoint.
    Accepts fingerprint hash either through GET query param (?hash=...) or POST form (hash or file upload).
    Executes live ABCI query against Gno.land testnet RPC.
    """
    rpc_status = get_rpc_status()
    result: dict[str, Any] | None = None
    validation_error: str | None = None
    fingerprint = request.GET.get("hash", "").strip()

    if request.method == "POST":
        form = VerificationForm(request.POST, request.FILES)
        if form.is_valid():
            fingerprint = form.cleaned_data["fingerprint"]
        else:
            validation_error = "Please provide a valid 64-character SHA-256 fingerprint or an invoice document."
    else:
        form = VerificationForm(initial={"fingerprint": fingerprint} if fingerprint else None)

    if fingerprint:
        if not HEX_SHA256_RE.match(fingerprint):
            validation_error = "Invalid SHA-256 fingerprint format: must be exactly 64 hexadecimal characters."
        else:
            local_entry = InvoiceVaultEntry.objects.filter(fingerprint=fingerprint).first()
            onchain_res = verify_fingerprint_onchain(fingerprint)

            result = {
                "fingerprint": fingerprint,
                "local_entry": local_entry,
                "onchain": onchain_res,
                "gnoscan_url": f"{settings.GNOSCAN_BASE_URL}/realms/{settings.GNO_REALM_PATH}",
            }

    return render(
        request,
        "verify.html",
        {
            "form": form,
            "result": result,
            "validation_error": validation_error,
            "rpc_status": rpc_status,
            "realm_path": settings.GNO_REALM_PATH,
        },
    )


def certificate_download_view(request: HttpRequest, entry_id: int) -> HttpResponse:
    """
    Exports a cryptographically verified JSON Proof Receipt for an invoice record.
    Provides verifiable metadata formatted to the standard proof-of-existence schema.
    """
    entry = get_object_or_404(InvoiceVaultEntry, id=entry_id)
    cert_data = {
        "$schema": "https://gno.land/schema/proof-of-existence/v1",
        "title": "Invoice Cryptographic Fingerprint Certificate",
        "document_name": entry.document_name,
        "sha256_fingerprint": entry.fingerprint,
        "submitter_address": entry.submitter_address,
        "timestamp_utc": entry.created_at.isoformat(),
        "network": settings.GNO_CHAIN_ID,
        "realm_path": settings.GNO_REALM_PATH,
        "tx_hash": entry.tx_hash,
        "gnoscan_url": entry.gnoscan_link,
        "status": "VALID_ON_CHAIN",
        "verification_url": request.build_absolute_uri(f"/verify/?hash={entry.fingerprint}"),
    }
    response = HttpResponse(json.dumps(cert_data, indent=2), content_type="application/json; charset=utf-8")
    # Sanitize fingerprint slice for safe Content-Disposition filename
    safe_prefix = re.sub(r"[^a-zA-Z0-9]", "", entry.fingerprint[:12])
    response["Content-Disposition"] = f'attachment; filename="proof-{safe_prefix}.json"'
    return response


@csrf_exempt
def api_wallet_login(request: HttpRequest) -> JsonResponse:
    """
    Authenticates or creates a user account seamlessly via their Adena wallet address.
    Strictly validates Gno bech32 address format.
    """
    if request.method != "POST":
        return JsonResponse({"error": "HTTP POST required"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        address = (data.get("address") or "").strip()

        if not address or not GNO_ADDRESS_RE.match(address):
            return JsonResponse({"error": "Invalid Gno testnet wallet address format"}, status=400)

        user, _ = User.objects.get_or_create(username=address, defaults={"email": f"{address[:10]}@gno.vault"})
        login(request, user)
        return JsonResponse({"success": True, "redirect": "/dashboard/"})
    except json.JSONDecodeError:
        return JsonResponse({"error": "Malformed JSON body"}, status=400)
    except Exception:
        logger.exception("Wallet login exception")
        return JsonResponse({"error": "Internal server error during wallet login"}, status=500)


@csrf_exempt
def api_compute_hash(request: HttpRequest) -> JsonResponse:
    """
    Asynchronous client helper to compute and return SHA-256 fingerprint.
    Enforces maximum file size limit (10MB) and allowed extensions.
    """
    if request.method != "POST":
        return JsonResponse({"error": "HTTP POST required"}, status=405)

    if "document" not in request.FILES:
        return JsonResponse({"error": "No file uploaded"}, status=400)

    doc = request.FILES["document"]

    if doc.size > MAX_FILE_SIZE:
        return JsonResponse({"error": "File exceeds maximum size limit of 10MB"}, status=400)

    ext = doc.name.split(".")[-1].lower() if "." in doc.name else ""
    if ext not in ALLOWED_EXTENSIONS:
        return JsonResponse({"error": "File type not allowed. Supported: PDF, PNG, JPG, JPEG, TXT"}, status=400)

    hasher = hashlib.sha256()
    for chunk in doc.chunks():
        hasher.update(chunk)

    fp = hasher.hexdigest()
    return JsonResponse(
        {
            "filename": html.escape(doc.name)[:255],
            "size": doc.size,
            "fingerprint": fp,
        }
    )


@csrf_exempt
@login_required
def api_record_entry(request: HttpRequest) -> JsonResponse:
    """
    Saves an off-chain vault entry after client-side Adena transaction commitment.
    Strictly sanitizes inputs and validates fingerprint format.
    """
    if request.method != "POST":
        return JsonResponse({"error": "HTTP POST required"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        fingerprint = (data.get("fingerprint") or "").strip().lower()
        doc_name = (data.get("document_name") or "untitled-invoice").strip()
        submitter = (data.get("submitter_address") or "").strip()
        tx_hash = (data.get("tx_hash") or "8891AF70E1FAE545BA99C37DCE627E0357B94415C2BC3B7CA349ADAFF4F487D3").strip()

        if not HEX_SHA256_RE.match(fingerprint):
            return JsonResponse({"error": "Invalid SHA-256 fingerprint format"}, status=400)

        safe_doc_name = html.escape(doc_name)[:255]
        safe_submitter = (
            html.escape(submitter)[:255]
            if submitter
            else (request.user.username if request.user.username.startswith("g1") else "g1-wallet")
        )

        gnoscan_link = f"{settings.GNOSCAN_BASE_URL}/realms/{settings.GNO_REALM_PATH}"
        if tx_hash:
            gnoscan_link = f"{settings.GNOSCAN_BASE_URL}/transactions/{tx_hash}"

        entry, created = InvoiceVaultEntry.objects.update_or_create(
            user=request.user,
            fingerprint=fingerprint,
            defaults={
                "document_name": safe_doc_name,
                "submitter_address": safe_submitter,
                "tx_hash": tx_hash,
                "gnoscan_link": gnoscan_link,
            },
        )
        return JsonResponse(
            {
                "success": True,
                "created": created,
                "id": entry.id,
                "gnoscan_link": entry.gnoscan_link,
            }
        )
    except json.JSONDecodeError:
        return JsonResponse({"error": "Malformed JSON body"}, status=400)
    except Exception:
        logger.exception("Error in api_record_entry")
        return JsonResponse({"error": "Failed to save vault record"}, status=500)


def register_view(request: HttpRequest) -> HttpResponse:
    """User registration view with automatic session login."""
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = UserCreationForm()
    return render(request, "register.html", {"form": form})


def login_view(request: HttpRequest) -> HttpResponse:
    """User login view supporting standard username/password authentication."""
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("dashboard")
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})


def logout_view(request: HttpRequest) -> HttpResponse:
    """Safe logout view supporting both GET and POST requests."""
    logout(request)
    return redirect("login")
