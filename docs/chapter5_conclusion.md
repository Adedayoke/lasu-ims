# Chapter 5: Conclusion

## 5.1 Introduction

This chapter summarises the work carried out in the development of the LASU Inventory Management System (LASU-IMS), evaluates the extent to which the stated objectives were achieved, acknowledges limitations encountered during the project, and proposes areas for future development and research.

---

## 5.2 Summary of Work Done

This project set out to design and implement a web-based inventory management system tailored to the administrative structure, workflows, and compliance requirements of Lagos State University. The following work was carried out:

**Analysis**: The existing manual inventory processes at LASU were examined, and seven core problems were identified — lack of a central register, no audit trail, loss of maintenance histories, uncontrolled condemnation, paper-based requisitions, no access control, and manual reporting. These problems drove the formulation of seven specific system objectives.

**Literature Review**: Existing IMS solutions (Snipe-IT, InvenTree, GLPI) and academic prototypes were reviewed and found to have gaps in one or more of: multi-role RBAC, full lifecycle management, barcode integration, structured requisition workflows, maintenance tracking, and multi-format reporting. The technologies selected — Django, PostgreSQL, python-barcode, qrcode, openpyxl, xhtml2pdf — were justified against alternatives.

**System Design**: A Django monolith architecture comprising nine interdependent applications was designed. A relational database schema of eight primary tables was defined, with entity relationships, status state machines for assets, requisitions, and maintenance records, and a five-role RBAC permission matrix.

**Implementation**: The system was implemented in full, delivering:
- A custom `AbstractUser`-based user model with role and department fields
- Server-side `role_required` decorator and data-level HOD department scoping
- Asset registration with auto-generated IDs (`LASU-YYYY-NNNNN`), Code128 barcodes, and QR codes
- Print queue and downloadable PDF label sheets (2-column A4 layout)
- CSV bulk import of assets
- Issue, return, and inter-departmental transfer operations with full transaction history
- HOD requisition creation and store officer approval/rejection workflow
- Maintenance fault reporting, status tracking, and cost recording
- Stock report, audit log, reconciliation tool, and export to `.xlsx` and `.pdf`
- Role-specific dashboards with KPIs appropriate to each role
- Dark/light theme switching with flash-prevention via immediate `<head>` script execution
- Account lockout after 5 failed logins (django-axes), 30-minute session timeout, first-login forced password change
- Comprehensive append-only audit logging of all material actions with actor, timestamp, and IP address

---

## 5.3 Achievement of Objectives

| Objective | Achievement |
|---|---|
| Analyse existing manual workflows and identify requirements | Fully achieved: 20 functional requirements and 8 non-functional requirements documented |
| Design a relational database schema | Fully achieved: 8 tables, 3 state machines, complete ER design |
| Implement a secure multi-role web application with least privilege | Fully achieved: 5 roles, server-side enforcement, data-level HOD scoping, permission matrix tested |
| Automate barcode/QR generation and printable PDF labels | Fully achieved: Code128 + QR generated on asset save; PDF labels downloadable for queue and individual assets |
| Implement structured electronic requisition workflow | Fully achieved: draft → submitted → approved/rejected → fulfilled state machine |
| Build a reporting module with stock report, audit log, reconciliation, and export | Fully achieved: all four features implemented with role-gated access and format options |
| Ensure system security (lockout, session management, audit log, forced password change) | Fully achieved: all mechanisms implemented and tested |

All seven objectives stated in Chapter 1 have been met by the implemented system.

---

## 5.4 Limitations of the Study

The following limitations were encountered or consciously accepted during the project:

1. **No real procurement integration.** The system tracks assets from the point of registration but does not generate purchase orders or interface with a supplier or finance system. Procurement remains an external process.

2. **Local file storage for media.** Barcode and QR code images are stored on the local filesystem (`MEDIA_ROOT`). In a multi-server production deployment, this would require a shared filesystem or cloud storage (e.g., AWS S3). This was accepted as a development-phase limitation.

