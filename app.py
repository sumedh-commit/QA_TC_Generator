import os, re, json, io, textwrap
from datetime import datetime
import streamlit as st
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

st.set_page_config(page_title="QA Test Case Generator", page_icon="🧪", layout="wide")

FRAMEWORKS = ["Selenium + Java + TestNG", "Playwright + TypeScript", "REST Assured + Java", "Postman Collection"]


def clean_title(text):
    text = re.sub(r'\s+', ' ', text.strip())
    return text[:100] if text else "Requirement validation"


def infer_feature(requirement):
    words = re.findall(r"[A-Za-z][A-Za-z0-9_-]*", requirement)
    stop = {"the","and","for","with","that","this","from","when","user","should","must","have","will","can","into","then","they","their","there","are","has","allow","allows"}
    meaningful = [w for w in words if w.lower() not in stop]
    return " ".join(meaningful[:5]).title() or "General Feature"


def generate_cases(requirement, count=12):
    feature = infer_feature(requirement)
    req_short = clean_title(requirement)
    templates = [
        ("Positive flow - valid input", "Valid input matching the stated requirement", "Submit valid data and complete the primary user flow.", "The system accepts the input and completes the intended flow without errors.", "Functional", "P1"),
        ("Required field validation", "Required fields are available and the user leaves one blank", "Leave a required field empty and submit.", "Submission is blocked and a clear validation message is shown.", "Negative", "P1"),
        ("Invalid input handling", "Input violates a documented format or business rule", "Enter invalid data and submit.", "The system rejects invalid data and displays an actionable error without corrupting state.", "Negative", "P1"),
        ("Boundary values", "Minimum, maximum, and just-outside-boundary values are known", "Test minimum, maximum, below-minimum, and above-maximum values.", "Boundary values follow documented rules; out-of-range values are rejected or handled as specified.", "Boundary", "P1"),
        ("Empty and null values", "Optional and nullable fields are identified", "Send empty strings, nulls, and omitted fields where applicable.", "Each value is handled according to the requirement and the response remains stable.", "Negative", "P2"),
        ("Duplicate submission", "The primary action can be triggered more than once", "Submit once, then double-click or repeat the request.", "The system prevents unintended duplicate records or clearly supports idempotent behavior.", "Integration", "P1"),
        ("Error and recovery", "A downstream service or operation can fail", "Simulate an error or unavailable dependency, then retry.", "The error is handled gracefully; retry/recovery follows documented behavior and no partial corruption occurs.", "Resilience", "P1"),
        ("Authorization", "The feature has authenticated or role-based access", "Access the feature as an unauthenticated user and as a user without permission.", "Only authorized users can perform permitted actions; access is denied safely otherwise.", "Security", "P1"),
        ("Persistence and data consistency", "The flow creates or updates data", "Complete the flow, refresh/reopen the page, and verify the saved data through an approved source.", "Saved values remain consistent across the UI and relevant API/database records.", "Data", "P1"),
        ("Usability and feedback", "The user receives success, error, or progress feedback", "Perform the action under normal and slow-response conditions.", "Feedback is clear, accurate, accessible, and does not leave the UI in a misleading state.", "UI", "P2"),
        ("Session and timeout", "The flow depends on an authenticated or time-bound session", "Attempt the flow after session expiry or a long idle period.", "The system prompts for re-authentication or recovers according to the specified session policy.", "Security", "P2"),
        ("Regression - adjacent flow", "The feature shares components or data with adjacent flows", "Run the primary flow and one related existing flow.", "The new behavior works and existing related functionality remains unaffected.", "Regression", "P1"),
        ("Concurrency", "Multiple users or requests may update the same resource", "Perform simultaneous updates or repeat the operation from separate sessions.", "Conflicting updates are handled consistently with no lost or duplicated data.", "Concurrency", "P2"),
        ("Audit and observability", "The system should log significant actions or failures", "Perform a successful action and a failed action; inspect approved logs/analytics.", "Relevant events contain the expected identifiers and outcome without exposing secrets.", "Logging", "P3"),
    ]
    cases = []
    for i, (title, pre, steps, expected, typ, priority) in enumerate(templates[:count], 1):
        cases.append({
            "Test Case ID": f"TC-{i:03d}", "Requirement Reference": "REQ-1 (user supplied requirement)",
            "Module": feature, "Test Scenario / Title": f"{feature}: {title}",
            "Preconditions": pre, "Test Data": "Use valid/invalid values from the approved specification; exact values TBD if not provided.",
            "Steps": f"1. Review the requirement: {req_short}\n2. {steps}",
            "Expected Result": expected, "Priority": priority, "Test Type": typ,
            "Status": "Not Run", "Automation Feasibility": "Yes" if typ not in ("Usability", "Logging") else "Partial",
            "Assumptions / Notes": "Generic baseline scenario. Confirm feature-specific rules and expected messages against the source requirement."
        })
    return cases


