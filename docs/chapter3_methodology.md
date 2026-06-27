# Chapter 3: Methodology

## 3.1 Introduction

This chapter describes the approach taken to develop the LASU Inventory Management System. It covers the software development methodology adopted, the requirements analysis process, system design decisions (architecture, database schema, data flow, and user interface), and the tools and technologies used. Together, these sections document the process by which identified problems were translated into a working system.

---

## 3.2 Software Development Methodology

### 3.2.1 Iterative and Incremental Development

LASU-IMS was developed using an **iterative and incremental** approach, drawing on Agile principles without the formal ceremony of a full Scrum implementation. The development was structured as a series of increments, each adding a functional module:

| Increment | Module Added | Key Deliverables |
|---|---|---|
| 1 | Project scaffold, accounts | Django project, custom User model, login/logout, first-login password change, role-based decorator |
| 2 | Core models | Asset, AssetCategory, Department, Transaction, AuditLog, Requisition, MaintenanceLog |
| 3 | Assets module | Registration, barcode/QR generation, print queue, CSV import, condemnation |
| 4 | Operations module | Issue, return, inter-departmental transfer, transaction history |
| 5 | Requisitions module | HOD creation, store officer approval/rejection, status workflow |
| 6 | Maintenance module | Fault reporting, technician assignment, cost recording, status update |
| 7 | Reports module | Stock report, audit log, reconciliation tool, Excel/PDF export |
| 8 | Admin panel | User CRUD, department CRUD, system settings |
| 9 | Dashboards | Role-specific dashboards for all five roles |
| 10 | UI/UX polish | CSS design system, dark/light theme, responsive layout |

This approach allowed the core asset management functionality to be working and testable early, with less-central modules added progressively. Each increment was verified against the requirements before proceeding to the next.

### 3.2.2 Rationale for Not Using Waterfall

The Waterfall model — in which all requirements are gathered, then all design done, then all implementation done, then all testing done — would have been unsuitable here. The institutional requirements for a university IMS evolved as the project progressed; for example, the specific data each role's dashboard should display became clearer only after the core modules were functional. An iterative approach accommodated this evolution naturally.

---

## 3.3 Requirements Analysis

### 3.3.1 Functional Requirements

Functional requirements describe what the system must do.

#### Authentication and User Management
- FR-01: The system shall authenticate users with a username and password.
- FR-02: The system shall lock accounts for 15 minutes after 5 consecutive failed login attempts.
- FR-03: New accounts shall require users to change their password on first login before accessing any other page.
- FR-04: Only the superadmin shall be able to create, edit, activate, and deactivate user accounts.
- FR-05: Each user account shall be assigned exactly one role from: `superadmin`, `store_officer`, `hod`, `auditor`, `bursar`.
- FR-06: HOD accounts shall be associated with exactly one department.

#### Asset Management
- FR-07: Authorised users (superadmin, store officer) shall be able to register new assets with: name, category, department, status, condition, serial number, supplier, purchase date, purchase cost, location, and notes.
- FR-08: The system shall automatically generate a unique Asset ID in the format `LASU-YYYY-NNNNN` on registration.
- FR-09: The system shall automatically generate a `Code128` barcode image and a QR code image for each registered asset.
- FR-10: Authorised users shall be able to add assets to a print queue and download a PDF of barcode/QR labels.
- FR-11: Only the superadmin shall be able to condemn an asset; condemnation shall require a written reason.
- FR-12: HODs shall only be able to view assets belonging to their own department.

#### Operations
- FR-13: Store officers shall be able to issue an asset to a named custodian, recording the transaction.
- FR-14: Store officers shall be able to record the return of an issued asset.
- FR-15: Store officers shall be able to transfer an asset from one department to another, recording both source and destination.
- FR-16: All operations (issue, return, transfer) shall be logged as `Transaction` records with a system-generated transaction ID.

