# Invoice Fingerprint Vault — Brand Asset & Usage Guidelines

This document specifies the official brand standards, grid geometry, color rules, and implementation instructions for the **Invoice Fingerprint Vault** brand mark, icon, and favicon suite.

---

## 1. Brand Mark Overview
- **Brand Name:** Invoice Fingerprint Vault (or "Invoice Vault")
- **Brand Brief:** A sovereign decentralized document notary on Gno.land providing tamper-proof SHA-256 fingerprinting for enterprise invoices and contracts — secure, cryptographic, and legible from a 16x16 favicon to 1024x1024 app icon.
- **Logo Type:** Combination Mark (Geometric Vault Shield & Biometric Hash Mark + Precision Wordmark)
- **Grid System:** 32x32 unit vector grid with 4-unit safe zone padding.

---

## 2. Color Palette (3-Color System)

| Role | Color Name | Hex Code | Usage |
|------|------------|----------|-------|
| **Primary** | Electric Amber / Gold | `#f59e0b` (`#fbbf24` highlight, `#d97706` shadow) | Shield boundary, biometric ridges, logotype accent |
| **Accent** | Tendermint Emerald | `#10b981` | Validator consensus node, live status indicators |
| **Foundation** | Obsidian Dark | `#08090a` (`#0c0d10` elevated surface) | Icon background tile, dark mode canvas |
| **Wordmark** | Pure White | `#ffffff` | Primary "Invoice" typography |
| **Sub-label** | Muted Slate | `#a1a1aa` | Micro-tracked tagline |

---

## 3. Geometry & Grid Construction

The emblem is mathematically constructed on a **32x32 unit coordinate matrix**:
1. **The Vault Shield Hull:** Symmetrical parabolic spline apex at `(16, 2.5)` extending to shoulders at `(25.5, 5.5)`, descending through flanks to the bottom anchor apex at `(16, 29)`.
2. **Concentric Biometric Hash Ridges:** Three radial arc paths centered along the vertical axis:
   - Outer Ridge ($r = 10\text{ units}$): Outer biometric loop.
   - Middle Ridge ($r = 7\text{ units}$): Mid-layer cryptographic circuit.
   - Inner Ridge ($r = 4.5\text{ units}$): Core vault sanctum.
3. **Consensus Nodes:** 
   - Central proof-of-existence starburst node at `(16, 17)`.
   - Triad consensus status beacon at `(16, 7.5)` with dual emerald validator points at `(14.7, 7.8)` and `(17.3, 7.8)`.

---

## 4. Usage Rules & Clear Space

- **Clear Space:** Always maintain a minimum clear space of **$1\times$ the width of the shield emblem** around the logo lockup on all sides. No text, boundaries, or competing imagery may intrude into this exclusion zone.
- **Minimum Size:**
  - Full Combination Logo (`logo-primary.svg`): Minimum width **120px** digital.
  - App Icon (`app-icon-*.png`): Minimum **32px** digital.
  - Favicon (`favicon.svg`, `favicon-16x16.png`): Specifically hand-tuned for **16x16** and **32x32** browser tab displays.

---

## 5. Prohibited Usages (Do Not)

- ❌ **Do not stretch or distort** the aspect ratio of the logo or emblem under any circumstances.
- ❌ **Do not alter or substitute the gradient stops** (e.g., do not replace amber with red or purple).
- ❌ **Do not rotate** the shield emblem; it must always remain vertically upright.
- ❌ **Do not place the full-color logo over busy or low-contrast backgrounds**; use `logo-mono.svg` when placing over vibrant or photographic backgrounds.
- ❌ **Do not apply unapproved bevels or drop shadows** beyond the specified SVG filter parameters.

---

## 6. Directory Structure & File Manifest

```
brand-assets/
├── logo/
│   ├── logo-primary.svg         # Full color vector master (420x80)
│   ├── logo-primary-512.png     # Full color raster export (512x98)
│   ├── logo-mono.svg            # Single color monochrome vector (pure white)
│   └── logo-mono-512.png        # Single color raster export (512x98)
├── icon/
│   ├── app-icon.svg             # Master 1024x1024 vector app icon
│   ├── app-icon-1024.png        # iOS/macOS 1024x1024 master app store icon
│   ├── app-icon-512.png         # 512x512 app icon
│   └── app-icon-192.png         # 192x192 mobile icon
├── favicon/
│   ├── favicon.svg              # Modern high-contrast vector favicon (64x64)
│   ├── favicon-16x16.png        # 16x16 browser tab favicon
│   ├── favicon-32x32.png        # 32x32 retina / bookmark favicon
│   ├── favicon-48x48.ico        # Multi-layer Windows ICO file
│   ├── apple-touch-icon-180x180.png  # Apple iOS home screen touch icon
│   ├── android-chrome-192x192.png    # Android PWA home screen icon
│   └── android-chrome-512x512.png    # Android PWA splash screen icon
└── usage-guidelines.md          # Official brand specification (this file)
```

---

## 7. HTML Favicon & Web Implementation Snippet

```html
<!-- Modern Vector Favicon for Chrome, Safari, Firefox -->
<link rel="icon" type="image/svg+xml" href="/static/favicon.svg">

<!-- Standard PNG Favicons -->
<link rel="icon" type="image/png" sizes="32x32" href="/static/img/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/static/img/favicon-16x16.png">

<!-- Apple Touch Icon -->
<link rel="apple-touch-icon" sizes="180x180" href="/static/img/apple-touch-icon.png">

<!-- Progressive Web App Manifest -->
<link rel="manifest" href="/static/site.webmanifest">
<meta name="theme-color" content="#08090a">
```
