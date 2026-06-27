# Chapter 1: Introduction

## 1.1 Background of the Study

Inventory management is a critical administrative function in any large institution. Universities, as complex organisations hosting thousands of assets ranging from laboratory equipment and computing hardware to office furniture and library resources, face a particularly acute challenge in tracking, maintaining, and accounting for physical property over time. Lagos State University (LASU) — one of Nigeria's largest state-owned universities — manages assets distributed across multiple faculties, departments, and administrative units spread over an extensive campus.

Traditionally, asset tracking in Nigerian public universities has relied on paper-based ledgers, spreadsheets, or ad hoc manual records maintained by individual store officers. These approaches introduce significant risks: records become inconsistent, assets go untracked after transfers between departments, maintenance histories are lost, and reconciliation at audit time becomes laborious or impossible. The absence of a centralised, role-controlled system makes it difficult for auditors to verify asset counts, for bursars to reconcile asset valuations, and for management to make evidence-based procurement decisions.

The emergence of web-based management information systems has provided institutions worldwide with scalable, accessible, and secure alternatives to manual record-keeping. A well-designed Inventory Management System (IMS) digitises the full asset lifecycle — from initial registration and barcode tagging, through departmental assignment, issue, transfer, and maintenance, to eventual condemnation and write-off — and enforces access controls so that each staff member can only perform the actions appropriate to their role.

This project develops and implements the **LASU Inventory Management System (LASU-IMS)**: a full-stack web application purpose-built for Lagos State University's administrative structure, workflows, and compliance requirements.

---

## 1.2 Statement of the Problem

The following problems have been observed in the current manual asset management practice at Lagos State University:

1. **Lack of a centralised asset register.** Assets are recorded separately by each department, making it impossible for the central store to know the institution-wide count or value of any asset class at any point in time.

2. **No audit trail.** When an asset moves from one department to another, or when it is issued to a staff member, there is often no formal record of the transaction. Discrepancies discovered during audits cannot be traced to a responsible party.

3. **Maintenance records are not retained.** Repair histories are stored informally, so repeated failures of the same asset are not flagged, and there is no basis on which to decide between repair and replacement.

4. **Condemnation and write-off are uncontrolled.** Assets are sometimes removed from service without formal condemnation procedures, making the institution's books inaccurate.

5. **Requisition workflows are paper-based.** Heads of Department (HODs) submit paper requisitions that must be physically routed to the store for approval, causing delays and loss of paperwork.

6. **No role-based access control.** In the absence of a digital system, sensitive information — such as asset valuations and audit logs — is accessible to any staff member who can access the relevant cabinet.

7. **Reporting is manual and time-consuming.** Producing a stock report or financial valuation summary requires hours of manual aggregation from multiple sources, making real-time decision support impossible.

---

## 1.3 Aim and Objectives

### Aim
To design, develop, and deploy a web-based Inventory Management System for Lagos State University that digitises the full asset lifecycle, enforces role-based access control, and provides real-time reporting and audit capabilities.

### Objectives
1. To analyse the existing manual inventory workflows at LASU and identify specific functional requirements for a replacement system.
2. To design a relational database schema that accurately models assets, departments, users, transactions, requisitions, and maintenance records.
3. To implement a secure, multi-role web application using the Django web framework, enforcing least-privilege access at every endpoint.
4. To automate barcode and QR code generation for each registered asset and provide printable label output in PDF format.
5. To implement a structured requisition workflow allowing HODs to raise, and store officers to approve or reject, asset requests electronically.
6. To build a reporting module that produces stock reports, audit logs, reconciliation tools, and exportable Excel and PDF outputs.
7. To ensure system security through login rate-limiting, session management, forced password change on first login, and comprehensive audit logging of all system actions.

---

## 1.4 Scope of the Study

This system covers the following functional areas:

- **Asset Registration and Management**: creation, editing, categorisation, departmental assignment, and condemnation of assets.
- **Barcode and QR Code Generation**: automatic generation of unique barcodes and QR codes per asset, print queue management, and PDF label download.
- **Operations**: issue of assets to custodians, return, and inter-departmental transfer.
- **Requisitions**: creation by HODs, approval/rejection by store officers, and fulfilment tracking.
- **Maintenance**: fault reporting, technician assignment, cost recording, and status tracking.
- **Reports**: stock valuation reports, full audit log, physical reconciliation tool, and export to Excel (`.xlsx`) and PDF.
- **User Administration**: account creation, role assignment, departmental grouping, and forced first-login password change — managed exclusively by the superadmin.

The system does **not** cover:
- Procurement or purchasing workflows (raising purchase orders to suppliers).
- Financial accounting or integration with LASU's existing finance system.
- Physical asset tracking via GPS or RFID.
- Student-facing functionality.

---

## 1.5 Significance of the Study

The LASU-IMS addresses institutional needs at several levels:

- **Administrative**: gives store officers a single, authoritative register of all assets and their current status in real time.
- **Financial**: enables the bursar to view asset valuations, write-off totals (condemned assets), and generate financial-grade reports — directly supporting the annual audit.
- **Audit and Compliance**: every action taken in the system — login, asset creation, issue, transfer, condemnation — is automatically written to an immutable audit log with timestamps and IP addresses, satisfying internal audit requirements.
- **Departmental**: HODs gain visibility into their department's asset holdings without being able to modify records, and can raise electronic requisitions without paper.
- **Academic Contribution**: the project demonstrates the design and application of a multi-role, full-stack web system for a real institutional context, contributing to the body of knowledge on information systems in Nigerian public universities.

---

## 1.6 Definition of Terms

| Term | Definition |
|---|---|
| **Asset** | Any physical item owned by the institution that has a measurable value and is tracked over its useful life. |
| **Asset ID** | A unique system-generated identifier assigned to each asset on registration (e.g., `LASU-2026-00001`). |
| **Barcode** | A machine-readable 1-D visual representation of an asset's ID, generated using the `Code128` standard and printed on a physical label. |
| **QR Code** | A 2-D matrix barcode encoding the asset's ID and detail URL, scannable by a mobile camera. |
| **Custodian** | The staff member to whom an asset is currently assigned (issued). |
| **Department** | An organisational unit of the university (e.g., Faculty of Science, Registry, Bursary). |
| **Requisition** | A formal electronic request by an HOD for assets to be issued to their department. |
| **Transaction** | A recorded event in the asset's lifecycle: issue, return, transfer, or condemnation. |
| **RBAC** | Role-Based Access Control — a security model in which users are granted permissions based on their assigned role rather than individually. |
| **Audit Log** | An append-only record of every significant action performed in the system, including the actor, timestamp, and IP address. |
| **Condemnation** | The formal process of declaring an asset unserviceable and removing it from active inventory. |
| **Superadmin** | The highest-privilege system role, responsible for user management, department configuration, and system settings. |
| **HOD** | Head of Department — the academic or administrative lead of a university department, who can raise requisitions and view their own department's assets. |
| **Store Officer** | The staff member responsible for the physical store — they register assets, approve requisitions, and perform issue/return/transfer operations. |
| **Bursar** | The financial officer who reviews asset valuations and write-offs. |
| **Auditor** | The internal audit officer who reviews the audit log and performs physical reconciliation. |
| **Django** | A high-level Python web framework that promotes rapid development and clean, pragmatic design. |
| **ORM** | Object-Relational Mapper — a programming technique that converts data between the database and Python objects, used here via Django's built-in ORM. |