#### Requisitions
- FR-17: HODs shall be able to create a requisition requesting specific assets for their department.
- FR-18: Store officers shall be able to approve or reject submitted requisitions.
- FR-19: Approved requisitions shall be fulfillable by the store officer; fulfilment shall update the requisition status.
- FR-20: Each requisition shall record its full status history.

#### Maintenance
- FR-21: Authorised users (superadmin, store officer) shall be able to report a maintenance issue for any asset.
- FR-22: Maintenance records shall capture: issue description, priority, reported date, assigned technician, and repair cost.
- FR-23: Store officers shall be able to update maintenance status (pending → in progress → completed) and record repair notes and cost.
- FR-24: Condemned assets shall be listed separately in a dedicated condemned-assets view.

#### Reports
- FR-25: Authorised users shall be able to generate a stock report filterable by status, category, department, and date range.
- FR-26: Superadmin and auditor shall be able to view the full system audit log, filterable by action text, user, and date range.
- FR-27: Superadmin, auditor, and store officer shall be able to use a reconciliation tool to scan an asset's barcode and flag discrepancies.
- FR-28: Superadmin, auditor, store officer, and bursar shall be able to export the stock report to Excel (`.xlsx`) and PDF.
- FR-29: HODs' stock report view shall be automatically scoped to their own department.

#### Dashboards
- FR-30: Each role shall see a dashboard tailored to their responsibilities on login, displaying relevant KPIs and recent activity.

### 3.3.2 Non-Functional Requirements

Non-functional requirements describe qualities the system must exhibit.

| ID | Requirement | Description |
|---|---|---|
| NFR-01 | **Security** | All state-changing operations require server-side role verification; secrets externalised; sessions expire after 30 minutes of inactivity. |
| NFR-02 | **Usability** | The UI must be operable by non-technical staff; forms must provide clear labels, validation messages, and feedback on success/error. |
| NFR-03 | **Performance** | Page load time for list views (paginated to 25 records) shall be under 2 seconds on a standard broadband connection. |
| NFR-04 | **Availability** | The system shall target 99% uptime in production, achieved through managed cloud hosting (NeonDB for the database, Whitenoise for static file serving). |
| NFR-05 | **Maintainability** | Each functional area is a separate Django application (`assets`, `requisitions`, etc.) with its own models, views, URLs, and templates, enabling independent modification. |
| NFR-06 | **Scalability** | The database design and query structure shall support up to 100,000 assets and 1,000 users without architectural change. |
| NFR-07 | **Auditability** | Every material user action shall be recorded in an audit log with actor, timestamp, affected object, and IP address. |
| NFR-08 | **Portability** | The database backend shall be switchable between SQLite (development) and PostgreSQL (production) via a single environment variable. |

---

## 3.4 System Design

### 3.4.1 System Architecture

LASU-IMS is a **Django monolith** — a single Django project containing nine interdependent applications. This architecture was chosen over a microservices approach for the following reasons:

- The application is a single-purpose institutional tool, not a platform requiring independent scaling of components.
- A monolith reduces operational complexity (one server, one deployment pipeline, one database connection).
- Django's app system provides sufficient internal separation of concerns without the network overhead of inter-service communication.

```
┌─────────────────────────────────────────────────────────┐
│                        Client Browser                    │
└───────────────────────────┬─────────────────────────────┘
                            │ HTTPS
┌───────────────────────────▼─────────────────────────────┐
│                    Django WSGI Application               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │ accounts │  │  assets  │  │ reports  │  │ admin_  │ │
│  │  + auth  │  │   +ops   │  │          │  │  panel  │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │requisit- │  │mainten-  │  │dashboard │  │  core   │ │
│  │  ions    │  │   ance   │  │          │  │ models  │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │
│                          │                               │
│                    Django ORM                            │
└───────────────────────────┬─────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────┐
│          PostgreSQL Database (NeonDB, production)        │
│              SQLite (development / local)                │
└─────────────────────────────────────────────────────────┘
```