def automation_code(framework, requirement, cases):
    title = clean_title(requirement)
    if framework == "Selenium + Java + TestNG":
        return f'''// Generated starter template - replace URL, locators, and assertions with application details.\nimport org.openqa.selenium.*;\nimport org.openqa.selenium.chrome.ChromeDriver;\nimport org.testng.Assert;\nimport org.testng.annotations.*;\nimport java.time.Duration;\n\npublic class GeneratedRequirementTest {{\n  private WebDriver driver;\n  @BeforeMethod public void setUp() {{\n    driver = new ChromeDriver();\n    driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(2));\n    driver.manage().window().maximize();\n  }}\n  @Test(description = "{title.replace(chr(34), chr(39))}")\n  public void validateRequirement() {{\n    driver.get(System.getProperty("baseUrl", "https://replace-me.example"));\n    // TODO: Add stable locators, user actions, and assertions from the requirement.\n    Assert.assertTrue(driver.getTitle() != null, "Page title should be available");\n  }}\n  @AfterMethod public void tearDown() {{ if (driver != null) driver.quit(); }}\n}}\n'''
    if framework == "Playwright + TypeScript":
        return f'''// Generated starter template - replace URL, locators, and assertions.\nimport {{ test, expect }} from '@playwright/test';\n\ntest('{title.replace(chr(39), chr(92)+chr(39))}', async ({{ page }}) => {{\n  await page.goto(process.env.BASE_URL ?? 'https://replace-me.example');\n  // TODO: Add role/test-id locators, actions, and requirement-specific assertions.\n  await expect(page).toHaveTitle(/.*/);\n}});\n'''
    if framework == "REST Assured + Java":
        return f'''// Generated API starter template - replace endpoint, auth, payload, and expected status.\nimport org.testng.annotations.Test;\nimport static io.restassured.RestAssured.given;\nimport static org.hamcrest.Matchers.*;\n\npublic class GeneratedApiTest {{\n  @Test(description = "{title.replace(chr(34), chr(39))}")\n  public void validateApiRequirement() {{\n    given()\n      .baseUri(System.getProperty("apiBaseUrl", "https://replace-me.example"))\n      .header("Accept", "application/json")\n    .when()\n      .get("/replace-with-endpoint") // TODO: choose the documented HTTP method and endpoint\n    .then()\n      .statusCode(anyOf(is(200), is(201))); // TODO: assert the documented status and response schema\n  }}\n}}\n'''
    collection = {"info":{"name":"Generated QA API Tests","schema":"https://schema.getpostman.com/json/collection/v2.1.0/collection.json","description":title},"item":[{"name":"Replace with requirement API test","request":{"method":"GET","header":[{"key":"Accept","value":"application/json"}],"url":{"raw":"{{baseUrl}}/replace-with-endpoint","host":["{{baseUrl}}"],"path":["replace-with-endpoint"]}},"event":[{"listen":"test","script":{"type":"text/javascript","exec":["pm.test('Response status is successful - replace with documented expectation', function () {","  pm.expect(pm.response.code).to.be.oneOf([200, 201]);","});","// TODO: Assert required response fields, schema, and business rules."]}}]}],"variable":[{"key":"baseUrl","value":"https://replace-me.example"}]}
    return json.dumps(collection, indent=2)


