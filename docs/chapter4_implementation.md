# Chapter 4: Implementation

## 4.1 Introduction

This chapter presents the concrete implementation of the LASU Inventory Management System. It covers the project structure, database implementation, security implementation, each functional module's key code, the template and UI system, and testing. Code excerpts are included where they illustrate technically significant design decisions.

---

## 4.2 Project Structure

The project root is organised as follows:

```
lasu-ims/
├── lasu_ims/                   # Django project package
│   ├── settings/
│   │   ├── base.py             # Shared settings
│   │   ├── dev.py              # Development overrides (DEBUG=True)
│   │   └── prod.py             # Production overrides (HTTPS, security)
│   ├── urls.py                 # Root URL configuration
│   └── wsgi.py
├── accounts/                   # Custom user model, auth views, decorators
├── core/                       # Shared models, signals, template tags
├── dashboard/                  # Role-dispatched dashboard views
├── assets/                     # Asset CRUD, barcode/QR, PDF labels
├── requisitions/               # Requisition workflow
├── operations/                 # Issue, return, transfer
├── maintenance/                # Fault tracking
├── reports/                    # Stock report, audit log, exports
├── admin_panel/                # Superadmin: user/dept/settings management
├── templates/                  # HTML templates (mirrors app structure)
│   ├── base.html               # Master layout template
│   ├── partials/               # sidebar.html, topbar.html, pagination.html
│   ├── accounts/
│   ├── assets/
│   ├── dashboard/
│   ├── requisitions/
│   ├── operations/
│   ├── maintenance/
│   ├── reports/
│   └── admin_panel/
├── static/
│   ├── css/
│   │   ├── base.css            # Design tokens, reset, typography
│   │   ├── components.css      # Buttons, cards, tables, badges, forms
│   │   ├── layout.css          # App shell grid, sidebar, topbar
│   │   └── dashboard.css       # Login page, stat cards, charts
│   ├── js/
│   │   ├── theme.js            # Dark/light theme switcher
│   │   └── barcode-scan.js     # Camera-based barcode scanner
│   └── images/
│       └── lasu-logo.jpg       # Institution logo
├── media/                      # Uploaded/generated files (gitignored)
│   ├── barcodes/               # Generated barcode PNGs
│   └── qrcodes/                # Generated QR code PNGs
├── docs/                       # Project write-up chapters
├── .env                        # Environment variables (gitignored)
├── manage.py
└── requirements.txt
```

---

## 4.3 Environment Configuration

All sensitive and environment-specific settings are externalised to a `.env` file using `python-decouple`. The file is excluded from version control via `.gitignore`.

**.env (development example):**
```ini
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

**`lasu_ims/settings/base.py` (key excerpt):**
```python
from pathlib import Path
from decouple import config, Csv
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SECRET_KEY = config('SECRET_KEY')
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost', cast=Csv())

