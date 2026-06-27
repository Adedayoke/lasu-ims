# LASU Inventory Management System

A production-ready inventory management system for Lagos State University.

## Quick Start

### 1. Clone / navigate to the project
```bash
cd lasu-ims
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Copy `.env.example` to `.env` and fill in your NeonDB URL:
```bash
copy .env.example .env   # Windows
cp .env.example .env     # Mac/Linux
```

Edit `.env`:
```
SECRET_KEY=your-long-random-secret-key
DATABASE_URL=postgresql://user:password@ep-xxx.neon.tech/lasu_ims?sslmode=require
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. Run migrations
```bash
python manage.py migrate
```

### 6. Seed the database
```bash
python manage.py seed_lasu
```

### 7. Collect static files (for production)
```bash
python manage.py collectstatic
```

### 8. Start the development server
```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000

## Default Credentials (after seeding)

| Role | Username | Password |
|---|---|---|
| Super Admin | admin | Admin@1234 |
| Store Officer | storekeeper | Test@1234 |
| Head of Dept | hod_eng | Test@1234 |
| Auditor | auditor1 | Test@1234 |
| Bursar | bursar1 | Test@1234 |

> All accounts except the store officer will be prompted to change their password on first login.

## Architecture

- **Framework**: Django 5.x (Python 3.11+)
- **Database**: PostgreSQL via NeonDB
- **PDF Export**: xhtml2pdf
- **Excel Export**: openpyxl
- **Barcode**: python-barcode + Pillow
- **QR Code**: qrcode[pil]
- **Auth protection**: django-axes (login throttling)
- **Static files**: WhiteNoise

## URL Structure

| URL | Description |
|---|---|
| `/` | Redirects to dashboard |
| `/login/` | Login page |
| `/dashboard/` | Role-specific dashboard |
| `/assets/` | Asset registry |
| `/operations/issue/` | Issue an asset |
| `/operations/return/` | Return an asset |
| `/requisitions/` | Requisition workflow |
| `/maintenance/` | Maintenance log |
| `/reports/stock/` | Stock report |
| `/reports/audit-log/` | Audit trail |
| `/admin-panel/users/` | User management (superadmin) |
| `/lasu-control/` | Django admin (emergency) |

## Security Notes

- CSRF protection on all forms
- Session timeout: 30 minutes
- Login lockout: 5 failed attempts → 15 minute cooldown
- Role-based access control enforced server-side on every view
- All state-changing actions logged to AuditLog
- Passwords: minimum 8 chars, 1 uppercase, 1 number
