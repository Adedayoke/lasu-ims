# LASU Inventory Management System — Claude Code Build Prompt
---

## Project overview

Build a complete, production-ready **Inventory Management System for Lagos State University (LASU)**. This is a Django monolith — the backend and frontend live in one project. Django serves all pages using its template engine. No React, no Vue, no separate frontend repo.

The system digitises the full lifecycle of physical university assets: procurement → registration → issuance → maintenance → condemnation. It replaces paper-based processes (Bin Cards, Store Issue Vouchers) with a barcode-driven, role-aware web application.

---

## Tech stack

| Layer | Choice |
|---|---|
| Language | Python 3.11+ |
| Framework | Django 5.x |
| Database | PostgreSQL via **NeonDB** (connect using `DATABASE_URL` env var with `psycopg2-binary`) |
| Templating | Django templates |
| Styling | Plain CSS (SCSS compiled via `django-compressor` or flat `.css` files — no Tailwind, no Bootstrap) |
| Barcode generation | `python-barcode` + `Pillow` (Code 128 + QR via `qrcode` library) |
| PDF export | `WeasyPrint` |
| Excel export | `openpyxl` |
| Auth | Django's built-in `auth` + custom user model |
| Environment | `python-decouple` for `.env` management |
| Static files | Django `staticfiles` |

---

## Design language — critical, read carefully

The UI must look like a **modern, professional enterprise dashboard** — clean, data-dense, confidence-inspiring. Think Linear, Vercel dashboard, or Stripe. Not a student project, not Bootstrap defaults.

Apply these rules strictly:

### Colour palette
```
--color-bg:         #0f1117        /* page background — near black */
--color-surface:    #1a1d27        /* card / panel background */
--color-surface-2:  #22263a        /* elevated surface, hover states */
--color-border:     #2e3347        /* subtle border */
--color-border-strong: #404660     /* emphasis border */
--color-accent:     #4f6ef7        /* primary action — indigo blue */
--color-accent-hover: #3a57e8
--color-success:    #22c55e
--color-warning:    #f59e0b
--color-danger:     #ef4444
--color-text-primary:   #f1f3f9
--color-text-secondary: #8b92a9
--color-text-muted:     #565d75
```

Dark theme by default. Provide a CSS variable–based light theme toggle (stored in `localStorage`) as a nice-to-have after core features.

### Typography
- Font: `Inter` from Google Fonts (weights 400, 500, 600)
- Base: 14px / 1.6 line height
- Headings: 500 weight, not bold
- Labels and table headers: 11px, 500 weight, letter-spacing 0.06em, `--color-text-secondary`

### Layout
- Fixed left sidebar (240px wide) for navigation
- Top bar (56px) with page title, breadcrumb, and user avatar/role badge
- Main content area with 24px padding
- Cards use 12px border-radius, `--color-surface` bg, `--color-border` border (0.5px or 1px)
- No drop shadows — borders do the separation work
- Tables: no zebra striping. Use a subtle hover highlight (`--color-surface-2`) on rows instead
- Stat/metric cards: icon left, large number, muted label below
- Status badges: pill shape, soft background tint of the status colour, text in the darker shade

### Sidebar navigation groups
```
OVERVIEW
  - Dashboard

ASSETS
  - Asset registry
  - Register new asset
  - Barcode print queue

OPERATIONS
  - Requisitions
  - Issuance
  - Returns

MAINTENANCE
  - Maintenance log
  - Condemned assets

REPORTS
  - Stock report
  - Audit log
  - Export centre

ADMIN (admin/superuser only)
  - Users
  - Departments
  - Settings
```

Active nav item: accent-coloured left border (3px), accent text, subtle accent background tint.

---

## Custom user model

Create a custom user model from the start (`accounts` app). Do not use Django's default `User` directly.

```python
class User(AbstractUser):
    role = CharField(choices=ROLE_CHOICES)
    department = ForeignKey('Department', null=True, blank=True)
    phone = CharField(max_length=20, blank=True)
    staff_id = CharField(max_length=50, blank=True, unique=True)
    is_active = BooleanField(default=True)
```

### Roles and what they can do