DATABASES = {
    'default': dj_database_url.parse(
        config('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True,
    )
}

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 1800  # 30 minutes

AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 0.25      # 15 minutes
AXES_LOCKOUT_TEMPLATE = 'accounts/lockout.html'
AXES_RESET_ON_SUCCESS = True
```

---

## 4.4 Custom User Model

Django's built-in `User` model was extended via `AbstractUser` to add institution-specific fields. Extending `AbstractUser` (rather than using a separate profile model) keeps user data in a single table and allows the ORM to use the custom model everywhere Django references a user.

**`accounts/models.py`:**
```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLES = [
        ('superadmin',    'Super Admin'),
        ('store_officer', 'Store Officer'),
        ('hod',           'Head of Department'),
        ('auditor',       'Auditor'),
        ('bursar',        'Bursar'),
    ]
    role           = models.CharField(max_length=20, choices=ROLES, default='hod')
    department     = models.ForeignKey(
        'core.Department', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='members'
    )
    phone          = models.CharField(max_length=20, blank=True)
    staff_id       = models.CharField(max_length=30, unique=True, blank=True, null=True)
    must_change_password = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"
```

`AUTH_USER_MODEL = 'accounts.User'` in `settings/base.py` tells Django to use this model throughout the project.

---

## 4.5 Role-Based Access Control Implementation

### 4.5.1 Decorators

A reusable `role_required` decorator enforces role checks at the view layer. Wrapping a view function with this decorator means that even if a user knows the URL, they receive an HTTP 403 Forbidden response unless their role is in the permitted list.

**`accounts/decorators.py`:**
```python
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required

def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.role not in roles:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

# Convenience aliases
def superadmin_required(view_func):
    return role_required('superadmin')(view_func)

def store_officer_required(view_func):
    return role_required('superadmin', 'store_officer')(view_func)
```

### 4.5.2 Data-Level Scoping

Role checks alone are insufficient where different users of the same role should see different subsets of data. HODs must only see their own department's assets. This is enforced in each view by filtering the queryset:

```python
@login_required
def asset_list(request):
    qs = Asset.objects.select_related('category', 'department', 'custodian')
    # ... apply user-submitted filters ...
    if request.user.role == 'hod' and request.user.department:
        qs = qs.filter(department=request.user.department)
    # ...
```

The same scoping is applied in the stock report, asset detail, and requisition detail views.

### 4.5.3 Permission Matrix

| View / Action | superadmin | store_officer | hod | auditor | bursar |
|---|:---:|:---:|:---:|:---:|:---:|
| Register / Edit / Import assets | ✓ | ✓ | — | — | — |
| Condemn asset | ✓ | — | — | — | — |
| Issue / Return / Transfer | ✓ | ✓ | — | — | — |
| Create requisition | ✓ | ✓ | ✓ | — | — |
| Approve / Reject requisition | ✓ | ✓ | — | — | — |
| Report / Update maintenance | ✓ | ✓ | — | — | — |
| View assets | ✓ (all) | ✓ (all) | ✓ (own dept) | ✓ (all) | ✓ (all) |
| Stock report | ✓ (all) | ✓ (all) | ✓ (own dept) | ✓ (all) | ✓ (all) |
| Audit log | ✓ | — | — | ✓ | — |
| Reconciliation | ✓ | ✓ | — | ✓ | — |
| Export (Excel / PDF) | ✓ | ✓ | — | ✓ | ✓ |
| User / Dept / Settings admin | ✓ | — | — | — | — |

---

## 4.6 Asset Module Implementation

### 4.6.1 Auto ID Generation

Asset IDs follow the format `LASU-YYYY-NNNNN`. The sequence resets each calendar year. Generation occurs in a `pre_save` signal:

```python
@receiver(pre_save, sender=Asset)
def set_asset_id(sender, instance, **kwargs):
    if not instance.asset_id:
        year = timezone.now().year
        last = Asset.objects.filter(
            asset_id__startswith=f'LASU-{year}-'
        ).order_by('-asset_id').first()
        seq = 1
        if last:
            try:
                seq = int(last.asset_id.split('-')[-1]) + 1
            except ValueError:
                pass
        instance.asset_id = f'LASU-{year}-{seq:05d}'
```

### 4.6.2 Barcode and QR Code Generation

Barcodes and QR codes are generated in a `post_save` signal triggered on first creation:

```python
@receiver(post_save, sender=Asset)
def generate_codes(sender, instance, created, **kwargs):
    if not created:
        return
    # Generate Code128 barcode
    import barcode
    from barcode.writer import ImageWriter
    bc = barcode.get('code128', instance.asset_id, writer=ImageWriter())
    buf = BytesIO()
    bc.write(buf, options={'write_text': False, 'module_height': 10})
    instance.barcode_image.save(
        f'barcode_{instance.asset_id}.png', ContentFile(buf.getvalue()), save=False
    )
    # Generate QR code
    import qrcode
    qr = qrcode.make(instance.asset_id)
    buf2 = BytesIO()
    qr.save(buf2, format='PNG')
    instance.qr_code_image.save(
        f'qr_{instance.asset_id}.png', ContentFile(buf2.getvalue()), save=False
    )
    # Use update() to avoid re-triggering the signal
    Asset.objects.filter(pk=instance.pk).update(
        barcode_image=instance.barcode_image,
        qr_code_image=instance.qr_code_image,
        barcode_number=instance.asset_id,
    )
```

### 4.6.3 Print Queue (Session-Based)

The print queue stores a list of Asset IDs in the user's server-side session. No database table is required:

```python
@login_required
def print_queue(request):
    if request.user.role not in ('superadmin', 'store_officer'):
        raise PermissionDenied
    queue = request.session.get('print_queue', [])
    if request.method == 'POST':
        action   = request.POST.get('action')
        asset_id = request.POST.get('asset_id')
        if action == 'add' and asset_id and asset_id not in queue:
            queue.append(asset_id)
        elif action == 'remove':
            queue = [x for x in queue if x != asset_id]
        elif action == 'clear':
            queue = []
        request.session['print_queue'] = queue
        return redirect(request.META.get('HTTP_REFERER', 'assets:print_queue'))
    assets = Asset.objects.filter(asset_id__in=queue) if queue else []
    return render(request, 'assets/print_queue.html', {'assets': assets})
```

### 4.6.4 Label PDF Generation

PDF label sheets are generated server-side using `xhtml2pdf`. A `link_callback` function resolves URL references in the HTML (for barcode/QR images and the LASU logo) to absolute filesystem paths, which `xhtml2pdf` requires to embed images:

```python
def _pdf_link_callback(uri, rel):
    if uri.startswith(settings.MEDIA_URL):
        return os.path.join(settings.MEDIA_ROOT, uri[len(settings.MEDIA_URL):])
    if uri.startswith(settings.STATIC_URL):
        rel_path = uri[len(settings.STATIC_URL):]
        for d in getattr(settings, 'STATICFILES_DIRS', []):
            path = os.path.join(str(d), rel_path)
            if os.path.isfile(path):
                return path
    return uri

def _render_label_pdf(request, assets):
    from xhtml2pdf import pisa
    assets_list = list(assets)
    if len(assets_list) % 2 == 1:
        assets_list.append(None)          # pad to even for 2-column layout
    label_rows = [assets_list[i:i+2] for i in range(0, len(assets_list), 2)]
    html = render(request, 'assets/label_pdf.html', {'label_rows': label_rows}).content.decode()
    buf = io.BytesIO()
    pisa.CreatePDF(html, dest=buf, link_callback=_pdf_link_callback)
    buf.seek(0)
    return buf
```

The `label_pdf.html` template uses a plain HTML table (CSS Grid is not supported by `xhtml2pdf`) to arrange labels in two columns per row across an A4 page.

---

## 4.7 Requisition Workflow Implementation

The requisition status follows a defined state machine:

```
draft ──► submitted ──► approved ──► fulfilled
                    └──► rejected
```

Status transitions are enforced in views — for example, only a `submitted` requisition can be approved:

```python
@login_required
def req_approve(request, pk):
    if request.user.role not in ('superadmin', 'store_officer'):
        raise PermissionDenied
    req = get_object_or_404(Requisition, pk=pk, status='submitted')
    if request.method == 'POST':
        req.status      = 'approved'
        req.reviewed_by = request.user
        req.reviewed_at = timezone.now()
        req.review_notes = request.POST.get('notes', '')
        req.save()
        AuditLog.objects.create(
            user=request.user,
            action=f'Approved requisition {req.requisition_id}',
            model_name='Requisition',
            object_id=str(req.pk),
            ip_address=_get_ip(request),
        )
        messages.success(request, f'Requisition {req.requisition_id} approved.')
        return redirect('requisitions:detail', pk=pk)
    return render(request, 'requisitions/approve.html', {'req': req})
```

`get_object_or_404(Requisition, pk=pk, status='submitted')` serves double duty: it returns 404 (not 403) if someone attempts to approve an already-approved or rejected requisition, preventing double-processing.

---

## 4.8 Maintenance Module Implementation

Maintenance records follow a three-state lifecycle: `pending → in_progress → completed`. The status update view also captures repair cost and notes on completion:

```python
@login_required
def maintenance_update(request, pk):
    if request.user.role not in ('superadmin', 'store_officer'):
        raise PermissionDenied
    log = get_object_or_404(MaintenanceLog, pk=pk)
    if request.method == 'POST':
        log.status              = request.POST.get('status', log.status)
        log.assigned_technician = request.POST.get('technician', log.assigned_technician)
        log.repair_notes        = request.POST.get('repair_notes', '')
        cost = request.POST.get('repair_cost', '').strip()
        if cost:
            log.repair_cost = Decimal(cost)
        if log.status == 'completed' and not log.completed_at:
            log.completed_at = timezone.now()
            # Mark the asset as no longer under repair
            log.asset.status = 'in_store'
            log.asset.save()
        log.save()
        # ...audit log...
        return redirect('maintenance:detail', pk=pk)
```

---

## 4.9 Reports Module Implementation

### 4.9.1 Stock Report with Role Filtering

The `_filter_assets` helper applies user-submitted GET filters. The stock report view applies an additional HOD department filter before aggregating the total value:

```python
@login_required
def stock_report(request):
    qs = _filter_assets(request).order_by('-created_at')
    if request.user.role == 'hod' and request.user.department:
        qs = qs.filter(department=request.user.department)
    total_value = qs.aggregate(v=Sum('purchase_cost'))['v'] or 0
    paginator = Paginator(qs, 25)
    page = paginator.get_page(request.GET.get('page'))
    # ...
```

### 4.9.2 Audit Log

The audit log view is restricted to superadmin and auditor. It queries `AuditLog` records with optional filters and paginates at 50 records per page:

```python
@login_required
def audit_log(request):
    if request.user.role not in ('superadmin', 'auditor'):
        raise PermissionDenied
    qs = AuditLog.objects.select_related('user').order_by('-timestamp')
    # ...filter by action text, username, date range...
    paginator = Paginator(qs, 50)
    return render(request, 'reports/audit_log.html', {'page_obj': paginator.get_page(...)})
```

### 4.9.3 Excel Export with openpyxl

The Excel export produces a styled `.xlsx` workbook. Headers are formatted with a dark background and white bold text; cells are auto-width; the top row is frozen for scrollability:

```python
@login_required
def export_excel(request):
    if request.user.role not in ('superadmin', 'auditor', 'store_officer', 'bursar'):
        raise PermissionDenied
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    qs = _filter_assets(request).order_by('asset_id')
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Stock Report'
    headers = ['Asset ID','Name','Category','Department','Status',
               'Condition','Custodian','Serial No.','Purchase Date','Purchase Cost (₦)','Location']
    header_fill = PatternFill(start_color='1a1d27', end_color='1a1d27', fill_type='solid')
    header_font = Font(bold=True, color='FFFFFF')
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.font = header_fill; cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center')
    ws.freeze_panes = 'A2'
    for row, asset in enumerate(qs, 2):
        ws.cell(row=row, column=1, value=asset.asset_id)
        # ... populate remaining columns ...
    buf = io.BytesIO()
    wb.save(buf); buf.seek(0)
    response = HttpResponse(buf.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="lasu_ims_stock_{ts}.xlsx"'
    return response
```

---

## 4.10 Audit Logging Implementation

Every view that performs a material action writes an `AuditLog` entry immediately after the action succeeds. This pattern is applied consistently across all modules:

```python
AuditLog.objects.create(
    user       = request.user,
    action     = f'Registered new asset {asset.asset_id} — {asset.name}',
    model_name = 'Asset',
    object_id  = str(asset.pk),
    ip_address = _get_ip(request),
)
```

The IP address helper respects reverse proxies by checking the `X-Forwarded-For` header first:

```python
def _get_ip(request):
    x = request.META.get('HTTP_X_FORWARDED_FOR')
    return x.split(',')[0].strip() if x else request.META.get('REMOTE_ADDR', '')
```

---

## 4.11 Template System Implementation

### 4.11.1 Template Inheritance

All application pages extend a single `base.html` master template, which provides the full HTML structure, CSS and JS includes, and the app shell (sidebar + topbar + main content area). Individual pages override named blocks:

```html
<!-- base.html (simplified) -->
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  {% block title %}LASU IMS{% endblock %}
  <link rel="stylesheet" href="{% static 'css/base.css' %}">
  <script src="{% static 'js/theme.js' %}"></script>
</head>
<body>
<div class="app-shell">
  {% include "partials/sidebar.html" %}
  <header class="topbar">{% include "partials/topbar.html" %}</header>
  <main class="main-content">
    {% block content %}{% endblock %}
  </main>
  <div class="sidebar-overlay" id="sidebar-overlay"></div>
</div>
{% block extra_js %}{% endblock %}
</body>
</html>
```

Login-related pages do **not** extend `base.html` — they are standalone pages with their own minimal HTML structure, since the app shell is only appropriate for authenticated users.

### 4.11.2 Custom Template Filters

Three custom filters are registered in `core/templatetags/ims_tags.py` and added to `TEMPLATES[0]['OPTIONS']['builtins']` so they are available in every template without explicit `{% load %}`:

```python
@register.filter
def in_list(value, arg):
    """Usage: {% if user.role|in_list:'superadmin,auditor' %}"""
    return value in [x.strip() for x in arg.split(',')]

@register.filter
def naira(value, decimals=None):
    """Usage: {{ value|naira }} → ₦150,000.00  |  {{ value|naira:0 }} → ₦150,000"""
    try:
        val = float(value)
        return f"₦{val:,.0f}" if str(decimals) == '0' else f"₦{val:,.2f}"
    except (ValueError, TypeError):
        return "—"
```

The `in_list` filter powers role-conditional rendering in the sidebar and throughout templates, replacing multiple chained `{% if role == '...' or role == '...' %}` checks.

### 4.11.3 Dark/Light Theme Switching

The theme system works without a page reload by toggling a `data-theme` attribute on the `<html>` element. The implementation in `static/js/theme.js` is structured in two phases:

```javascript
(function () {
  const STORAGE_KEY = 'lasu-ims-theme';
  const root = document.documentElement;

  function applyTheme(theme) {
    root.setAttribute('data-theme', theme);
    // update the icon SVG path inside #theme-icon
  }

  // Phase 1: runs immediately in <head> to prevent flash
  applyTheme(localStorage.getItem(STORAGE_KEY) || 'dark');

  // Phase 2: deferred until DOM is ready, to find the button
  document.addEventListener('DOMContentLoaded', function () {
    var btn = document.getElementById('theme-toggle');
    if (btn) {
      btn.addEventListener('click', function () {
        var next = (root.getAttribute('data-theme') || 'dark') === 'dark' ? 'light' : 'dark';
        localStorage.setItem(STORAGE_KEY, next);
        applyTheme(next);
      });
    }
  });
})();
```

Loading the script in `<head>` without `defer` means it runs before the browser paints, so the correct theme colours are applied from the very first frame.

---

## 4.12 Login Security Implementation

### 4.12.1 Account Lockout (django-axes)

`django-axes` is configured in `INSTALLED_APPS` and `MIDDLEWARE`. It monitors failed login attempts and temporarily locks accounts:

```python
AXES_FAILURE_LIMIT = 5        # lock after 5 failures
AXES_COOLOFF_TIME  = 0.25    # locked for 15 minutes (0.25 hours)
AXES_LOCKOUT_TEMPLATE = 'accounts/lockout.html'
AXES_RESET_ON_SUCCESS = True  # reset counter on successful login
```

When an account is locked, Django-axes short-circuits the authentication backend and renders the lockout template rather than the login form.

### 4.12.2 First-Login Password Change

On every authenticated request, a middleware-like check in `accounts/views.py` redirects users whose `must_change_password` is `True` to the password change page — regardless of which URL they attempted to access:

```python
@login_required
def password_change_forced(request):
    if not request.user.must_change_password:
        return redirect('dashboard:home')
    if request.method == 'POST':
        form = SetPasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            request.user.must_change_password = False
            request.user.save(update_fields=['must_change_password'])
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Password updated. Welcome to LASU IMS.')
            return redirect('dashboard:home')
    else:
        form = SetPasswordForm(request.user)
    return render(request, 'accounts/password_change_forced.html', {'form': form})
```

The redirect to this view is triggered in the `accounts:login` success handler: after authentication, if `user.must_change_password` is True, the user is sent to `accounts:password_change_forced` instead of `LOGIN_REDIRECT_URL`.

---

## 4.13 Dashboard Implementation

A single `dashboard:home` URL routes to a dispatcher view that selects the correct sub-template based on the user's role and computes role-specific context:

```python
ROLE_TEMPLATES = {
    'superadmin':    'dashboard/superadmin.html',
    'store_officer': 'dashboard/store_officer.html',
    'hod':           'dashboard/hod.html',
    'auditor':       'dashboard/auditor.html',
    'bursar':        'dashboard/bursar.html',
}

@login_required
def home(request):
    role     = request.user.role
    template = ROLE_TEMPLATES.get(role, 'dashboard/superadmin.html')
    context  = _build_context(request, role)
    return render(request, 'dashboard/base_dashboard.html', {
        **context, 'dashboard_template': template
    })
```

`dashboard/base_dashboard.html` extends `base.html` and uses `{% include dashboard_template %}` to render the role-specific content. This keeps all dashboards inside the common app shell without duplicating the shell in each dashboard template.

The `_build_context` function queries role-appropriate data:

- **Superadmin**: total assets, active/under_repair/condemned counts, total value, department-wise asset count and value, 10 most recent audit log entries, pending requisitions.
- **Store Officer**: today's issues/returns, pending requisitions, assets due for return, recent transactions.
- **HOD**: own department's asset count and breakdown, own department's pending/approved requisitions, recent transactions on own assets.
- **Auditor**: total assets, active/under_repair/condemned/lost counts, 10 most recent audit entries.
- **Bursar**: total asset value, condemned value, total asset count, assets added this year vs last year, asset value by department (for bar chart).

---

## 4.14 Seed Data Command

A custom management command `python manage.py seed_lasu` populates the database with test data for development and demonstration:

```python
# management/commands/seed_lasu.py
class Command(BaseCommand):
    help = 'Seed the database with test users, departments, categories, and assets.'

    def handle(self, *args, **kwargs):
        # Create departments
        depts = ['Faculty of Science', 'Faculty of Law', 'Registry', 'Bursary', 'ICT Centre']
        # Create categories
        cats = ['Computing', 'Furniture', 'Laboratory', 'Audio-Visual', 'Office Equipment']
        # Create one user per role
        roles = ['superadmin', 'store_officer', 'hod', 'auditor', 'bursar']
        # Create 20 sample assets with generated IDs, barcodes, and QR codes
```

Default credentials printed to the console allow immediate login and testing of all five roles.

---

## 4.15 CSV Bulk Import

The store officer can import multiple assets from a CSV file. The import view parses the file, creates `Asset` objects row by row (triggering the `post_save` signal for each, which generates barcodes and QR codes), and reports success/failure per row:

```python
reader = csv.DictReader(io.StringIO(decoded))
for i, row in enumerate(reader, start=2):
    try:
        cat, _  = AssetCategory.objects.get_or_create(name=row.get('category','General').strip())
        dept, _ = Department.objects.get_or_create(name=row.get('department','General').strip(), ...)
        asset   = Asset(name=row['name'].strip(), category=cat, department=dept, ...)
        asset.save()   # triggers auto-ID and barcode generation
        imported += 1
    except Exception as e:
        errors.append(f'Row {i}: {e}')
```

Expected CSV column headers: `name`, `category`, `department`, `status`, `condition`, `serial_number`, `supplier_name`, `purchase_cost`, `purchase_date`, `location`, `notes`.

---

## 4.16 System Testing

### 4.16.1 Manual Functional Testing

Each module was tested manually by logging in as each of the five roles and verifying:

| Test Case | Expected Result | Pass/Fail |
|---|---|---|
| Login with wrong password 5× | Account locked, lockout page shown | Pass |
| First-login user tries to access dashboard | Redirected to forced password change | Pass |
| HOD attempts to access `/assets/register/` | HTTP 403 Forbidden | Pass |
| HOD views asset list | Only own department's assets shown | Pass |
| HOD views stock report | Only own department's assets shown | Pass |
| Bursar attempts to access `/reports/audit-log/` | HTTP 403 Forbidden | Pass |
| Store officer registers asset | Asset created, barcode PNG and QR PNG generated in `/media/` | Pass |
| Store officer issues asset | Transaction record created, asset status → `issued` | Pass |
| Store officer transfers asset | Asset department updated, transaction recorded | Pass |
| Store officer condemns asset | Only superadmin button visible; HOD/store officer cannot condemn | Pass |
| HOD creates requisition | Status = `submitted`, visible to store officer | Pass |
| Store officer approves requisition | Status → `approved`, review notes saved | Pass |
| Export Excel | `.xlsx` file downloaded with all filtered assets | Pass |
| Export PDF | `.pdf` file downloaded with all filtered assets | Pass |
| Download label PDF (single asset) | PDF with barcode + QR images downloaded | Pass |
| Download label PDF (print queue) | PDF with all queued assets in 2-column layout downloaded | Pass |
| Dark/light theme toggle | Theme switches immediately, persists on page reload | Pass |
| Mobile: sidebar | Sidebar hidden by default, opens on hamburger tap | Pass |

### 4.16.2 Security Testing

| Test Case | Expected Result | Pass/Fail |
|---|---|---|
| Direct URL access to `/admin-panel/users/` as store officer | HTTP 403 Forbidden | Pass |
| POST to `/requisitions/1/approve/` as HOD | HTTP 403 Forbidden | Pass |
| SQL injection in search field (`' OR 1=1--`) | Django ORM parameterises query; no injection | Pass |
| CSRF attack (POST without token) | HTTP 403 Forbidden | Pass |
| Session replay after logout | Session invalidated; 302 redirect to login | Pass |

### 4.16.3 Database Migration Verification

```bash
python manage.py makemigrations accounts
python manage.py makemigrations core
python manage.py makemigrations
python manage.py migrate
python manage.py seed_lasu
```

All migrations applied cleanly in the correct order (`accounts` before `core`, since `core` models reference `accounts.User` via foreign keys).

---

## 4.17 Deployment Considerations

While the system is currently run locally for development, the following configuration changes are required for production deployment:

| Setting | Development Value | Production Value |
|---|---|---|
| `DEBUG` | `True` | `False` |
| `DATABASE_URL` | `sqlite:///db.sqlite3` | `postgresql://...` (NeonDB) |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | `lasu-ims.lasu.edu.ng` |
| `SECURE_SSL_REDIRECT` | (not set) | `True` |
| `SESSION_COOKIE_SECURE` | (not set) | `True` |
| `CSRF_COOKIE_SECURE` | (not set) | `True` |
| Static files | Dev server (`runserver`) | Whitenoise (already configured) |
| Media files | Local filesystem | Cloud storage (AWS S3 / Cloudinary) recommended |

The `prod.py` settings file contains these overrides, activated by setting `DJANGO_SETTINGS_MODULE=lasu_ims.settings.prod` in the production environment.
