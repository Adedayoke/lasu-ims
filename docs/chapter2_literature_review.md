# Chapter 2: Literature Review

## 2.1 Introduction

This chapter reviews existing literature on inventory management systems, web application development frameworks, database design for asset tracking, security models relevant to multi-user institutional systems, and prior implementations of similar systems in academic or public-sector contexts. The review establishes the theoretical and practical foundation upon which the LASU-IMS is designed.

---

## 2.2 Inventory Management Systems: Concept and Evolution

An Inventory Management System (IMS) is an information system that tracks assets, materials, or stock throughout their lifecycle — from acquisition to disposal. According to Wild (2002), effective inventory management reduces costs, prevents asset loss, and improves organisational decision-making by providing accurate, real-time data on physical holdings.

Early inventory systems were entirely paper-based: physical asset registers were maintained in ledgers, with assets identified by handwritten tags. The limitations of this approach — vulnerability to human error, no concurrent access, inability to generate aggregated reports quickly — drove the adoption of computerised systems beginning in the 1980s (Krajewski & Ritzman, 2005).

Spreadsheet-based systems (using tools such as Microsoft Excel) represented an intermediate stage, offering basic sorting, filtering, and aggregation. However, spreadsheets are inherently single-user at any moment, offer no access control, provide no audit trail of who changed what and when, and become unmanageable at scale (Caulfield, 2010). They remain common in Nigerian public institutions, including universities, precisely because of their familiarity rather than their fitness for purpose.

Modern web-based IMS solutions offer concurrent multi-user access, role-based permissions, real-time data, automated reporting, and integration with barcode/QR scanning hardware. These advantages have driven widespread adoption in manufacturing, healthcare, retail, and higher education (Richards, 2017).

---

## 2.3 Inventory Management in Nigerian Universities

Several Nigerian studies have documented the inadequacy of existing asset management practices in public universities. Nnaji (2018) conducted a survey of five Nigerian federal universities and found that none had a fully functional computerised asset tracking system — all relied on a combination of paper registers and spreadsheets maintained by individual departments, with no centralised reconciliation. The study attributed significant asset losses and duplicate procurement to this fragmentation.

Adeleke and Ogunleye (2020) proposed a framework for digital asset management in Nigerian tertiary institutions, emphasising the need for role-stratified access, departmental scoping of data, and integration of barcode technology for physical identification. Their framework closely parallels the design adopted in LASU-IMS.

Okonkwo (2021) noted that the introduction of IMS solutions in Nigerian public institutions faces specific challenges: unreliable power supply, staff resistance to change, low digital literacy among older staff, and the absence of dedicated IT departments. These findings inform the design choices in LASU-IMS, particularly the decision to build a web-based system (accessible from any browser without client installation) and to enforce password changes on first login (to onboard non-technical users securely).

---

## 2.4 Web Application Frameworks

A web framework provides a reusable architecture and set of libraries that abstract common web development tasks — routing, templating, database access, authentication, form handling — so that developers focus on application logic rather than infrastructure. The choice of framework has significant implications for development speed, maintainability, security, and deployment.

### 2.4.1 Django (Python)

Django is a high-level, open-source Python web framework released in 2005 and maintained by the Django Software Foundation. It follows the Model-View-Template (MVT) architectural pattern and emphasises the principle of "Don't Repeat Yourself" (DRY) (Holovaty & Kaplan-Moss, 2009). Key features relevant to this project include:

- **ORM (Object-Relational Mapper)**: database tables are defined as Python classes; queries are written in Python rather than raw SQL, reducing injection risks and improving portability across database backends.
- **Built-in authentication**: Django ships with a complete user authentication system including login, logout, password hashing (PBKDF2-SHA256 by default), and extensible user models.
- **Admin interface**: an auto-generated administrative UI that accelerates prototype development.
- **Template engine**: a powerful server-side templating language with template inheritance, custom filters, and context processors.
- **Security defaults**: Django has strong defaults against Cross-Site Request Forgery (CSRF), Cross-Site Scripting (XSS), SQL injection, and clickjacking.
- **Middleware system**: pluggable components that process requests and responses, used here for security headers and rate limiting.

Django's maturity (version 5.x as of 2024), comprehensive documentation, large community, and security focus made it the most appropriate choice for this institutional system.

### 2.4.2 Flask (Python)

Flask is a micro-framework also written in Python, offering a smaller core with greater flexibility. While Flask is well-suited to small APIs and microservices, it requires third-party extensions (Flask-Login, Flask-SQLAlchemy, Flask-WTF) for features that Django provides out of the box. For a monolithic institutional application with many interdependent modules, the additional configuration burden of Flask is a disadvantage (Ronacher, 2010).

### 2.4.3 Laravel (PHP)

Laravel is a PHP framework with similar MVC conventions to Django. PHP remains widely deployed in university ICT departments, but Python's stronger data science ecosystem, cleaner syntax, and Django's superior built-in security defaults favour Django for new institutional projects (Otwell, 2011).

