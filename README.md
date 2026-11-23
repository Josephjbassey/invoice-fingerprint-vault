# Invoice Fingerprint Vault

[![Network: Gno.land Onyx](https://img.shields.io/badge/Network-Gno.land%20Onyx-f59e0b?style=flat-square)](https://faucet.gno.land)
[![Gno Version](https://img.shields.io/badge/GnoVM-v1.8.0-indigo?style=flat-square)](https://github.com/gnolang/gno)
[![Framework](https://img.shields.io/badge/Backend-Django%206.1-emerald?style=flat-square)](https://www.djangoproject.com)
[![Wallet](https://img.shields.io/badge/Web3%20Wallet-Adena%20Native-orange?style=flat-square)](https://adena.app)
[![Tests](https://img.shields.io/badge/Unit%20Tests-100%25%20Passing-brightgreen?style=flat-square)](https://github.com)
[![Security](https://img.shields.io/badge/Security-Production%20Hardened-blue?style=flat-square)](#-security--developer-compliance)

A production-grade, decentralized **Proof-of-Existence Registry** for invoices, agreements, and receipts built for the **Gno.land Hackathon 2026**.

Invoice Fingerprint Vault anchors cryptographic SHA-256 digests of commercial documents to the **Gno.land testnet (`onyx-1`)** using Gno's deterministic AVL tree state storage. Integrated natively with the **Adena Wallet** for 1-click passwordless Web3 authentication and transaction signing, paired with a modern Django application and public real-time ABCI query verification portal.

---

## 🌟 Key Innovations & Value Proposition

- 🛡️ **Zero-Knowledge Privacy:** Document contents and customer personally identifiable information (PII) **never leave the user's browser unhashed**. The 64-character SHA-256 fingerprint is calculated entirely client-side using the browser-native Web Crypto API.
- ⚡ **Immutable On-Chain Proof:** Fingerprints are committed to the Gno.land state tree alongside the submitter's bech32 address and block timestamp using deterministic AVL tree indexing.
- 🦊 **Native Adena Wallet Integration:** Seamless connection via `window.adena`, supporting `/vm.m_call` transaction dispatch and 1-click passwordless login without traditional database passwords.
- 🔍 **Public Third-Party Verification Portal:** Clients, auditors, and tax authorities can verify any document's authenticity in real-time by pasting its fingerprint or uploading the original file, evaluated live against Gno's CometBFT ABCI query RPC.
- 📜 **Downloadable Portable Proof Receipts:** Generates cryptographic JSON certificates conforming to proof-of-existence specifications with direct GnoScan explorer links.

---

## 🏛️ System Architecture

```
                                  +--------------------------------------------------+
                                  |                 User Browser                     |
                                  |  - Client-Side SHA-256 (Web Crypto API)          |
                                  |  - Adena Wallet Extension (window.adena)         |
                                  +------------------------+-------------------------+
                                                           |
                                      +--------------------+--------------------+
                                      |                                         |
                            (1) Sign Tx (/vm.m_call)                   (2) HTTP REST / HTML
                                      |                                         |
                                      v                                         v
                         +--------------------------+             +--------------------------+
                         |      Gno.land Node       |             |   Django 6.1 Backend     |
                         |   (onyx-1 / CometBFT)    | <---------+ |  - Off-Chain User Vault  |
                         +--------------------------+  ABCI Query |  - Live Network Monitor  |
                         | Realm:                   |  (vm/qrender|  - Proof Receipt Service |
                         | gno.land/r/.../vault     |             +--------------------------+
                         |  - avl.Tree Storage      |                           |
                         |  - Deterministic Lookup  |                           v
                         |  - chain.Emit Events     |             +--------------------------+
                         +--------------------------+             |  Encrypted SQLite / DB   |
                                                                  +--------------------------+
```

---

## ⛓️ On-Chain Deployment Details (Onyx-1 Testnet)

| Parameter | Value |
| :--- | :--- |
| **Network** | Gno.land Onyx Testnet (`onyx-1`) |
| **Deployed Realm Path** | `gno.land/r/g12uesl2nr27jh8q63x06lrpwarrndwsngm2u3d6/vault` |
| **Deployment Tx Hash** | `8891AF70E1FAE545BA99C37DCE627E0357B94415C2BC3B7CA349ADAFF4F487D3` |
| **Committed Block Height** | `1350400` |
| **Deployer Key Address** | `g12uesl2nr27jh8q63x06lrpwarrndwsngm2u3d6` |
| **User Adena Wallet** | `g1ryq6ldrlwtsvp0mhs5r8g7qflp2upe4lw57zk2` (Funded with 30 GNOT) |
| **Explorer** | [GnoScan Explorer](https://gnoscan.io) |

---

## 🚀 Quickstart & Installation

### Prerequisites
- Python 3.12+ (or 3.14)
- Go 1.22+
- Gno toolchain (`gno`, `gnokey`) v1.8.0

### 1. One-Line Setup
```bash
make setup
```
*Creates the Python virtual environment, installs pinned dependencies, and runs initial database migrations.*

### 2. Start Development Server
```bash
make run
```
*Accessible at `http://127.0.0.1:8000` (or `http://localhost:8000`).*
- **Default Test User:** `demo` / `hackathon123` (or sign in instantly with Adena wallet).

### 3. Run Test Suites
```bash
make test
```
*Executes Go wrapper tests, Gno.land native realm tests (`gno test .`), and all 12 Django integration & security tests.*

### 4. Code Compliance & Linting
```bash
make lint
make format
```
*Verifies compliance against Ruff standards and Go formatting rules.*

---

## ☁️ Deployment on Render

This project is pre-configured for seamless 1-click deployment on [Render](https://render.com).

### Option A: Automatic via Blueprint (`render.yaml`)
1. Push your repository to GitHub.
2. In the Render Dashboard, click **New +** > **Blueprint**.
3. Select your repository. Render will automatically parse [`render.yaml`](render.yaml), configure environment variables, run [`render-build.sh`](render-build.sh) (which compiles WhiteNoise static assets and applies database migrations), and launch Gunicorn.

### Option B: Manual Web Service Setup on Render
- **Environment:** `Python`
- **Build Command:** `./render-build.sh`
- **Start Command:** `gunicorn vault_project.wsgi:application`
- **Key Environment Variables:**
  - `DEBUG`: `False`
  - `PYTHON_VERSION`: `3.12.8`
  - `DJANGO_SECRET_KEY`: *(Generate strong secret)*
  - `ALLOWED_HOSTS`: `.onrender.com,localhost,127.0.0.1`
  - `CSRF_TRUSTED_ORIGINS`: `https://*.onrender.com`
  - `GNO_RPC_URL`: `https://rpc.onyx.testnets.gno.land:443`
  - `GNO_CHAIN_ID`: `onyx-1`
  - `GNO_REALM_PATH`: `gno.land/r/g12uesl2nr27jh8q63x06lrpwarrndwsngm2u3d6/vault`
  - `GNOSCAN_BASE_URL`: `https://gnoscan.io`

*Note: WhiteNoise serves all compressed CSS, JS, and invoice assets natively without requiring an external S3 bucket or CDN.*

---

## 🔒 Security & Developer Compliance

- **OWASP Compliance:** Full protection against XSS (automatic HTML escaping), CSRF protection, and SQL injection prevention via Django ORM parameterized queries.
- **Strict Input Validation:** 
  - Fingerprint inputs are enforced via regular expressions (`^[a-fA-F0-9]{64}$`).
  - Wallet addresses are verified against Cosmos/Gno bech32 formats (`^g1[a-z0-9]{36,58}$`).
- **File Upload Guardrails:**
  - Hard limit of 10MB per document (`FILE_UPLOAD_MAX_MEMORY_SIZE = 10MB`).
  - Strict extension whitelisting (`.pdf`, `.png`, `.jpg`, `.jpeg`, `.txt`). Arbitrary script execution (.exe, .sh, .py) is blocked at the form and API boundary.
- **Zero Deployment Warnings:** Evaluated against `python manage.py check --deploy` with 0 security warnings in production mode.
- **No Committed Secrets:** Private keys, SQLite runtime databases, and mnemonic seed phrases are excluded via `.gitignore`.

---

## 🧪 Sample Invoices & Test Assets

Realistic sample invoices with pre-computed hashes and companion PNG preview assets are provided in [`sample_invoices/`](sample_invoices/):

- [`invoice_apex_design_101.pdf`](sample_invoices/invoice_apex_design_101.pdf): Consulting & Smart Contract Architecture Invoice ($11,961.63)
- [`receipt_nexus_cloud_202.pdf`](sample_invoices/receipt_nexus_cloud_202.pdf): Dedicated RPC & Infrastructure Receipt ($475.00)
- [`contract_retainer_zenith_303.pdf`](sample_invoices/contract_retainer_zenith_303.pdf): Web3 Protocol Retainer & Audit Agreement (20,678.40 CHF)

Generate or refresh sample assets at any time with:
```bash
make invoices
```

---

## 🎬 Hackathon Demo Video & Media

- **Final Demo Video:** [`media/demo_video_gnome_vault.mp4`](media/demo_video_gnome_vault.mp4)
- **Length:** 2 minutes 10 seconds *(strictly compliant with the < 5 minute rule)*
- **Resolution:** 1080p Full HD (1920x1080) progressive 25 fps
- **Narration Audio:** Studio neural voiceover synchronized with on-screen actions
- **Keyframe Snapshots:** [`media/snapshots/`](media/snapshots/)

---

## 🗺️ Production Roadmap

1. **Batch Document Timestamping (Q1):** Merkle root aggregation enabling enterprise users to commit thousands of invoices in a single transaction with sub-cent overhead.
2. **GRC-20 Micropayments (Q2):** Pay-per-verification API and automated notary royalties using custom GRC-20 tokens on Gno.land.
3. **Mobile Camera Scanning (Q3):** Native mobile app with real-time camera QR/barcode and optical fingerprint scanning for on-site supply-chain verification.

---

## 📄 License

MIT License. Built with pride for the **Gno.land 2026 Hackathon**.
