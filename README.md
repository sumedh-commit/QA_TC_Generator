# QA Test Case Generator Agent (MVP)

A local Streamlit web app that generates baseline manual QA test cases, framework starter scripts, and an Excel workbook from a pasted requirement or `.txt`/`.md` file.

## Features
- Manual test cases with IDs, preconditions, data, steps, expected results, priority, type, status, and automation feasibility.
- Starter templates for Selenium + Java + TestNG, Playwright + TypeScript, REST Assured + Java, and Postman Collection JSON.
- Excel workbook with `Manual Test Cases`, `Automation Scenarios`, `Traceability`, and `Read Me` sheets.
- CSV and individual code downloads.
- Runs locally; requirements are not sent to an external AI service in this MVP.

## Setup
Requires Python 3.10-3.13.

This app is tested against Python 3.10-3.13. Newer Python 3.14/3.15 builds can fail when installing some transitive dependencies (for example pandas/pyarrow from the current Streamlit stack).

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit (usually `http://localhost:8501`).

## How to use
1. Paste a requirement, acceptance criteria, API description, or bug report.
2. Choose output mode and automation frameworks in the sidebar.
3. Click **Generate QA Deliverables**.
4. Review generated cases and assumptions.
5. Download individual starter scripts or the Excel workbook.

## Important limitations
This first version is a deterministic template-based MVP, not yet an LLM-powered requirement reasoning system. Generated scenarios are generic and may not reflect all business rules. Replace placeholder URLs, locators, endpoints, payloads, and assertions. Review expected results with the source requirement. No generated test has been executed or verified against your application.

## Recommended next development steps
1. Add a secure server-side LLM integration to parse requirements into structured JSON.
2. Add requirement-to-test traceability and coverage scoring.
3. Add uploads for DOCX/PDF/XLSX and API specifications.
4. Add project profiles for the target app, environments, selectors, API auth, and test-data strategy.
5. Add validation and sandbox execution for supported automation code, with explicit user approval before running tests.
6. Add authentication, role-based access, and secure secret management before team deployment.