def make_workbook(cases, code_map, requirement):
    wb = Workbook()
    ws = wb.active; ws.title = "Manual Test Cases"
    headers = list(cases[0].keys()) if cases else ["Test Case ID", "Test Scenario / Title"]
    ws.append(headers)
    for c in cases: ws.append([c.get(h, "") for h in headers])
    auto = wb.create_sheet("Automation Scenarios")
    auto_headers = ["Automation ID", "Manual Test Case ID", "Framework", "Scenario", "Automation Status", "Notes"]
    auto.append(auto_headers)
    for fw in code_map:
        for i, c in enumerate(cases, 1):
            if c["Automation Feasibility"] != "No":
                auto.append([f"AUTO-{fw[:3].upper()}-{i:03d}", c["Test Case ID"], fw, c["Test Scenario / Title"], "Starter / Not Executed", "Generated code is a scaffold; complete selectors, test data, and assertions."])
    trace = wb.create_sheet("Traceability")
    trace.append(["Requirement Reference", "Requirement Summary", "Test Case IDs", "Coverage Notes"])
    trace.append(["REQ-1", clean_title(requirement), ", ".join(c["Test Case ID"] for c in cases), "Baseline generic coverage; review against full acceptance criteria."])
    readme = wb.create_sheet("Read Me")
    rows = [
        ["QA Test Case Generator - Export Notes"],
        ["Generated at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        ["Source requirement", requirement],
        ["Important", "Generated scenarios are a starting point. Verify business rules and expected results before execution."],
        ["Automation", "Automation Scenarios lists linked candidates. Source templates are provided in the app; replace placeholders before running."],
        ["Status", "All test cases default to Not Run. No tests have been executed by this workbook generator."],
    ]
    for r in rows: readme.append(r)
    for sheet in wb.worksheets:
        sheet.freeze_panes = "A2"
        sheet.auto_filter.ref = sheet.dimensions
        for cell in sheet[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="174A7E")
            cell.alignment = Alignment(wrap_text=True, vertical="top")
        for col in sheet.columns:
            max_len = min(max((len(str(c.value or "")) for c in list(col)[:100]), default=10) + 2, 55)
            sheet.column_dimensions[get_column_letter(col[0].column)].width = max(14, max_len)
        for row in sheet.iter_rows(min_row=2):
            for cell in row: cell.alignment = Alignment(wrap_text=True, vertical="top")
    out = io.BytesIO(); wb.save(out); out.seek(0)
    return out.getvalue()

st.title("🧪 QA Test Case Generator Agent")
st.caption("Generate manual test cases, automation starter scripts, and an Excel workbook from a requirement.")

with st.sidebar:
    st.header("Generation settings")
    mode = st.selectbox("Output mode", ["Both: Manual + Automation", "Manual test cases only", "Automation scripts only"])
    frameworks = st.multiselect("Automation frameworks", FRAMEWORKS, default=[FRAMEWORKS[0], FRAMEWORKS[1], FRAMEWORKS[2]])
    case_count = st.slider("Baseline scenarios", min_value=6, max_value=14, value=12)
    st.markdown("---")
    st.subheader("Optional AI enhancement")
    st.write("Add an OpenAI API key in your environment to enable a future LLM-backed generator. This MVP currently uses deterministic templates and does not send your requirements anywhere.")
    st.caption("Offline template mode is active.")

example = "As an admin, I can search for an account, open its reports, select a date range and channel, and view the filtered report results. Invalid dates should show validation, and users without report permission must not access the page."
requirement = st.text_area("Paste a BRD, user story, acceptance criteria, API requirement, or bug description", value=example, height=190, placeholder="Describe the feature, business rules, validations, and expected behavior...")
col1, col2 = st.columns([1, 1])
with col1:
    uploaded = st.file_uploader("Or upload a text-based requirement (.txt, .md)", type=["txt", "md"])
    if uploaded is not None:
        try: requirement = uploaded.read().decode("utf-8")
        except Exception: st.error("Could not read this file as UTF-8 text.")
with col2:
    st.info("Tip: Include acceptance criteria, field rules, API examples, user roles, and expected error messages for more precise tests.")

if st.button("Generate QA Deliverables", type="primary", use_container_width=True):
    if not requirement.strip():
        st.error("Enter a requirement or upload a text file first.")
    else:
        cases = generate_cases(requirement, case_count)
        selected_frameworks = frameworks if mode != "Manual test cases only" else []
        code_map = {fw: automation_code(fw, requirement, cases) for fw in selected_frameworks}
        st.session_state["cases"] = cases
        st.session_state["code_map"] = code_map
        st.session_state["requirement"] = requirement
        st.session_state["mode"] = mode

if "cases" in st.session_state:
    cases = st.session_state["cases"]
    code_map = st.session_state["code_map"]
    st.success(f"Generated {len(cases)} baseline manual scenarios and {len(code_map)} framework template(s). Review assumptions before use.")
    tab1, tab2, tab3 = st.tabs(["Manual Test Cases", "Automation Scripts", "Coverage & Notes"])
    with tab1:
        st.dataframe(cases, use_container_width=True, hide_index=True)
        csv_bytes = io.StringIO()
        import csv
        writer = csv.DictWriter(csv_bytes, fieldnames=list(cases[0].keys())); writer.writeheader(); writer.writerows(cases)
        st.download_button("Download manual cases (CSV)", csv_bytes.getvalue().encode("utf-8-sig"), "manual_test_cases.csv", "text/csv")
    with tab2:
        if not code_map:
            st.info("Choose one or more frameworks and generate again to include automation scripts.")
        for fw, code in code_map.items():
            st.subheader(fw)
            language = "json" if fw == "Postman Collection" else ("typescript" if "TypeScript" in fw else "java")
            st.code(code, language=language)
            filename = {"Selenium + Java + TestNG":"selenium_testng_starter.java", "Playwright + TypeScript":"playwright_starter.spec.ts", "REST Assured + Java":"rest_assured_starter.java", "Postman Collection":"postman_collection.json"}[fw]
            st.download_button(f"Download {fw} starter", code, filename, key=f"download_{fw}")
    with tab3:
        st.markdown("**Coverage generated:** positive flow, required fields, invalid input, boundaries, null/empty data, duplicate submission, error recovery, authorization, persistence, usability, session timeout, regression, concurrency, and audit/logging.")
        st.markdown("**Important limitations**")
        st.markdown("- This first version uses generic templates; it does not semantically understand every requirement yet.\n- Replace all placeholder URLs, selectors, payloads, expected status codes, and assertions.\n- The code has not been executed against your application.\n- Add exact acceptance criteria to improve the expected results; do not treat generic assumptions as approved requirements.")
    workbook = make_workbook(cases, code_map, st.session_state["requirement"])
    st.download_button("📥 Download Excel workbook (.xlsx)", workbook, "qa_test_case_generator.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary", use_container_width=True)
else:
    st.markdown("### What you'll get")
    c1, c2, c3 = st.columns(3)
    c1.metric("Manual scenarios", "6–14")
    c2.metric("Frameworks", "4 supported")
    c3.metric("Excel sheets", "4")
    st.caption("Workbook tabs: Manual Test Cases, Automation Scenarios, Traceability, and Read Me.")