| Role | Permissions |
|---|---|
| `superadmin` | Everything including user management and system settings |
| `store_officer` | Register assets, issue items, process returns, print barcodes |
| `hod` | Submit and approve requisitions for their department, view their dept assets |
| `auditor` | View all assets and transactions, run reconciliation scans, export reports |
| `bursar` | View asset valuation dashboard and all reports, no write access |

Enforce permissions using Django's `@login_required`, `@permission_required`, and a custom `role_required` decorator. Never just check roles in templates — always enforce server-side.

---

## Database models

### `core` app — main models

```python
Department
  name, code, faculty, hod (FK User), created_at

AssetCategory
  name, description, depreciation_rate (decimal)

Asset
  asset_id (auto, LASU-YYYY-XXXXX format)
  name, description
  category (FK AssetCategory)
  department (FK Department)
  custodian (FK User, nullable)
  status = CHOICES: active | under_repair | condemned | in_store | lost
  condition = CHOICES: new | good | fair | poor
  purchase_date, purchase_cost (decimal)
  supplier_name
  barcode_number (unique, auto-generated)
  barcode_image (ImageField)
  qr_code_image (ImageField)
  serial_number
  location_description (free text, e.g. "Room 204, Engineering Block A")
  notes
  created_by (FK User)
  created_at, updated_at

Requisition
  req_number (auto, REQ-YYYY-XXXXX)
  requested_by (FK User)
  department (FK Department)
  status = CHOICES: draft | submitted | approved | rejected | fulfilled
  priority = CHOICES: low | normal | urgent
  notes
  approved_by (FK User, nullable)
  approved_at (nullable)
  created_at, updated_at

RequisitionItem
  requisition (FK)
  asset_category (FK AssetCategory)
  quantity_requested
  quantity_approved (nullable)
  purpose (text)

Transaction
  transaction_id (auto, TXN-YYYY-XXXXX)
  asset (FK Asset)
  transaction_type = CHOICES: issued | returned | transferred | condemned | repaired
  from_department (FK Department, nullable)
  to_department (FK Department, nullable)
  from_custodian (FK User, nullable)
  to_custodian (FK User, nullable)
  condition_before, condition_after
  notes
  performed_by (FK User)
  created_at

MaintenanceLog
  asset (FK Asset)
  issue_description
  reported_by (FK User)
  assigned_technician (text)
  status = CHOICES: reported | in_progress | completed | cancelled
  repair_cost (decimal, nullable)
  repair_notes
  reported_at, completed_at (nullable)

AuditLog
  user (FK User)
  action (text — e.g. "Issued asset LASU-2026-00142 to Dr. Adeola")
  model_name, object_id
  ip_address
  timestamp
```

Auto-log every create/update/delete to `AuditLog` using Django signals or a custom save mixin. Capture the user's IP address on every write.

---

## App structure

```
lasu_ims/               ← Django project root
  settings/
    base.py
    development.py
    production.py
  urls.py
  wsgi.py

accounts/               ← Custom user model, login, profile
core/                   ← All main models (Asset, Department, Transaction, etc.)
dashboard/              ← Dashboard views per role
assets/                 ← Asset registry, barcode generation, print queue
requisitions/           ← Requisition creation, approval workflow
operations/             ← Issuance, returns, transfers
maintenance/            ← Maintenance log, condemnation
reports/                ← Stock reports, audit log viewer, PDF/Excel export
admin_panel/            ← User management, department management, settings

static/
  css/
    base.css            ← CSS variables, reset, typography
    layout.css          ← Sidebar, topbar, main content grid
    components.css      ← Buttons, badges, cards, tables, forms, modals
    dashboard.css       ← Dashboard-specific stat cards and charts
  js/
    sidebar.js          ← Toggle, active state
    barcode-scan.js     ← Handle USB scanner input (keypress listener)
    theme.js            ← Light/dark toggle
    tables.js           ← Client-side search/filter on tables

templates/
  base.html             ← Shell: sidebar + topbar + content block
  partials/
    sidebar.html
    topbar.html
    pagination.html
    confirm_modal.html
  accounts/
  dashboard/
  assets/
  requisitions/
  operations/
  maintenance/
  reports/
  admin_panel/
```

