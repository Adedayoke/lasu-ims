# AI Chapter Generation Prompts
## LASU Inventory Management System — Project Write-Up

**How to use each prompt:**
1. Copy the full prompt for the chapter you want to generate.
2. Open your AI assistant (Claude, ChatGPT, etc.).
3. Paste the prompt, then attach the corresponding chapter markdown file from this `docs/` folder.
4. The AI will generate the complete, formatted chapter.

**Corresponding files:**
| Chapter | Prompt below | Attach this file |
|---|---|---|
| Chapter 1 | Prompt 1 | `chapter1_introduction.md` |
| Chapter 2 | Prompt 2 | `chapter2_literature_review.md` |
| Chapter 3 | Prompt 3 | `chapter3_methodology.md` |
| Chapter 4 | Prompt 4 | `chapter4_implementation.md` |
| Chapter 5 | Prompt 5 | `chapter5_conclusion.md` |

**Global formatting rules (already embedded in each prompt, listed here for reference):**
- Font: Times New Roman, size 12 throughout
- Line spacing: Double-spaced body text
- Paragraph spacing: No extra space between paragraphs; indent first line of each paragraph 0.5 inch
- Headings: Heading 1 (chapter title), Heading 2 (main sections e.g. 1.1), Heading 3 (subsections e.g. 1.1.1)
- Referencing: APA 7th Edition — in-text citations and a reference list at the end of each chapter
- Tables and figures: numbered per chapter (Table 1.1, Figure 3.1, etc.), captioned above tables and below figures
- Page margins: 1 inch on all sides

---

---

## PROMPT 1 — Chapter 1: Introduction

```
You are an academic writing assistant helping to produce a formal undergraduate/postgraduate 
project report. The attached file contains the full structured content for Chapter 1 
(Introduction) of a software engineering project titled:

"Design and Implementation of a Web-Based Inventory Management System for Lagos State 
University (LASU-IMS)"

Your task is to write Chapter 1 in full academic prose, using every section and data point 
in the attached file. Do not summarise or omit any section. Expand each bullet point and 
heading into well-developed paragraphs suitable for a final-year project report.

FORMATTING REQUIREMENTS — apply these exactly:
- Font: Times New Roman, 12pt, for all body text, headings, captions, and table content.
- Line spacing: Double-spaced throughout.
- Paragraph style: First line of each paragraph indented 0.5 inch; no blank lines between 
  paragraphs within a section.
- Chapter title ("Chapter 1: Introduction"): format as Heading 1.
- Section titles (e.g. "1.1 Background of the Study"): format as Heading 2.
- Sub-section titles (e.g. "1.1.1 ..."): format as Heading 3.
- Do not use bullet points in the final output — convert all lists into flowing prose or 
  numbered lists where appropriate.
- Any table must be: numbered (Table 1.1, Table 1.2 ...), captioned above the table in 
  bold ("Table 1.1: Title of Table"), and formatted with clear borders.
- Referencing: APA 7th Edition. Add in-text citations where claims are made about 
  existing practices, institutions, or technology. Add a "References" section at the very 
  end of the chapter listing all cited works in APA 7 format, alphabetically sorted.
- The definition of terms section should be presented as a formatted table (Term | Definition).
- Page margins: 1 inch on all sides.

CONTENT INSTRUCTIONS:
- Write in formal, third-person academic English throughout.
- The background section should clearly establish the context of inventory management in 
  Nigerian universities before introducing LASU specifically.
- The statement of the problem must present each problem as a distinct, numbered point 
  followed by explanatory prose.
- The aims and objectives section must distinguish clearly between the single overarching 
  aim and the numbered list of specific, measurable objectives.
- The scope section must clearly distinguish what the system covers from what it 
  deliberately excludes.
- The significance section should address each stakeholder group (administrative, 
  financial, audit, departmental, academic) separately.
- Minimum length: 2,500 words for the full chapter (excluding the reference list and 
  definitions table).

Begin the output with "Chapter 1: Introduction" formatted as Heading 1.
```

---

---

## PROMPT 2 — Chapter 2: Literature Review