Static files (CSS, JavaScript, images) are served by **Whitenoise**, a Python WSGI middleware that serves compressed, long-cached static files efficiently from the same process as the application — removing the need for a separate web server (e.g., Nginx) in the initial deployment phase.

Media files (barcode images, QR code images) are stored on the server's local filesystem under `MEDIA_ROOT` and served via Django's development media-serving mechanism (to be replaced by cloud storage, e.g., AWS S3, in a production-grade deployment).

### 3.4.2 Application Decomposition

The Django project `lasu_ims` contains the following applications:

| Application | Responsibility |
|---|---|
| `accounts` | Custom User model, login/logout views, password change, first-login enforcement, login rate limiting middleware integration |
| `core` | Shared models used across apps: `Asset`, `AssetCategory`, `Department`, `Transaction`, `AuditLog`, `Requisition`, `MaintenanceLog`; custom template tags (`ims_tags`) |
| `dashboard` | Role-dispatched dashboard views, per-role context computation |
| `assets` | Asset CRUD, barcode/QR generation, print queue, CSV bulk import, condemnation, label PDF generation |
| `requisitions` | Requisition creation, listing, detail, approval, rejection, fulfilment |
| `operations` | Issue, return, and transfer views; transaction history |
| `maintenance` | Fault reporting, maintenance detail, status update, condemned-asset list |
| `reports` | Stock report, audit log, reconciliation tool, Export Centre, Excel and PDF export |
| `admin_panel` | User management (CRUD), department management (CRUD), system settings — superadmin only |

Settings are split across `lasu_ims/settings/base.py` (shared), `dev.py` (development overrides), and `prod.py` (production overrides), following the Django settings-split pattern.

### 3.4.3 Database Schema (Entity-Relationship Description)

The database comprises the following primary entities and relationships:

#### User (`accounts_user`)
Extends Django's `AbstractUser`. Additional fields:
- `role` (CharField, choices: superadmin / store_officer / hod / auditor / bursar)
- `department` (ForeignKey → Department, nullable — not all roles are dept-scoped)
- `phone` (CharField)
- `staff_id` (CharField, unique)
- `must_change_password` (BooleanField — set True on creation, cleared on first-login password change)

#### Department (`core_department`)
- `name` (CharField, unique)
- `code` (CharField, unique — short abbreviation)
- `description` (TextField, optional)

#### AssetCategory (`core_assetcategory`)
- `name` (CharField, unique — e.g., "Computing", "Furniture")
- `description` (TextField, optional)

#### Asset (`core_asset`)
The central entity. Key fields:
- `asset_id` (CharField, PK — auto-generated `LASU-YYYY-NNNNN`)
- `name`, `description`, `notes`
- `category` (ForeignKey → AssetCategory)
- `department` (ForeignKey → Department)
- `status` (CharField, choices: in_store / issued / under_repair / transferred / condemned / lost)
- `condition` (CharField, choices: excellent / good / fair / poor)
- `serial_number`, `supplier_name`, `location_description`
- `purchase_date` (DateField), `purchase_cost` (DecimalField)
- `barcode_number` (CharField, unique — auto-generated)
- `barcode_image` (ImageField — stores generated PNG)
- `qr_code_image` (ImageField — stores generated PNG)
- `custodian` (ForeignKey → User, nullable)
- `created_by` (ForeignKey → User)
- `created_at`, `updated_at` (auto timestamps)

Asset ID generation: on `pre_save`, the model queries the database for the highest existing sequence number for the current year and assigns the next. If `LASU-2026-00020` is the last, the next is `LASU-2026-00021`.

Barcode/QR generation: on `post_save` (if newly created), `python-barcode` generates a Code128 PNG to `media/barcodes/`, and `qrcode` generates a QR PNG to `media/qrcodes/`.

