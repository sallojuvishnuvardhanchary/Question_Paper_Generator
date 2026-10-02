# Syllabus-Driven Intelligent Exam Question Paper Generator

**CoreAlgorithm PROBLEM95 — Design and Analysis of Algorithms (DAA)**  
*Automatic Question Generation and Balanced Paper Construction using Greedy, Backtracking, and Sorting Algorithms*

---

## 1. Project Overview

The **Syllabus-Driven Intelligent Exam Question Paper Generator** is a production-grade, algorithm-centric academic web application. It transforms the question paper synthesis workflow from static question-bank selection into a **dynamic, syllabus-driven automatic generation engine**.

### Core Workflow:
```text
CLIENT
   ↓
UPLOAD SYLLABUS COPY (PDF / DOCX / TXT)
   ↓
EXTRACT SYLLABUS CONTENT (Units, Titles, Topics)
   ↓
REVIEW & EDIT EXTRACTED SYLLABUS
   ↓
SELECT QUESTION PAPER TYPE (Theory+Bits / Theory / MCQ)
   ↓
CONFIGURE PAPER STRUCTURE (Parts, Sections, Questions, Marks, Internal Choices)
   ↓
GENERATE CANDIDATE QUESTIONS FROM SYLLABUS (Bloom's Taxonomy)
   ↓
APPLY DAA OPTIMIZATION (Greedy / Backtracking with Branch & Bound / Sorting)
   ↓
VALIDATE PAPER CONSTRAINTS
   ↓
PREVIEW FORMATTED EXAMINATION PAPER
   ↓
GENERATE PROFESSIONAL REPORTLAB A4 PDF (Student Paper + Answer Key)
   ↓
DOWNLOAD HIGH-RESOLUTION PDF
```

---

## 2. Supported Examination Paper Types

The application supports three distinct academic paper formats:

1. **Option 1 — Theory + Bits**:
   * Blends conceptual short-answer bits (e.g. 2 Marks each) and analytical descriptive theory problems (e.g. 10 or 16 Marks each).
   * Fully configurable multi-part and multi-section layouts.
   * Full support for internal choices: `Q11. (a) ... OR Q11. (b) ...` with equal-marks symmetry.

2. **Option 2 — Theory Only**:
   * Dedicated to pure descriptive, analytical, and derivation-based examinations.
   * Short, medium, and comprehensive long-answer questions.
   * Configurable internal choices per unit or section.

3. **Option 3 — Multiple Choice Questions (MCQ)**:
   * Objective assessment papers with 4 distinct options `(A)`, `(B)`, `(C)`, `(D)` per question.
   * Internally verified answer keys.
   * Separate Official Answer Key PDF generation with solutions and rationale.

---

## 3. Dynamic Paper Structure Builder

Rather than enforcing one hard-coded exam format, the client has complete freedom to define their own examination pattern:
* **Multiple Parts**: Part A, Part B, Part C, etc.
* **Sections Per Part**: Section 1, Section 2, etc.
* **Granular Section Parameters**:
  * Number of questions
  * Marks per question
  * Question type (Bits, Short Answer, Theory, MCQ)
  * Internal Choice toggle (`(a) OR (b)`)
* **Live Calculation**: Automatically tallies section totals, part totals, overall maximum marks, and estimated exam duration.
* **University Presets**:
  * *Autonomous Engineering (100 Marks)*: Part A (10 × 2M Bits) + Part B (5 × 16M Theory with choices)
  * *Mid-Term Assessment (50 Marks)*: Part A (5 × 2M Short) + Part B (4 × 10M Theory with choices)
  * *Pure Theory Examination (70 Marks)*: 5 × 14M Analytical problems
  * *Objective MCQ Examination (50 Marks)*: 50 × 1M MCQs

---

## 4. DAA Algorithms Implemented

### 4.1. Greedy Selection Algorithm
Selects locally optimal questions at each stage to satisfy dynamic section targets:
$$\text{Score}(q) = W_m \cdot S_{\text{marks}} + W_d \cdot S_{\text{diff}} + W_u \cdot S_{\text{unit}} + W_t \cdot S_{\text{topic}} + W_n \cdot S_{\text{novelty}}$$
* Enforces exact mark feasibility on concluding section questions.
* Prioritizes units and difficulty tiers with the highest deficit.
* Time Complexity: $\mathcal{O}(K \cdot N)$, Space Complexity: $\mathcal{O}(N)$.