---

## Key features to implement in full

### 1. Authentication
- Custom login page (not Django admin style — styled to match the dark dashboard)
- "Forgot password" flow (use Django's built-in password reset with email backend)
- Session timeout after 30 minutes of inactivity (JS-based warning + Django session config)
- First-login password change enforcement
- Login attempt throttling: lock account for 15 minutes after 5 failed attempts (use `django-axes` or implement manually)

### 2. Asset registry
- List view: searchable, filterable by status / category / department / custodian
- Pagination (25 per page)
- Asset detail page showing full history (all transactions, maintenance logs)
- Register new asset form with live barcode preview
- Edit asset (with audit trail of what changed)
- Bulk import via CSV (template downloadable)
- Auto-generate `asset_id` in format `LASU-{YEAR}-{5-digit-sequence}` on save
- Auto-generate barcode number and render barcode image on save using `python-barcode`
- Also generate a QR code (using `qrcode` library) that encodes the asset detail URL

### 3. Barcode print queue
- Store officers add assets to a print queue
- Print queue page renders all barcodes + QR codes in a print-optimised layout
- "Print labels" button triggers `window.print()` with a CSS `@media print` stylesheet that hides the sidebar/topbar and formats labels cleanly
- Label format: asset name, asset ID, barcode, QR code, department

### 4. Requisition workflow
- HODs or store officers create requisitions listing what items are needed
- Submitted requisitions appear in the store officer's approval queue
- Store officer (or superadmin) can approve with quantity adjustments or reject with reason
- Approved requisitions create an issuance task in the operations queue
- Status timeline shown on requisition detail page (Draft → Submitted → Approved → Fulfilled)

### 5. Issuance and returns
- Issue page: scan or search asset barcode → select receiving department and custodian → confirm
- USB barcode scanner support: listen for rapid keypress input ending in Enter (standard HID scanner behaviour) and auto-populate the asset search field
- Return page: scan barcode → record condition → confirm
- Transfer: move asset between departments (creates two Transaction records)
- All operations update `Asset.status`, `Asset.custodian`, `Asset.department` immediately

### 6. Maintenance log
- Report an asset for maintenance from the asset detail page or from the maintenance list
- Log tracks: issue description, assigned technician, repair cost, status updates
- When repair is complete, asset status reverts to `active`
- Condemn asset: requires reason + superadmin confirmation. Sets status to `condemned`, removes custodian, logs transaction

### 7. Role-based dashboards
Each role sees a different dashboard on login:

**Store officer dashboard:**
- Total assets in store, total issued, total under repair
- Recent transactions (last 10)
- Pending requisitions awaiting action
- Low stock alert (categories with < 5 items in store)

**HOD dashboard:**
- Their department's assets (count by status)
- Assets assigned to staff in their dept
- Their department's submitted/pending requisitions

**Auditor dashboard:**
- System-wide asset totals by status
- Recent audit log entries
- Quick-scan reconciliation tool (scan barcode → see if asset is where the DB says it is)

**Bursar dashboard:**
- Total asset value (sum of purchase costs)
- Asset value by faculty/department (bar chart using Chart.js — the only JS chart library allowed)
- Assets added this year vs last year
- Condemned asset value (write-offs)

**Superadmin dashboard:**
- All of the above
- User activity summary
- System health: last backup timestamp placeholder, total users, active sessions count

### 8. Reports and export
- Stock report: filterable by date range, department, category, status
- Export to PDF (WeasyPrint — styles a print-friendly version of the filtered table)
- Export to Excel (openpyxl — proper headers, column widths, freeze top row)
- Audit log: searchable by user, action, date range — paginated, no export needed
- All exports are generated server-side and streamed as file downloads

### 9. Reconciliation tool (for auditors)
- Auditor scans a barcode
- System looks up the asset and shows: expected location vs last known location, custodian, status
- Auditor can flag a discrepancy (creates an AuditLog entry with type `discrepancy`)
- Discrepancy report exportable as PDF

---

## Security requirements — implement all of these

1. **CSRF protection** — Django's built-in `{% csrf_token %}` on every form. Never disable.
2. **SQL injection** — Use Django ORM exclusively. No raw SQL. If raw SQL is ever needed, use parameterised queries only.
3. **XSS** — Django's auto-escaping is on. Never use `| safe` unless the content is explicitly generated server-side and not user input.
4. **Authentication on every view** — Every view (except login and password reset) must be wrapped in `@login_required`. Use `LoginRequiredMixin` on class-based views.
5. **Authorisation** — Every view checks the user's role server-side. A store officer navigating to `/admin/users/` must get a 403, not just a redirect.
6. **Password policy** — Enforce via Django validators: minimum 8 chars, at least one number, at least one uppercase. Configure in `AUTH_PASSWORD_VALIDATORS`.
7. **Session security** — `SESSION_COOKIE_HTTPONLY = True`, `SESSION_COOKIE_SAMESITE = 'Lax'`, `SESSION_EXPIRE_AT_BROWSER_CLOSE = False`, `SESSION_COOKIE_AGE = 1800` (30 min).
8. **HTTPS headers** — `SECURE_BROWSER_XSS_FILTER = True`, `X_FRAME_OPTIONS = 'DENY'`, `CONTENT_NOSNIFF = True`. In production: `SECURE_SSL_REDIRECT = True`, `HSTS` headers.
9. **File uploads** — Barcode and QR images are system-generated only, not user-uploaded. If CSV import is added, validate file type strictly (check MIME type and extension).
10. **Sensitive data in env** — `SECRET_KEY`, `DATABASE_URL`, `EMAIL_HOST_PASSWORD` must live in `.env` only, loaded via `python-decouple`. Never hardcode.
11. **Admin URL** — Change the default `/admin/` URL to `/lasu-control/` in `urls.py`.
12. **Audit everything** — Every state-changing action (create, update, delete, login, logout, failed login) writes to `AuditLog`.

---

## NeonDB connection

```python
# settings/base.py
from decouple import config
import dj_database_url

DATABASES = {
    'default': dj_database_url.parse(
        config('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True,
    )
}
```

`.env` file (create this, never commit it):
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@ep-xxx.neon.tech/lasu_ims?sslmode=require
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## URL structure

```
/                           → redirect to /dashboard/
/login/                     → accounts:login
/logout/                    → accounts:logout
/password-reset/            → accounts:password_reset

/dashboard/                 → dashboard:home (role-aware)

/assets/                    → assets:list
/assets/register/           → assets:register
/assets/<id>/               → assets:detail
/assets/<id>/edit/          → assets:edit
/assets/<id>/barcode/       → assets:barcode_image (serves PNG)
/assets/print-queue/        → assets:print_queue
/assets/import/             → assets:csv_import

/requisitions/              → requisitions:list
/requisitions/new/          → requisitions:create
/requisitions/<id>/         → requisitions:detail
/requisitions/<id>/approve/ → requisitions:approve
/requisitions/<id>/reject/  → requisitions:reject

/operations/issue/          → operations:issue
/operations/return/         → operations:return
/operations/transfer/       → operations:transfer
/operations/history/        → operations:history

/maintenance/               → maintenance:list
/maintenance/report/        → maintenance:report
/maintenance/<id>/          → maintenance:detail
/maintenance/<id>/update/   → maintenance:update
/assets/<id>/condemn/       → assets:condemn

/reports/stock/             → reports:stock
/reports/audit-log/         → reports:audit_log
/reports/reconciliation/    → reports:reconciliation
/reports/export/pdf/        → reports:export_pdf
/reports/export/excel/      → reports:export_excel

/admin-panel/users/         → admin_panel:users
/admin-panel/users/new/     → admin_panel:user_create
/admin-panel/departments/   → admin_panel:departments
/admin-panel/settings/      → admin_panel:settings

/lasu-control/              → Django admin (for emergency DB access only)
```

---

## CSS architecture — write this carefully

**`base.css`** — CSS custom properties on `:root`, CSS reset, body font setup, scrollbar styling.

**`layout.css`** — The shell:
```css
.app-shell { display: grid; grid-template-columns: 240px 1fr; grid-template-rows: 56px 1fr; min-height: 100vh; }
.sidebar { grid-row: 1 / -1; }
.topbar { grid-column: 2; }
.main-content { grid-column: 2; overflow-y: auto; padding: 24px; }
```

**`components.css`** — Reusable components. Write these properly:
- `.btn`, `.btn-primary`, `.btn-secondary`, `.btn-danger`, `.btn-ghost`
- `.badge`, `.badge-success`, `.badge-warning`, `.badge-danger`, `.badge-info`, `.badge-neutral`
- `.card`, `.card-header`, `.card-body`, `.card-footer`
- `.stat-card` (metric display cards for dashboard)
- `.data-table` (full-width, hover rows, sticky header)
- `.form-group`, `.form-label`, `.form-control`, `.form-select`, `.form-error`
- `.modal-overlay`, `.modal` (CSS-only show/hide via class toggle from JS)
- `.alert`, `.alert-success`, `.alert-warning`, `.alert-danger`
- `.pagination`
- `.timeline` (for asset history and requisition status trail)
- `.empty-state` (icon + heading + subtext for empty lists)
- `.sidebar-nav`, `.sidebar-nav-group`, `.sidebar-nav-item`, `.sidebar-nav-item.active`
- `.topbar-breadcrumb`, `.user-chip` (avatar circle + name + role badge)
- `.scan-input` (large styled input for barcode scanner focus)

---

## Barcode scanner UX

In the Issue, Return, and Reconciliation pages, implement a scan input that captures USB barcode scanner input:

```javascript
// barcode-scan.js
const scanInput = document.querySelector('.scan-input');
if (scanInput) {
  let buffer = '';
  let lastKeyTime = 0;

  document.addEventListener('keypress', (e) => {
    const now = Date.now();
    if (now - lastKeyTime > 100) buffer = ''; // reset if gap too long
    lastKeyTime = now;

    if (e.key === 'Enter' && buffer.length > 3) {
      scanInput.value = buffer;
      scanInput.dispatchEvent(new Event('change'));
      buffer = '';
      // trigger HTMX or form submit here
    } else {
      buffer += e.key;
    }
  });
}
```

When a valid barcode is scanned, auto-submit the search and display the asset details inline below (using a small `fetch()` call to an API endpoint that returns an HTML partial).

---

## Initial data and setup

Create a `management command`: `python manage.py seed_lasu` that:
1. Creates 5 departments: Engineering, Sciences, Administration, Library, ICT Unit
2. Creates one superadmin user: `admin@lasu.edu.ng` / `Admin@1234` (force password change on first login)
3. Creates one user per role for testing
4. Creates 10 sample asset categories (Computers, Furniture, Lab Equipment, etc.)
5. Creates 20 sample assets spread across departments

---

## Requirements file

```
Django>=5.0
psycopg2-binary
dj-database-url
python-decouple
Pillow
python-barcode
qrcode[pil]
WeasyPrint
openpyxl
django-axes
whitenoise
```

---

## What to build first (suggested order)

1. Project scaffold + settings split + NeonDB connection verified
2. Custom user model + all roles + login/logout pages (styled)
3. Core models + migrations
4. Base template shell (sidebar, topbar, layout CSS, component CSS)
5. Asset registry (list, register, detail, edit)
6. Barcode generation on asset save
7. Dashboard views per role
8. Issuance and returns with barcode scan input
9. Requisition workflow
10. Maintenance log + condemnation
11. Reports + PDF/Excel export
12. Audit log viewer
13. User and department management (superadmin)
14. Seed command
15. Security hardening pass (review all views for auth + role checks)

---

## Final notes for Claude Code

- Write real, working code. No placeholder comments like `# TODO: implement this`.
- Every form must have server-side validation with proper error messages shown in the template.
- Every destructive action (delete, condemn, deactivate user) must have a confirmation modal.
- Django messages framework for flash notifications — style them as `.alert` components in the base template.
- The system should be fully usable without JavaScript for core actions (forms POST normally). JS enhances but doesn't gate.
- `python manage.py check --deploy` should pass with no critical warnings before handoff.
- Include a `README.md` with setup instructions: clone → create `.env` → `pip install -r requirements.txt` → `migrate` → `seed_lasu` → `runserver`.