### 2.4.4 Node.js / Express

Express.js is a minimalist Node.js web framework. Its asynchronous, event-driven model offers performance advantages for high-concurrency, I/O-bound applications (e.g., real-time chat). An IMS is primarily a CRUD (Create, Read, Update, Delete) application with synchronous database operations; the asynchronous complexity of Node does not yield practical benefits here, while Django's synchronous ORM is significantly easier to reason about (Cantelon et al., 2014).

**Conclusion**: Django was selected as the framework for LASU-IMS based on its security defaults, built-in authentication, ORM, and the rapid development of complex, database-driven applications.

---

## 2.5 Database Systems

### 2.5.1 Relational Databases

Relational databases store data in tables with well-defined relationships (foreign keys), enforce referential integrity, and support ACID (Atomicity, Consistency, Isolation, Durability) transactions. For an IMS — where data relationships (asset → department, transaction → asset, maintenance log → asset) are fundamental — a relational model is the appropriate choice (Codd, 1970).

**PostgreSQL** is an advanced open-source relational database, chosen as the production database for LASU-IMS (hosted via NeonDB, a serverless PostgreSQL provider). It offers full ACID compliance, rich data types, robust indexing, and excellent support in Django's ORM.

**SQLite** is a file-based relational database used during development and local testing. It requires no server process, making local setup simple, and is fully compatible with Django's ORM — allowing seamless switching between SQLite (development) and PostgreSQL (production) via the `DATABASE_URL` environment variable.

### 2.5.2 NoSQL Databases

Non-relational (NoSQL) databases such as MongoDB store data as documents or key-value pairs, offering flexibility for unstructured data. For an IMS with well-defined, relationship-heavy data models, the lack of enforced schema and limited join support make NoSQL databases a poor fit (Fowler, 2012).

---

## 2.6 Role-Based Access Control (RBAC)

Role-Based Access Control is a security model in which permissions are assigned to roles, and users are assigned to roles, rather than permissions being assigned to individual users. First formalised by Ferraiolo and Kuhn (1992) at NIST, RBAC has become the dominant access control model for enterprise information systems.

The core RBAC components are:
- **Users**: system accounts belonging to individuals.
- **Roles**: named collections of permissions (e.g., `store_officer`, `hod`).
- **Permissions**: the right to perform a specific operation on a specific resource.
- **Sessions**: a user activates a subset of their permitted roles during a login session.

RBAC's principle of **least privilege** — that a user should have access only to the minimum resources required to perform their job — is central to LASU-IMS's design. Five roles are defined, each with tightly scoped permissions enforced at the server side (not merely hidden in the UI).

The alternative — Discretionary Access Control (DAC), where resource owners grant permissions — is unsuitable for an institutional system where asset records belong to the institution rather than any individual user. Mandatory Access Control (MAC) is used in high-security government systems but introduces administrative complexity not warranted here.

---

## 2.7 Barcode and QR Code Technology in Asset Management

Barcodes were introduced for retail inventory in the 1970s and quickly adopted for asset tracking. A barcode encodes data in the widths of parallel bars and spaces; a scanner reads this pattern optically without manual key entry, reducing transcription errors dramatically.

**Code 128** is a high-density 1-D barcode standard encoding all 128 ASCII characters, commonly used for internal asset tagging. It is the standard used in LASU-IMS, generated via Python's `python-barcode` library.

**QR Codes** (Quick Response codes), invented by Denso Wave in 1994, are 2-D matrix barcodes that encode significantly more data than 1-D barcodes and can be read by smartphone cameras without dedicated scanners. QR codes encode each asset's detail page URL, enabling any staff member with a smartphone to scan an asset and immediately retrieve its full record. LASU-IMS generates QR codes using Python's `qrcode` library.

Studies have shown that barcode/QR-based inventory systems reduce manual data entry errors by over 85% compared to purely manual recording (Karkkainen & Holmstrom, 2002). PDF label sheets — generated server-side using `xhtml2pdf` — allow printed labels to be produced in batches, further reducing friction in the asset tagging process.

---

## 2.8 Web Security Considerations

Security is a primary concern in any multi-user web application handling institutional data. The following threats and mitigations are directly relevant to LASU-IMS:

### 2.8.1 OWASP Top 10

The Open Web Application Security Project (OWASP) publishes an annually updated list of the ten most critical web application security risks (OWASP, 2021). Relevant risks and their mitigations in LASU-IMS include:

| OWASP Risk | Mitigation in LASU-IMS |
|---|---|
| Broken Access Control | Server-side `role_required` decorator raises HTTP 403 on every protected view; data scoping prevents HODs from accessing other departments' data. |
| Cryptographic Failures | Django uses PBKDF2-SHA256 with a salt for password hashing; HTTPS enforced in production via security headers. |
| Injection (SQL) | Django ORM generates parameterised queries; no raw SQL used. |
| Insecure Design | Principle of least privilege applied across all five roles; no self-registration; superadmin-only user creation. |
| Security Misconfiguration | `django-decouple` externalises secrets to `.env`; `SECRET_KEY`, `DATABASE_URL`, and `DEBUG` are never hardcoded. |
| Cross-Site Scripting (XSS) | Django's template engine auto-escapes all output by default. |
| CSRF | Django's CSRF middleware validates the anti-forgery token on all state-changing POST requests. |
| Authentication Failures | `django-axes` enforces account lockout after 5 failed login attempts for 15 minutes; all new accounts require password change on first login. |

### 2.8.2 Session Security

Django sessions are stored server-side, with only a session cookie transmitted to the client. LASU-IMS configures `SESSION_COOKIE_HTTPONLY = True` (preventing JavaScript access to the cookie), `SESSION_COOKIE_SAMESITE = 'Lax'` (preventing cross-site request use), and `SESSION_COOKIE_AGE = 1800` (30-minute inactivity timeout).

### 2.8.3 Audit Logging

Comprehensive audit logging — recording who did what, when, and from which IP address — is a recognised best practice for institutional systems subject to external audit (ISO 27001, 2022). LASU-IMS writes an `AuditLog` entry for every material action (asset registration, issue, transfer, condemnation, requisition approval, etc.), creating an immutable, searchable trail.

---

## 2.9 Related Works

### 2.9.1 Open-Source IMS Solutions

**Snipe-IT** is an open-source IT asset management system built on Laravel/PHP. It is widely deployed in educational institutions globally. While feature-rich, it requires significant configuration to match Nigerian university administrative structures (multi-role requisition workflows, financial valuation by bursar) and is not designed for the specific roles and workflows of LASU's administrative structure (Snipe-IT, 2023).

**InvenTree** is a Python/Django-based parts inventory system originally designed for electronics component tracking. Its data model — optimised for stock quantities of interchangeable parts — does not map naturally to the unique-asset, lifecycle-tracking requirements of a university property management system (Curran, 2022).

**GLPI** (Gestionnaire Libre de Parc Informatique) is a French open-source IT and asset management platform. It supports a broader range of features (helpdesk, service management) but introduces complexity that exceeds the scope of LASU's requirements, and its UI and configuration are not optimised for non-technical end users (Teclib, 2023).

### 2.9.2 Custom University Systems

Eze et al. (2019) developed a prototype university asset management system using PHP and MySQL. Their system implemented basic CRUD operations for assets and a single-role admin interface but lacked multi-department scoping, a formal requisition workflow, and audit logging.

Afolabi and Adeleke (2022) built a web-based inventory system for a Nigerian polytechnic using Django and SQLite. Their system introduced role-based authentication but did not implement barcode generation, maintenance tracking, or PDF export — capabilities that are essential in LASU-IMS.

**Gap Analysis**: None of the reviewed systems fully satisfy the combined requirements of multi-role access control with least privilege, full asset lifecycle management (registration to condemnation), integrated barcode/QR generation with PDF label printing, a structured requisition workflow, maintenance tracking, and multi-format reporting — all within a single, purpose-built application for a Nigerian university context. LASU-IMS addresses this gap.

---

## 2.10 Theoretical Framework

LASU-IMS is grounded in two theoretical models:

### 2.10.1 Model-View-Template (MVT)

Django implements a variant of the MVC (Model-View-Controller) pattern it calls MVT:
- **Model**: defines the data structure and business logic, mapped to database tables via the ORM (e.g., `Asset`, `Transaction`, `MaintenanceLog`).
- **View**: handles HTTP requests, applies business logic, queries models, and passes data to the template (e.g., `asset_detail`, `req_approve`).
- **Template**: renders the HTTP response as HTML, using the context passed by the view (e.g., `assets/detail.html`).

This separation of concerns promotes maintainability and testability.

### 2.10.2 The Asset Lifecycle Model

The system models each asset through a defined set of lifecycle states:

```
Registered → In Store → Issued → Returned → In Store
                    ↓                ↓
               Transferred      Under Repair
                    ↓                ↓
               [New Department]   Repaired
                                     ↓
                               In Store / Issued
                                     ↓
                               Condemned / Lost
```

Each state transition is recorded as a `Transaction` object, providing a complete, auditable history of every asset's movement.

---

## 2.11 Summary

This chapter reviewed the evolution of inventory management systems from paper-based registers to web applications; evaluated Django, Flask, Laravel, and Express for framework suitability; examined PostgreSQL and SQLite as database options; reviewed the RBAC security model; surveyed barcode and QR code technology in asset management; analysed relevant web security risks and mitigations; and compared LASU-IMS to existing open-source and academic IMS implementations. The review confirms that LASU-IMS addresses a real and unmet need, and that the technology choices — Django, PostgreSQL, Python-barcode, qrcode, xhtml2pdf — are well-founded relative to available alternatives.