### 4.2. Backtracking with Branch-and-Bound Pruning
Conducts depth-first state-space search to guarantee exact constraint satisfaction:
* **Bounding Criteria**:
  * *Marks Feasibility*: Prunes when remaining needed marks exceed pool maximums or fall below pool minimums.
  * *Candidate Sufficiency*: Prunes when remaining pool is smaller than required questions.
  * *Unit & Difficulty Quotas*: Prunes branches exceeding maximum quota caps.
* Reverts state upon detecting infeasible paths and explores alternative sibling branches.
* Worst-case $\mathcal{O}(2^N)$, average pruned $\mathcal{O}(N \cdot K)$.

### 4.3. Sorting Algorithms
Organizes candidate questions and generated paper sections:
* **Bubble Sort**, **Selection Sort**, **Insertion Sort**, **Merge Sort**, **Quick Sort**.
* Sorts candidates by Marks, Difficulty level, Unit number, Topic relevance, Novelty, and Past usage count.
* Interactive sorting visualizer and comparative benchmark engine in the Algorithm Lab.

---

## 5. ReportLab Server-Side PDF Generation

Produces authentic, publication-quality academic PDFs:
* Standard **A4 Page Format** with professional academic margins.
* Two-pass `NumberedCanvas` delivering dynamic **Page X of Y** pagination.
* Formal **Institution Header Box** (Institution Name, Department, Examination Title, Subject Code, Date, Duration, Max Marks).
* Clear Section Dividers and tabular marks alignment.
* Prominent, centered internal choice dividers `[ OR ]`.
* For MCQs: Compact 2×2 option grids `(A)`, `(B)`, `(C)`, `(D)`.
* **Separate Answer Key PDF**: Complete solution key table with correct option letters and explanatory notes.

---

## 6. Technology Stack

* **Backend**: Python 3.10+ / Flask
* **Document Parsing**: `pypdf` (PDF), `python-docx` (DOCX), standard UTF-8 (TXT)
* **PDF Engine**: ReportLab 4.x
* **Database**: SQLite3 with WAL mode and schema auto-migration
* **Frontend**: Vanilla ES6+ JavaScript, CSS3 Design System (Light & Dark Slate `#0F172A`), Chart.js 4.4
* **Testing**: Pytest (30 automated unit & integration tests)

---

## 7. Installation & Quick Start

```bash
# 1. Clone repository and navigate to folder
cd Question_Paper_Generator

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start Flask server
python app.py
```

Open your browser and navigate to:
```text
http://127.0.0.1:5000
```

---

## 8. Running Automated Tests

Run the full automated test suite with pytest:
```bash
python -m pytest tests/ -v
```

All 30 unit and integration tests execute with 100% pass rate:
* `tests/test_algorithms.py`: Greedy, Backtracking, and Sorting algorithms.
* `tests/test_api.py`: REST API endpoints, input validation, and end-to-end syllabus-to-PDF pipeline.
* `tests/test_paper_service.py`: Structured paper orchestration, choice symmetry, and DB persistence.
* `tests/test_pdf.py`: ReportLab examination paper & answer key PDF synthesis.
* `tests/test_question_generation.py`: Bloom's taxonomy candidate generation for Theory, Bits, and MCQs.
* `tests/test_syllabus.py`: PDF, DOCX, TXT document parsing and Roman/Arabic unit extraction.

---

## 9. Themes & Design

* **Light Mode**: Clean academic SaaS aesthetic with off-white backgrounds (`#F8FAFC`, `#FFFFFF`), indigo/blue accents (`#2563EB`), dark navy text (`#0F172A`), and clear visual hierarchy.
* **Dark Mode**: Premium Slate palette (`#0F172A` main background, `#1E293B` cards, `#334155` borders, `#60A5FA` accents). **Never pure black (`#000000`)**.
* Theme selection is persisted seamlessly across sessions via `localStorage`.

---

## 10. License

Academic and educational use — CoreAlgorithm PROBLEM95.
