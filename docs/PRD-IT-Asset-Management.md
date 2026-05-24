# Product Requirements Document
## IT Asset Management System

| Field | Detail |
|---|---|
| **Product Name** | IT Asset Management System |
| **Version** | 1.0.0 |
| **Author** | Bagues |
| **Date** | May 2026 |
| **Status** | In Development |
| **Stack** | Flask (Python), Bootstrap, Jinja2, fpdf2 |

---

## 1. Overview

### 1.1 Problem Statement

IT departments in hospital environments often manage a large and diverse inventory of hardware and software assets — from servers and workstations to medical peripherals and licensed software. Without a centralized system, asset tracking is commonly done via spreadsheets, which are error-prone, hard to audit, and unable to surface warranty expiration or procurement timelines proactively.

This application provides IT staff with a dedicated, web-based tool to manage the full lifecycle of IT assets: from procurement and registration through deployment, borrowing, and retirement.

### 1.2 Goals

- Provide a single source of truth for all IT assets in the organization
- Reduce time spent locating asset records and warranty information
- Enable tracking of asset borrowing and returns by staff
- Generate formal PDF reports for audit and procurement purposes

### 1.3 Non-Goals (Out of Scope — v1.0)

- Integration with ERP or finance systems (e.g. SAP, Odoo)
- Mobile application
- Automated warranty expiry email notifications
- Multi-branch / multi-department support
- User role management beyond a single admin role

---

## 2. Users

### 2.1 Primary User

**IT Staff / Teknisi**

The sole user group for v1.0. They are responsible for registering assets, managing loans, and producing reports. They are assumed to be technically proficient and work from a desktop browser.

> Future versions may add IT Manager read-only dashboards and non-IT staff borrowing portals.

---

## 3. Features & Requirements

### 3.1 Asset Management (CRUD)

**User Story:**
> As an IT staff member, I want to add, view, edit, and delete asset records so that I always have an accurate and up-to-date inventory.

**Functional Requirements:**

| ID | Requirement |
|---|---|
| F-01 | Staff can create a new asset record with: name, category, brand/model, serial number, condition, location, purchase date |
| F-02 | Staff can view a paginated list of all assets with search and filter by category and condition |
| F-03 | Staff can edit any field of an existing asset |
| F-04 | Staff can delete an asset record (with confirmation dialog) |
| F-05 | Each asset has a unique system-generated Asset ID |

---

### 3.2 Borrowing & Return

**User Story:**
> As an IT staff member, I want to record when an asset is borrowed and returned so that I know the current location and availability of each asset.

**Functional Requirements:**

| ID | Requirement |
|---|---|
| F-06 | Staff can create a borrowing record: borrower name, department, borrow date, expected return date |
| F-07 | An asset marked as "borrowed" is visually distinguished in the asset list |
| F-08 | Staff can record the return of a borrowed asset, including actual return date and condition notes |
| F-09 | A borrowing history log is kept per asset |
| F-10 | Staff can view a list of all currently active (unreturned) loans |

---

### 3.3 PDF Report Generation

**User Story:**
> As an IT staff member, I want to export asset data as a PDF report so that I can submit documentation to management or use it during audits.

**Functional Requirements:**

| ID | Requirement |
|---|---|
| F-11 | Staff can generate a PDF report of the full asset inventory |
| F-12 | Staff can generate a PDF filtered by category, condition, or date range |
| F-13 | PDF includes: report title, generation date, asset table, and total asset count |
| F-14 | PDF uses consistent organizational branding (logo, color palette, typography) |

---

### 3.4 Warranty & Procurement Tracking

**User Story:**
> As an IT staff member, I want to record warranty and procurement details per asset so that I can anticipate upcoming expirations and plan replacements.

**Functional Requirements:**

| ID | Requirement |
|---|---|
| F-15 | Each asset can store: vendor name, purchase price, procurement date, warranty duration, warranty expiry date |
| F-16 | The asset detail page displays warranty status: Active, Expiring Soon (≤ 30 days), or Expired |
| F-17 | A dedicated warranty/procurement section lists assets sorted by nearest expiry date |
| F-18 | Assets with expired or soon-expiring warranties are visually highlighted |

---

## 4. Non-Functional Requirements

| ID | Requirement |
|---|---|
| NF-01 | The application must load any page within 2 seconds under normal network conditions |
| NF-02 | The UI must be responsive and usable on desktop browsers (Chrome, Firefox) at minimum |
| NF-03 | All data must be persisted in a relational database (SQLite for dev, PostgreSQL for production) |
| NF-04 | PDF generation must complete within 5 seconds for up to 500 asset records |
| NF-05 | The application must not expose raw error tracebacks to the browser in production |

---

## 5. UI / Design

- **Framework:** Bootstrap + custom CSS design system
- **Aesthetic:** Luxury dark theme, warm gold accent (`#b49964`), dark backgrounds
- **Typography:** Cormorant Garamond (branding/headers), DM Sans (body/UI text)
- **Principles:** Clean information hierarchy, minimal clutter, professional data tables

---

## 6. Technical Architecture

```
Flask App (Python)
├── Routes / Controllers
├── Models (SQLAlchemy ORM)
│   ├── Asset
│   ├── BorrowRecord
│   └── Procurement
├── Templates (Jinja2 + Bootstrap)
└── Services
    └── ReportService (fpdf2)
```

- **Backend:** Flask, SQLAlchemy
- **Frontend:** Jinja2 templates, Bootstrap, custom CSS
- **PDF:** fpdf2
- **Database:** SQLite (development), PostgreSQL (production)
- **Deployment:** Linux server / Docker container

---

## 7. Success Metrics

Since this is an internal tool (v1.0), success is measured qualitatively:

- All CRUD operations work without data loss
- Borrowing records accurately reflect asset availability
- PDF reports are legible, branded, and contain correct data
- Warranty statuses are correctly computed and displayed

---

## 8. Future Roadmap (Post v1.0)

| Priority | Feature |
|---|---|
| High | Email/notification alerts for expiring warranties |
| High | IT Manager read-only dashboard with summary stats |
| Medium | Asset QR code label generation |
| Medium | Multi-role authentication (Admin, Viewer) |
| Low | REST API for integration with other hospital systems |
| Low | Bulk asset import via CSV/Excel |

---

## 9. Appendix

### Glossary

| Term | Definition |
|---|---|
| Asset | Any IT hardware or software tracked by the IT department |
| Borrowing Record | A log entry capturing the temporary assignment of an asset to a person |
| Warranty Status | Computed field indicating whether an asset's warranty is Active, Expiring Soon, or Expired |
| Procurement | The purchase event associated with an asset, including vendor and cost data |

---

*This document reflects the scope of IT Asset Management System v1.0 and is intended for personal portfolio documentation.*