```
You are an academic writing assistant helping to produce a formal undergraduate/postgraduate 
project report. The attached file contains the full structured content for Chapter 2 
(Literature Review) of a software engineering project titled:

"Design and Implementation of a Web-Based Inventory Management System for Lagos State 
University (LASU-IMS)"

Your task is to write Chapter 2 in full academic prose using every section in the attached 
file as your structural guide. Expand each section into well-developed paragraphs with 
properly cited academic sources.

INTERNET RESEARCH INSTRUCTION (IMPORTANT):
You have access to the internet. You MUST use it to:
1. Find real, verifiable academic references for every major claim in this chapter.
2. Verify that every source you cite actually exists — check the author, title, journal/
   publisher, year, volume, issue, and page numbers where applicable.
3. Only use references published between 2006 and 2026 (within the last 20 years). 
   Do NOT cite anything published before 2006. If a foundational concept (e.g. Codd's 
   relational model) requires a classic reference, supplement it with a recent secondary 
   source that discusses it.
4. Prioritise peer-reviewed journal articles, conference papers, and published textbooks. 
   Software documentation (Django, Flask, PostgreSQL, etc.) may be cited as online 
   references with access dates.
5. For claims about Nigerian universities specifically, search for journal articles from 
   Nigerian journals such as: African Journal of Computing & ICT, Journal of Information 
   and Communication Technology (JICT), International Journal of Computer Applications, 
   and similar.
6. Before including any reference, verify its existence. Do not fabricate or hallucinate 
   citations. If you cannot verify a specific source, use a verified alternative or state 
   that a citation is needed.

FORMATTING REQUIREMENTS — apply these exactly:
- Font: Times New Roman, 12pt, for all body text, headings, captions, and table content.
- Line spacing: Double-spaced throughout.
- Paragraph style: First line of each paragraph indented 0.5 inch; no blank lines between 
  paragraphs within a section.
- Chapter title ("Chapter 2: Literature Review"): format as Heading 1.
- Section titles (e.g. "2.1 Introduction"): format as Heading 2.
- Sub-section titles (e.g. "2.4.1 Django (Python)"): format as Heading 3.
- Sub-sub-section titles (e.g. "2.8.1 OWASP Top 10"): format as Heading 4.
- Do not use bullet points in the final output — convert all lists into flowing prose.
- Any comparison of technologies should be presented as a formatted table where appropriate 
  (numbered Table 2.1, Table 2.2 ..., captioned above the table in bold).
- In-text citations: APA 7th Edition format — (Author, Year) or Author (Year) as appropriate.
- Reference list: at the end of the chapter, titled "References", in APA 7th Edition 
  format, alphabetically sorted by first author's surname. Include DOI links where 
  available.
- Page margins: 1 inch on all sides.

CONTENT INSTRUCTIONS:
- Each sub-section comparing technologies (Django vs Flask vs Laravel vs Node.js, 
  PostgreSQL vs NoSQL, etc.) must end with a justified conclusion paragraph explaining 
  why the chosen technology was selected over the alternatives.
- The RBAC section must cite the original NIST definition as well as at least one recent 
  application of RBAC in an educational information system context.
- The "Related Works" section must compare at least four existing systems or academic 
  prototypes and conclude with a clear gap analysis paragraph explaining what LASU-IMS 
  provides that none of the reviewed works do.
- The "Theoretical Framework" section must explain both the MVT pattern and the Asset 
  Lifecycle Model clearly enough for a non-technical reader (e.g. an examiner from a 
  non-software background).
- Minimum length: 4,000 words (excluding the reference list).

Begin the output with "Chapter 2: Literature Review" formatted as Heading 1.
```

---

---

## PROMPT 3 — Chapter 3: Methodology