#### Transaction (`core_transaction`)
Records every state-changing operation on an asset:
- `transaction_id` (CharField, unique — UUID-based)
- `asset` (ForeignKey → Asset)
- `transaction_type` (choices: issued / returned / transferred / condemned / maintenance_in / maintenance_out)
- `from_department`, `to_department` (ForeignKey → Department, nullable)
- `performed_by` (ForeignKey → User)
- `condition_before`, `condition_after`
- `notes`
- `created_at`

On each transaction, a `post_save` signal updates the parent `Asset`'s status field to stay in sync.

#### Requisition (`core_requisition`)
- `requisition_id` (auto-generated unique reference)
- `requested_by` (ForeignKey → User — must be an HOD)
- `department` (ForeignKey → Department)
- `items` (TextField — description of requested assets)
- `quantity`, `priority` (choices: low / medium / high / urgent)
- `status` (choices: draft / submitted / approved / rejected / fulfilled)
- `justification`
- `reviewed_by` (ForeignKey → User, nullable — set when approved/rejected)
- `reviewed_at`, `review_notes`
- `created_at`, `updated_at`

#### MaintenanceLog (`core_maintenancelog`)
- `asset` (ForeignKey → Asset)
- `issue_description` (TextField)
- `priority` (choices: low / medium / high / critical)
- `status` (choices: pending / in_progress / completed)
- `assigned_technician` (CharField)
- `repair_cost` (DecimalField, nullable)
- `repair_notes` (TextField)
- `reported_by` (ForeignKey → User)
- `reported_at`, `completed_at`

#### AuditLog (`core_auditlog`)
- `user` (ForeignKey → User, nullable — `None` for system events)
- `action` (TextField — human-readable description of the action)
- `model_name` (CharField — the model affected)
- `object_id` (CharField — the PK of the affected object)
- `ip_address` (CharField)
- `timestamp` (DateTimeField, auto)

AuditLog records are written manually in each view function after a material action is completed. The log is append-only by convention (no update or delete views exist for it).

**Entity-Relationship Summary:**

```
User ──< Transaction >── Asset ──< MaintenanceLog
 │                         │
 │                       AssetCategory
 │
 └──< Requisition >── Department ──< Asset
                                    Department ──< User (HODs)
```

### 3.4.4 Data Flow Diagrams

#### Level 0 (Context Diagram)

```
               ┌─────────────────────────┐
Staff Member ──►                         ├──► Audit Log
               │      LASU-IMS           │
Superadmin  ──►  (Inventory Management  ├──► Reports / Exports
               │       System)           │
               │                         ├──► Barcode / QR Labels
               └─────────────────────────┘
```

#### Level 1 — Asset Lifecycle Flow

```
[Store Officer]
      │
      ├── Register Asset ──► Auto-generate ID, barcode, QR ──► Asset DB
      │
      ├── Issue Asset ──► Create Transaction(issued) ──► Update Asset.status
      │
      ├── Return Asset ──► Create Transaction(returned) ──► Update Asset.status
      │
      ├── Transfer ──► Create Transaction(transferred) ──► Update Asset.department, status
      │
      └── Condemn ──► Create Transaction(condemned) ──► Update Asset.status = condemned

[HOD]
      │
      └── Create Requisition ──► status=submitted ──► Store Officer Approves/Rejects
                                                           │
                                                      status=approved/rejected
```

### 3.4.5 Use Case Summary

| Actor | Use Case |
|---|---|
| Superadmin | Create/edit/deactivate users; manage departments; manage categories; condemn assets; view all data; full report access |
| Store Officer | Register assets; issue/return/transfer; approve/reject requisitions; report/update maintenance; reconcile; export reports |
| HOD | View own department's assets; create requisitions; view own requisitions; view stock report (dept-scoped) |
| Auditor | View all assets; view audit log; use reconciliation tool; export reports |
| Bursar | View all assets; view financial dashboard (valuations, write-offs); export reports |

---

## 3.5 User Interface Design

### 3.5.1 Design Principles

The UI was designed to the following principles:

- **Clarity over decoration**: a neutral, functional interface that surfaces data clearly rather than decorative design that competes with content.
- **Role-appropriate navigation**: the sidebar only shows links the current user's role can access; attempting to access a URL directly still returns 403.
- **Consistent feedback**: every action that changes state shows a Django `messages` framework alert (success/warning/error) on the next page load.
- **Mobile-responsive**: CSS media queries adapt the layout for tablet and mobile use, with a slide-in sidebar on small screens.

### 3.5.2 Colour System and Theming

The system implements a CSS custom-property-based design token system, supporting two themes — dark (default) and light — switchable at runtime:

```css
[data-theme="dark"] {
  --color-bg: #0f1117;
  --color-surface: #1a1d27;
  --color-accent: #4f6ef7;
  --color-text-primary: #e8eaf2;
  /* ... */
}
[data-theme="light"] {
  --color-bg: #f4f5f9;
  --color-surface: #ffffff;
  --color-accent: #4f6ef7;
  --color-text-primary: #111827;
  /* ... */
}
```

The selected theme is persisted in `localStorage` and applied by an inline `<script>` in the `<head>` before the page body renders, preventing a flash of the wrong theme on page load.

### 3.5.3 Layout Architecture

The application shell uses **CSS Grid**:

```css
.app-shell {
  display: grid;
  grid-template-columns: 240px 1fr;   /* sidebar | content */
  grid-template-rows: 56px 1fr;        /* topbar | main */
  min-height: 100vh;
}
```

The sidebar spans both rows (`grid-row: 1 / -1`). The topbar occupies column 2, row 1. Main content occupies column 2, row 2.

---

## 3.6 Tools and Technologies

| Category | Tool / Library | Version | Purpose |
|---|---|---|---|
| Language | Python | 3.12 | Primary development language |
| Web Framework | Django | 5.x | MVC web application framework |
| Database (dev) | SQLite | 3.x | Local development database |
| Database (prod) | PostgreSQL | 15 (via NeonDB) | Production database |
| DB adapter | psycopg2-binary | 2.x | PostgreSQL driver for Django |
| Environment config | python-decouple | 3.x | Externalises settings to `.env` |
| DB URL parsing | dj-database-url | 2.x | Parses `DATABASE_URL` into Django DB config |
| Static files | whitenoise | 6.x | Serves static files from the Django process |
| Login throttling | django-axes | 6.x | Account lockout after repeated failed logins |
| Barcode generation | python-barcode | 0.15 | Generates Code128 PNG barcode images |
| QR code generation | qrcode | 7.x | Generates QR code PNG images |
| Pillow | Pillow | 10.x | Image processing (dependency of barcode/qrcode) |
| Excel export | openpyxl | 3.x | Generates `.xlsx` spreadsheet exports |
| PDF generation | xhtml2pdf | 0.2.x | Renders HTML templates to PDF |
| Frontend CSS/JS | Custom (no framework) | — | Bespoke CSS design system; vanilla JS |
| Font | Inter (Google Fonts) | — | Primary UI typeface |
| Version control | Git | — | Source code management |

---

## 3.7 Development Environment

- **Operating System**: Windows 11 Pro
- **Editor**: VS Code
- **Python Virtual Environment**: `venv` (standard library)
- **Activation**: `source venv/Scripts/activate` (Git Bash on Windows)
- **Local server**: `python manage.py runserver` on `http://127.0.0.1:8000`
- **Database**: SQLite (`db.sqlite3`) during development; environment variable `DATABASE_URL=sqlite:///db.sqlite3`
- **Seed data**: `python manage.py seed_lasu` — populates one user per role, sample departments, categories, and assets for testing

---

## 3.8 Summary

This chapter described the iterative development methodology, derived functional and non-functional requirements from the problem statement, presented the system architecture (Django monolith, nine apps, CSS Grid UI), documented the database schema (eight tables, their fields, and relationships), outlined the data flow and use cases, described the UI design principles and theme system, and listed all tools and technologies. These design decisions provide the foundation for the implementation described in Chapter 4.
