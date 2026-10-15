# QA Test Case Generator Agent (MVP)

A Streamlit web app that generates manual QA test cases, framework starter scripts, and an Excel workbook from a pasted requirement or `.txt`/`.md` file.

## Features
- Manual test cases with IDs, preconditions, data, steps, expected results, priority, type, status, and automation feasibility.
- Local Qwen3.5-4B generation through the Hugging Face Transformers `image-text-to-text` pipeline; no model API key is required.
- Offline deterministic templates as an alternative to model-backed generation.
- Starter templates for Selenium + Java + TestNG, Playwright + TypeScript, REST Assured + Java, and Postman Collection JSON.
- Excel workbook with `Manual Test Cases`, `Automation Scenarios`, `Traceability`, and `Read Me` sheets.
- CSV and individual code downloads.
- Requirements are processed by the app host and are not sent to an external inference API. The public model weights are downloaded from Hugging Face on the first Qwen run.

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

## Local model requirements

Choose **Local Qwen3.5-4B** in the Generation engine selector to use the model. The first generation downloads several gigabytes of model weights and caches them on the host. Model loading and inference require substantial RAM or GPU memory and can be slow, especially on CPU-only machines. No Hugging Face or OpenAI API key is needed for this public model.

Choose **Offline templates** to generate cases without downloading or loading the model. This mode cycles through 14 generic patterns for counts above 14; larger counts are not distinct requirement-derived scenarios.

## How to use
1. Paste a requirement, acceptance criteria, API description, or bug report.
2. Choose output mode and automation frameworks in the sidebar.
3. Click **Generate QA Deliverables**.
4. Review generated cases and assumptions.
5. Download individual starter scripts or the Excel workbook.

## Important limitations
Qwen output is model-generated and must be reviewed against the source requirement; it can omit or misinterpret business rules. Offline template mode is generic and repeats its 14 patterns for counts above 14. Replace placeholder URLs, locators, endpoints, payloads, and assertions in the starter scripts. No generated test has been executed or verified against your application.

## Recommended next development steps
1. Add requirement-to-test traceability and coverage scoring.
2. Add uploads for DOCX/PDF/XLSX and API specifications.
3. Add project profiles for the target app, environments, selectors, API auth, and test-data strategy.
4. Add validation and sandbox execution for supported automation code, with explicit user approval before running tests.
5. Add authentication, role-based access, and secure deployment controls before team deployment.