```
You are an academic writing assistant helping to produce a formal undergraduate/postgraduate 
project report. The attached file contains the full structured content for Chapter 3 
(Methodology) of a software engineering project titled:

"Design and Implementation of a Web-Based Inventory Management System for Lagos State 
University (LASU-IMS)"

Your task is to write Chapter 3 in full academic prose, using every section and data point 
in the attached file. Do not summarise or omit any section. Expand each heading and 
sub-point into well-developed paragraphs.

FIGURE PLACEHOLDER INSTRUCTION (IMPORTANT):
This chapter requires several diagrams and figures. Wherever a diagram, chart, or figure 
is needed, insert a clearly formatted placeholder in the following format:

    ┌─────────────────────────────────────────────────────────┐
    │  [FIGURE X.X — Title of Figure]                         │
    │  Description: Brief description of what this figure     │
    │  should show (e.g., "System architecture diagram        │
    │  showing the Django application layers, database,       │
    │  and static file server").                              │
    │  To be inserted by author.                              │
    └─────────────────────────────────────────────────────────┘
    Figure X.X: Caption for this figure (Times New Roman, 12pt, centred, below image)

Insert figure placeholders for at minimum the following (add more wherever appropriate):
- Figure 3.1: System Architecture Diagram (Django layers, database, client browser)
- Figure 3.2: Application Decomposition Diagram (the 9 Django apps and their relationships)
- Figure 3.3: Entity-Relationship Diagram (all 6 database tables and their relationships)
- Figure 3.4: Level 0 Context Data Flow Diagram
- Figure 3.5: Level 1 Asset Lifecycle Data Flow Diagram
- Figure 3.6: Use Case Diagram (all 5 roles and their associated use cases)
- Figure 3.7: Application Shell UI Layout (CSS Grid wireframe of sidebar + topbar + main)
- Figure 3.8: Iterative Development Increment Timeline

FORMATTING REQUIREMENTS — apply these exactly:
- Font: Times New Roman, 12pt, for all body text, headings, table content, and figure 
  captions.
- Line spacing: Double-spaced throughout (single-spaced inside code blocks or tables only).
- Paragraph style: First line of each paragraph indented 0.5 inch; no blank lines between 
  paragraphs within a section.
- Chapter title ("Chapter 3: Methodology"): format as Heading 1.
- Section titles (e.g. "3.1 Introduction"): format as Heading 2.
- Sub-section titles (e.g. "3.3.1 Functional Requirements"): format as Heading 3.
- Sub-sub-section titles (e.g. "3.4.1 System Architecture"): format as Heading 4.
- Requirements (FR-01, NFR-01 etc.) should be presented in numbered tables:
    Table 3.1: Functional Requirements (columns: ID | Requirement | Description)
    Table 3.2: Non-Functional Requirements (columns: ID | Requirement | Description)
  Tables are numbered Table 3.X, captioned in bold above the table.
- Figures are numbered Figure 3.X; caption centred in Times New Roman 12pt below the 
  placeholder box.
- Tools and technologies table: Table 3.3 (columns: Category | Tool | Version | Purpose).
- Do not use bullet points in the final output — convert all lists to prose or tables.
- Referencing: APA 7th Edition in-text citations where appropriate. Reference list at 
  the end of the chapter.
- Page margins: 1 inch on all sides.

CONTENT INSTRUCTIONS:
- The methodology section must justify the iterative approach by explicitly contrasting it 
  with the Waterfall model and explaining why iteration was more suitable for this project.
- The requirements section must present functional requirements as a formal table with IDs 
  (FR-01 to FR-30) — do not reduce their number.
- The database schema section must describe each entity/table in prose before or after 
  each figure placeholder, explaining the purpose of each field and each relationship.
- The UI design section must describe the CSS Grid layout, the token-based colour system, 
  and the dark/light theme mechanism in terms a non-programmer examiner can understand.
- Minimum length: 4,500 words (excluding tables, figure placeholders, and reference list).

Begin the output with "Chapter 3: Methodology" formatted as Heading 1.
```

---

---

## PROMPT 4 — Chapter 4: Implementation

