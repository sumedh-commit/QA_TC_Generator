# QA Test Case Generator — Developer Explanation

## 1. Project overview

The QA Test Case Generator is a local web application built with Streamlit. It takes a requirement, user story, acceptance criteria, API description, or bug report and creates:

- A configurable set of manual QA test cases.
- Starter automation code for selected frameworks.
- CSV and Excel downloads for sharing and review.

The app supports local Qwen3.5-4B generation through Hugging Face Transformers, as well as deterministic offline templates. In Qwen mode, the model runs on the app host; requirement text is not sent to a hosted inference API.

## 2. Problem it addresses

Writing baseline QA scenarios manually can be repetitive and inconsistent. This tool gives a tester or developer a structured starting point, including common positive, negative, boundary, authorization, resilience, persistence, and regression checks. The generated cases still need to be reviewed against the real product rules before execution.

## 3. Technology stack

- **Python** — application logic.
- **Streamlit** — interactive web UI and session state.
- **openpyxl** — creates and formats Excel workbooks.
- **PyTorch, Transformers, and Accelerate** — load and run Qwen3.5-4B locally.
- **Python standard library** — text processing, JSON, CSV, and in-memory file handling.

The pinned runtime dependencies are listed in `requirements.txt`.

## 4. Application structure

The MVP is intentionally small:

- `app.py` contains the Streamlit interface, scenario generation, automation templates, and workbook export.
- `requirements.txt` pins the Python dependencies.
- `README.md` contains setup and usage instructions.
- `.env.example` notes that local model inference does not require an API key.

## 5. Request-to-download flow

1. Streamlit renders the input area, file uploader, output-mode selector, framework selector, and scenario-count slider.
2. The user enters a requirement or uploads a UTF-8 `.txt` or `.md` file.
3. When **Generate QA Deliverables** is selected, the app checks that the requirement is not empty.
4. The selected engine either calls `generate_qwen_cases()` to request structured cases from Qwen in batches of 10, or calls `generate_cases()` to use deterministic offline templates.
5. `automation_code()` builds starter code for each selected framework, unless the user selected manual-only output.
6. The generated data and selected mode are stored in `st.session_state`, so the results remain available through Streamlit reruns.
7. The UI presents a manual-case table, automation templates, coverage notes, CSV download, and Excel workbook download.

## 6. Important functions

### `clean_title(text)`

Normalizes whitespace and limits a requirement summary to 100 characters. It is used in scenario descriptions and generated code metadata.

### `infer_feature(requirement)`

Extracts a short, readable feature label from the requirement by removing a small set of common words. This label is used as the module name and as a prefix for each test title. It is a simple heuristic, not natural-language understanding.

### `generate_cases(requirement, count)`

Builds dictionaries for the requested number of cases. Each dictionary includes:

- Test case ID and requirement reference.
- Module and scenario title.
- Preconditions, test data, and numbered steps.
- Expected result, priority, test type, status, and automation feasibility.
- Assumptions and review notes.

The function cycles through 14 generic baseline patterns. When the requested count exceeds 14, later cases repeat those patterns and label them as separate data/configuration sets. This produces the requested row count, but does **not** discover new requirement-specific scenarios or invent approved test data.

### `load_qwen_pipeline()`

Loads and caches the Hugging Face Transformers pipeline for `Qwen/Qwen3.5-4B` using the `image-text-to-text` task and automatic device placement. The public model weights are downloaded from Hugging Face on the first run. A model API key is not required, but the host needs internet access for the initial download and sufficient RAM or GPU memory to load and run the model.

### `generate_qwen_cases(requirement, count, progress)`

Sends the requirement to the locally loaded Qwen model in batches of 10. It requests JSON, validates the response shape and required fields, and maps valid model output into the same case schema used by the rest of the app. Invalid or incomplete model output is reported as an error rather than silently replaced with template cases.

### `automation_code(framework, requirement, cases)`

Returns a starter template for one of four supported formats:

- Selenium + Java + TestNG.
- Playwright + TypeScript.
- REST Assured + Java.
- Postman Collection JSON.

The output contains placeholders for application URLs, selectors, endpoints, payloads, and assertions. These are scaffolds, not executable tests verified against a target application.

### `make_workbook(cases, code_map, requirement)`

Creates an `.xlsx` file in memory using `openpyxl`. The workbook contains:

1. **Manual Test Cases** — the generated case records.
2. **Automation Scenarios** — case-to-framework starter candidates.
3. **Traceability** — a basic link between the supplied requirement and generated case IDs.
4. **Read Me** — source requirement, generation notes, and execution-status disclaimer.

The workbook is returned as bytes, so the app does not need to write a temporary workbook to disk.

## 7. Output modes and framework selection

The UI offers three modes:

- **Both: Manual + Automation** — manual cases and selected automation templates.
- **Manual test cases only** — manual cases, with no automation templates.
- **Automation scripts only** — selected automation templates are displayed. The current implementation still generates and retains manual cases internally because generation and workbook creation share the same case data.

The framework selector controls which automation templates are included. Framework templates are starter examples and require project-specific implementation.

## 8. Data flow and privacy

Requirement processing happens on the app host. Qwen mode downloads public weights from Hugging Face, but prompts are sent to the local pipeline rather than to a hosted inference API. Generated data is held in Streamlit session state for the active session. The app has no database, user accounts, or authentication; do not deploy it publicly for confidential requirements without adding appropriate access controls and deployment safeguards.

## 9. Running locally

Use Python 3.10–3.13 as noted in the README:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit, usually `http://localhost:8501`.

## 10. Known limitations

- Qwen generation requires a large model download and substantial host RAM or GPU memory; it may be slow or fail on small deployment instances.
- Model-generated cases can be inaccurate and must be reviewed against the original requirement.
- Offline scenario generation is based on 14 generic templates, not requirement parsing.
- Counts above 14 repeat generic patterns with separate data-set labels; they should not be interpreted as that many unique, requirement-derived scenarios.
- Uploaded files are limited to UTF-8 `.txt` and `.md`; PDF, DOCX, spreadsheet, and API-spec parsing are not implemented.
- Framework outputs include placeholder values and assertions and have not been run against a real application.
- Traceability is currently a single generic requirement reference rather than detailed acceptance-criteria coverage.
- The app has no authentication, roles, persistent storage, or team collaboration.
- The **Automation scripts only** mode still builds manual cases internally.

## 11. Suggested future improvements

1. Parse requirements into structured acceptance criteria, business rules, and entities before generating tests.
2. Generate genuinely distinct cases from identified rules rather than cycling generic patterns.
3. Add requirement-to-case traceability and measurable coverage reporting.
4. Support DOCX, PDF, XLSX, CSV, and API specifications with format-specific parsers and validation.
5. Add project profiles for base URLs, authentication, selectors, environments, and test data.
6. Validate or execute generated automation only in a controlled environment with explicit user approval.
7. Add authentication, authorization, deployment hardening, and secure storage before team or public use.

## 12. Short presentation talk track

> “This project is a Streamlit-based QA test case generator. A tester enters a requirement or uploads a UTF-8 text or Markdown file, chooses local Qwen3.5-4B or offline templates, selects an output mode and automation framework, and sets the number of cases. The app produces structured manual cases, starter automation templates, and CSV or Excel exports. Python handles the application logic, Streamlit provides the UI, Transformers runs the model locally, and openpyxl builds the workbook. Qwen removes the need for a model API key, but its output still needs human review and the model host needs significant compute resources.”