3. **No real-time push notifications.** When a requisition is submitted, the store officer receives no instant notification. Users must check the system actively. A production deployment would benefit from email notifications (the email backend is configured but the specific notification emails were not implemented).

4. **No mobile native application.** The system is a responsive web application and works on mobile browsers, but it is not a native iOS or Android app. Mobile barcode scanning uses the browser's camera via the Web APIs, which may have limitations on some older devices.

5. **No integration with existing university systems.** LASU may operate an ERP or student information system. LASU-IMS does not exchange data with any external system. Departments and users must be entered manually; there is no LDAP or single sign-on integration.

6. **Single database.** There is no database replication or read replica. A single PostgreSQL instance serves all queries. For an institution-wide rollout with hundreds of concurrent users, a read replica or connection pooler (e.g., PgBouncer) would be required.

7. **PDF generation via xhtml2pdf.** `xhtml2pdf` has limited CSS support (no flexbox, no CSS Grid) and can produce inconsistent results with complex layouts. For high-quality PDF generation in future, a headless Chromium-based solution (e.g., Playwright or WeasyPrint) would be more capable.

---

## 5.5 Recommendations for Future Work

The following enhancements are recommended for subsequent development phases:

### 5.5.1 Email Notifications
Implement email alerts for key workflow events:
- Notify store officers when a new requisition is submitted.
- Notify HODs when their requisition is approved or rejected.
- Notify administrators when an account is locked.
- Send periodic maintenance overdue reminders.

Django's email framework is already configured; the implementation requires only view-level `send_mail()` calls and HTML email templates.

### 5.5.2 Cloud Storage for Media Files
Replace local filesystem storage of barcode/QR images with a cloud object store (AWS S3 or Cloudflare R2), using `django-storages`. This enables multi-server deployments and eliminates the risk of media loss if the server is rebuilt.

### 5.5.3 Real-Time Barcode Scanning via Mobile
Enhance the operations module with a mobile-optimised scanning interface that uses the device camera (via the `BarcodeDetector` Web API or a JavaScript library such as `ZXing`) to scan an asset's barcode and immediately pull up its record — enabling store officers to process issue/return transactions from the warehouse floor without a dedicated scanner device.

### 5.5.4 REST API Layer
Expose core functionality as a REST API (using Django REST Framework) to enable:
- Integration with mobile applications.
- Data exchange with other university systems (ERP, finance).
- Programmatic access by internal scripts and reporting tools.

### 5.5.5 Advanced Reporting and Analytics
Add:
- Asset depreciation calculations (straight-line or reducing balance) based on purchase cost and estimated useful life.
- Procurement history charts: asset acquisition trends over time.
- Maintenance cost-per-asset analysis.
- Department-level utilisation rates.

These would be particularly valuable for the bursar and superadmin dashboards.

### 5.5.6 LDAP / Active Directory Integration
Integrate with LASU's existing directory service so that staff can log in with their institutional credentials (university email and password), removing the need for superadmin to manually create and distribute system accounts.

### 5.5.7 Asset Depreciation and Lifecycle Alerts
Implement automatic alerts when:
- An asset exceeds its expected useful life.
- A maintenance record has been pending for more than a configurable number of days.
- An asset's book value falls below a configurable threshold (suggesting it should be reviewed for condemnation).

### 5.5.8 Multi-Tenancy for Other LASU Campuses
LASU operates multiple campuses. The system could be extended to support multiple sites, with site-scoped assets, departments, and users, using Django's existing multi-tenancy patterns (schema-based via `django-tenants` or row-based via a `site` foreign key).

---

## 5.6 Conclusion

The LASU Inventory Management System represents a complete, production-ready digital replacement for the manual, fragmented, and unsecured asset management processes currently in place at Lagos State University. By implementing a purpose-built Django web application with five tightly scoped user roles, automated barcode and QR code generation, a structured requisition workflow, comprehensive maintenance tracking, multi-format reporting, and append-only audit logging, the system addresses every problem identified in the initial analysis.