```
You are an academic writing assistant helping to produce a formal undergraduate/postgraduate 
project report. The attached file contains the full structured content for Chapter 4 
(Implementation) of a software engineering project titled:

"Design and Implementation of a Web-Based Inventory Management System for Lagos State 
University (LASU-IMS)"

Your task is to write Chapter 4 in full academic prose, using every section and code 
excerpt in the attached file. Do not omit or summarise any module. Each section should be 
explained clearly enough for a technical examiner who may not have seen the source code.

FIGURE PLACEHOLDER INSTRUCTION (IMPORTANT):
This chapter requires screenshots, interface views, and code output images. Wherever a 
screenshot, system output image, or interface view is needed, insert a clearly formatted 
placeholder in the following format:

    ┌─────────────────────────────────────────────────────────┐
    │  [FIGURE X.X — Title of Figure]                         │
    │  Description: Brief description of what this screenshot │
    │  or image should show.                                  │
    │  To be inserted by author.                              │
    └─────────────────────────────────────────────────────────┘
    Figure X.X: Caption for this figure (Times New Roman, 12pt, centred, below image)

Insert figure placeholders for at minimum the following (add more wherever appropriate):
- Figure 4.1: Project directory tree / folder structure screenshot
- Figure 4.2: Login page screenshot (dark theme)
- Figure 4.3: Login page screenshot (light theme)
- Figure 4.4: Superadmin dashboard screenshot
- Figure 4.5: Store Officer dashboard screenshot
- Figure 4.6: HOD dashboard screenshot
- Figure 4.7: Auditor dashboard screenshot
- Figure 4.8: Bursar dashboard screenshot
- Figure 4.9: Asset registration form screenshot
- Figure 4.10: Asset detail page showing barcode and QR code
- Figure 4.11: Print queue page with queued assets
- Figure 4.12: Sample downloaded barcode/QR label PDF
- Figure 4.13: Requisitions list page
- Figure 4.14: Requisition detail page showing approval/rejection action
- Figure 4.15: Maintenance log list page
- Figure 4.16: Stock report with active filters applied
- Figure 4.17: Audit log page
- Figure 4.18: Reconciliation tool page
- Figure 4.19: Export Centre page
- Figure 4.20: Sample exported Excel (.xlsx) file
- Figure 4.21: Admin panel — user management page
- Figure 4.22: Account lockout page (after 5 failed login attempts)
- Figure 4.23: Forced password change page (first login)

CODE BLOCK FORMATTING:
- All code excerpts from the attached file must be retained and presented in a 
  monospaced font (Courier New, 10pt) inside a clearly bordered code block.
- Each code block must be preceded by a label in the format:
  "Code Listing 4.X: Description of what the code does" (Times New Roman, 12pt, bold, 
  left-aligned, above the block).
- Number code listings sequentially: Code Listing 4.1, 4.2, 4.3 ...

FORMATTING REQUIREMENTS — apply these exactly:
- Font: Times New Roman, 12pt, for all body text, headings, table content, and figure 
  captions. Courier New 10pt inside code blocks only.
- Line spacing: Double-spaced body text; single-spaced inside code blocks.
- Paragraph style: First line of each paragraph indented 0.5 inch; no blank lines between 
  paragraphs within a section.
- Chapter title ("Chapter 4: Implementation"): format as Heading 1.
- Section titles (e.g. "4.1 Introduction"): format as Heading 2.
- Sub-section titles (e.g. "4.6.1 Auto ID Generation"): format as Heading 3.
- Sub-sub-section titles: format as Heading 4.
- Tables numbered Table 4.X, captioned above in bold Times New Roman 12pt.
- Figures numbered Figure 4.X, captioned below in Times New Roman 12pt centred.
- The permission matrix must be presented as a formal table (Table 4.1).
- The test cases (manual functional and security tests) must be presented as formal tables:
    Table 4.2: Manual Functional Test Results (Test Case | Expected | Actual | Pass/Fail)
    Table 4.3: Security Test Results (Test Case | Expected | Actual | Pass/Fail)
- The deployment settings must be presented as a table (Table 4.4).
- Do not use bullet points in final prose sections — convert to flowing paragraphs.
- Referencing: APA 7th Edition in-text citations where appropriate. Reference list at end.
- Page margins: 1 inch on all sides.

CONTENT INSTRUCTIONS:
- Each module section (Assets, Requisitions, Maintenance, Reports, etc.) must begin with 
  a brief paragraph explaining the purpose of the module before diving into implementation 
  detail.
- The code excerpts must be explained line-by-line or block-by-block in surrounding 
  prose — do not just present code without explanation.
- The security implementation section must explicitly reference OWASP standards and Django 
  security mechanisms by name, with in-text citations.
- The testing section must present results in table format and include a brief analysis 
  paragraph summarising the overall test outcome.
- Minimum length: 5,000 words (excluding code listings, tables, figure placeholders, 
  and reference list).

Begin the output with "Chapter 4: Implementation" formatted as Heading 1.
```

---

---

## PROMPT 5 — Chapter 5: Conclusion

```
You are an academic writing assistant helping to produce a formal undergraduate/postgraduate 
project report. The attached file contains the full structured content for Chapter 5 
(Conclusion) of a software engineering project titled:

"Design and Implementation of a Web-Based Inventory Management System for Lagos State 
University (LASU-IMS)"

Your task is to write Chapter 5 in full academic prose, using every section in the 
attached file. This is the final chapter and should have a reflective, evaluative tone — 
synthesising what was achieved, honestly acknowledging limitations, and proposing 
well-argued future work.

FORMATTING REQUIREMENTS — apply these exactly:
- Font: Times New Roman, 12pt, for all body text, headings, table content, and captions.
- Line spacing: Double-spaced throughout.
- Paragraph style: First line of each paragraph indented 0.5 inch; no blank lines between 
  paragraphs within a section.
- Chapter title ("Chapter 5: Conclusion"): format as Heading 1.
- Section titles (e.g. "5.1 Introduction"): format as Heading 2.
- Sub-section titles (e.g. "5.5.1 Email Notifications"): format as Heading 3.
- The "Achievement of Objectives" section must be presented as a formal table:
    Table 5.1: Achievement of Project Objectives
    Columns: Objective | Achievement Status | Evidence
  Captioned in bold above the table.
- Do not use bullet points in the final output — convert all lists to prose or tables.
- Referencing: APA 7th Edition in-text citations where appropriate. Reference list at 
  the end of the chapter.
- Page margins: 1 inch on all sides.

CONTENT INSTRUCTIONS:
- The Summary section (5.2) must briefly revisit every chapter of the report (what was 
  done in Chapter 1, what was found in Chapter 2, what was designed in Chapter 3, what 
  was built in Chapter 4) before summarising the outputs of Chapter 4 itself. This gives 
  the chapter a sense of closure for the full project.
- The "Achievement of Objectives" section must map every one of the 7 objectives stated 
  in Chapter 1 to a specific deliverable in Chapter 4, with evidence. Present this as 
  Table 5.1.
- The "Limitations" section must present each limitation as a numbered sub-section with: 
  (a) a clear description of the limitation, (b) the reason it was accepted or 
  unavoidable, and (c) its practical impact on the system.
- The "Future Work" section must present each recommendation as a numbered sub-section 
  with: (a) what would be built or changed, (b) the specific technology or approach that 
  would be used, and (c) how it would improve the system beyond its current state.
- The concluding paragraph (end of 5.6) must be at least 200 words and must bring 
  together the academic contribution, the institutional value, and the personal 
  development significance of the project.
- Minimum length: 2,000 words (excluding the table and reference list).

Begin the output with "Chapter 5: Conclusion" formatted as Heading 1.
```

---

---

## Quick Reference: Figure Numbers by Chapter

### Chapter 3 Figures
| Figure | Description |
|---|---|
| Figure 3.1 | System Architecture Diagram |
| Figure 3.2 | Application Decomposition (9 Django apps) |
| Figure 3.3 | Entity-Relationship Diagram |
| Figure 3.4 | Level 0 Context DFD |
| Figure 3.5 | Level 1 Asset Lifecycle DFD |
| Figure 3.6 | Use Case Diagram |
| Figure 3.7 | UI App Shell Wireframe (CSS Grid) |
| Figure 3.8 | Development Increment Timeline |

### Chapter 4 Figures (Screenshots to take from the running app)
| Figure | What to screenshot |
|---|---|
| Figure 4.1 | Project folder tree in VS Code |
| Figure 4.2 | Login page — dark theme |
| Figure 4.3 | Login page — light theme |
| Figure 4.4 | Superadmin dashboard |
| Figure 4.5 | Store Officer dashboard |
| Figure 4.6 | HOD dashboard |
| Figure 4.7 | Auditor dashboard |
| Figure 4.8 | Bursar dashboard |
| Figure 4.9 | Asset registration form |
| Figure 4.10 | Asset detail page (barcode + QR visible) |
| Figure 4.11 | Print queue page |
| Figure 4.12 | Downloaded label PDF open in a PDF viewer |
| Figure 4.13 | Requisitions list |
| Figure 4.14 | Requisition detail (approval buttons visible) |
| Figure 4.15 | Maintenance log list |
| Figure 4.16 | Stock report with filters applied |
| Figure 4.17 | Audit log page |
| Figure 4.18 | Reconciliation tool |
| Figure 4.19 | Export Centre |
| Figure 4.20 | Exported Excel file in Microsoft Excel |
| Figure 4.21 | Admin panel — user management |
| Figure 4.22 | Account lockout page |
| Figure 4.23 | Forced password change page |