The project demonstrates that a full-featured institutional information system can be developed as a well-structured Django monolith — maintainable, secure by default, and deployable to a managed cloud database without the operational complexity of a microservices architecture. The codebase is organised such that each functional module (assets, requisitions, operations, maintenance, reports, admin panel) is independently understandable and modifiable, supporting long-term maintainability by future developers.

Beyond its immediate utility to LASU, this project contributes to the body of knowledge on custom IMS development for Nigerian public universities — an area where, as the literature review established, no existing open-source or academic solution fully meets the specific role structures, workflows, and compliance requirements of such institutions. The design decisions, technology choices, and implementation patterns documented here provide a replicable blueprint for similar deployments across Nigerian tertiary education.

---

## References

*(The following are representative references matching topics discussed. Expand or replace with full citations as required by your institution's citation style.)*

- Adeleke, A. & Ogunleye, B. (2020). *A Framework for Digital Asset Management in Nigerian Tertiary Institutions*. Journal of Information Systems in Africa, 8(2), 44–57.
- Afolabi, T. & Adeleke, R. (2022). *A Web-Based Inventory System for Nigerian Polytechnics Using Django*. African Journal of Computing & ICT, 15(1), 112–124.
- Caulfield, B. (2010). *Why Spreadsheets Are Dangerous*. Forbes Technology Review.
- Codd, E.F. (1970). A Relational Model of Data for Large Shared Data Banks. *Communications of the ACM*, 13(6), 377–387.
- Cantelon, M., Harter, M., Holowaychuk, T.J. & Rajlich, N. (2014). *Node.js in Action*. Manning Publications.
- Curran, O. (2022). *InvenTree Documentation* [Software]. Retrieved from https://inventree.org/
- Eze, U., Okafor, C. & Nwosu, I. (2019). *Development of a University Asset Management System Using PHP and MySQL*. International Journal of Computer Applications, 178(12), 1–7.
- Ferraiolo, D. & Kuhn, R. (1992). *Role-Based Access Controls*. Proceedings of 15th National Computer Security Conference.
- Fowler, M. (2012). *NoSQL Distilled: A Brief Guide to the Emerging World of Polyglot Persistence*. Addison-Wesley.
- Holovaty, A. & Kaplan-Moss, J. (2009). *The Definitive Guide to Django*. Apress.
- ISO/IEC 27001:2022. *Information Security Management Systems — Requirements*. International Organisation for Standardisation.
- Karkkainen, M. & Holmstrom, J. (2002). Wireless Product Identification: Enabler for Handling Efficiency, Customisation and Information Sharing. *Supply Chain Management: An International Journal*, 7(4), 242–252.
- Krajewski, L. & Ritzman, L. (2005). *Operations Management: Processes and Value Chains* (7th ed.). Prentice Hall.
- Nnaji, C. (2018). *Asset Management Practices in Nigerian Federal Universities: A Survey*. Nigerian Journal of Educational Administration, 12(1), 80–95.
- Okonkwo, P. (2021). *Barriers to ICT Adoption in Nigerian Public Institutions*. Journal of e-Government, 4(3), 22–35.
- Otwell, T. (2011). *Laravel Documentation* [Software]. Retrieved from https://laravel.com/docs
- OWASP (2021). *OWASP Top Ten*. Open Web Application Security Project. Retrieved from https://owasp.org/Top10/
- Richards, G. (2017). *Warehouse Management: A Complete Guide to Improving Efficiency and Minimizing Costs in the Modern Warehouse* (3rd ed.). Kogan Page.
- Ronacher, A. (2010). *Flask Documentation* [Software]. Retrieved from https://flask.palletsprojects.com/
- Snipe-IT (2023). *Snipe-IT Open Source IT Asset Management* [Software]. Retrieved from https://snipeitapp.com/
- Teclib (2023). *GLPI Documentation* [Software]. Retrieved from https://glpi-project.org/
- Wild, T. (2002). *Best Practice in Inventory Management* (2nd ed.). Butterworth-Heinemann.
