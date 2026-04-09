import pandas as pd
import streamlit as st
import re
import json
import requests

st.set_page_config(
    page_title="LRD Migration Schedule Builder",
    page_icon="💳",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: #f0f7fb;
    background-image:
        radial-gradient(ellipse 70% 40% at 55% 0%, rgba(26,140,181,0.18) 0%, transparent 65%),
        radial-gradient(ellipse 40% 30% at 5% 95%, rgba(11,126,163,0.1) 0%, transparent 60%);
}

#MainMenu, footer, header { visibility: hidden; }

.page-header { padding: 1.8rem 0 0.5rem; }
.page-badge {
    display: inline-block;
    background: rgba(11,126,163,0.1);
    border: 1px solid rgba(11,126,163,0.25);
    color: #0b7ea3;
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 0.3rem 0.85rem;
    border-radius: 999px;
    margin-bottom: 0.9rem;
}
.page-title {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: #0d2d3d;
    letter-spacing: -0.03em;
    margin: 0 0 0.4rem;
    line-height: 1.15;
}
.page-title span {
    background: linear-gradient(135deg, #0b7ea3 0%, #1ab5d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.page-sub {
    font-size: 0.88rem;
    color: #6a8fa0;
    font-weight: 300;
    margin: 0 0 1.5rem;
}

[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid rgba(11,126,163,0.1) !important;
}
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown p { color: #0d2d3d !important; }
[data-testid="stSidebarHeader"] { display: none; }

[data-testid="stFileUploader"] {
    border: 1px solid rgba(11,126,163,0.2) !important;
    border-radius: 12px !important;
    padding: 0.5rem 0.75rem !important;
    background: rgba(240,247,251,0.6) !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(11,126,163,0.4) !important;
}

[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid rgba(11,126,163,0.1);
    border-radius: 14px;
    padding: 1.4rem 1.6rem !important;
    box-shadow: 0 1px 3px rgba(11,126,163,0.05), 0 4px 12px rgba(11,126,163,0.06);
}
[data-testid="stMetricLabel"] {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.68rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    color: #7aaabb !important;
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: unset !important;
    line-height: 1.35 !important;
    margin-bottom: 0.4rem !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.4rem !important;
    font-weight: 700 !important;
    color: #0d2d3d !important;
}

h2, h3 {
    font-family: 'Syne', sans-serif !important;
    color: #0d2d3d !important;
    letter-spacing: -0.02em !important;
}

[data-testid="stAlert"] {
    border-radius: 12px !important;
    border-left-color: #0b7ea3 !important;
}

.stDownloadButton button, .stButton button {
    background: linear-gradient(135deg, #0b7ea3 0%, #1a8cb5 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 9px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 0.5rem 1.2rem !important;
    box-shadow: 0 2px 8px rgba(11,126,163,0.28) !important;
    transition: opacity 0.2s !important;
}
.stDownloadButton button:hover, .stButton button:hover {
    opacity: 0.88 !important;
    box-shadow: 0 4px 14px rgba(11,126,163,0.38) !important;
}

[data-testid="stDataFrame"] {
    border-radius: 14px !important;
    overflow: hidden;
    border: 1px solid rgba(11,126,163,0.1) !important;
    box-shadow: 0 1px 3px rgba(11,126,163,0.04) !important;
}

.stSpinner > div { border-top-color: #0b7ea3 !important; }

.hub-footer {
    text-align: center;
    margin-top: 2.5rem;
    font-size: 0.71rem;
    color: #a8c8d8;
    letter-spacing: 0.04em;
}

.confidence-high   { color: #0b7ea3; font-weight: 500; font-size: 0.75rem; }
.confidence-medium { color: #e0983a; font-weight: 500; font-size: 0.75rem; }
.confidence-low    { color: #c0392b; font-weight: 500; font-size: 0.75rem; }
.unmapped-warning  { color: #c0392b; font-size: 0.75rem; font-style: italic; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
    <div class="page-badge">LRD Internal Tools</div>
    <h1 class="page-title">Migration <span>Schedule Builder</span></h1>
    <p class="page-sub">Generate recurring schedule migration files from legacy exports.</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Destination template fields
# -----------------------------
DESTINATION_FIELDS = [
    "FirstName", "LastName", "Email",
    "PaymentMethodType", "PaymentMethodId",
    "Amount", "Currency", "Frequency", "NextPaymentDate",
    "LegacyId", "CustomerId", "SegmentCode", "PlatformReferenceId",
    "DonorPaidCosts",
]

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"

# -----------------------------
# AI Mapping Function
# -----------------------------
def get_ai_mapping(source_columns: list, sample_rows: list) -> dict:
    sample_str = json.dumps(sample_rows[:3], indent=2)
    cols_str   = json.dumps(source_columns, indent=2)

    prompt = f"""You are a data migration expert. Your job is to map columns from a legacy schedule export file to a fixed destination template.

DESTINATION FIELDS (fixed — do not change these):
{json.dumps(DESTINATION_FIELDS, indent=2)}

Also map fund/project split columns. The destination uses Project1Code, Project1Name, Project1Amount, Project2Code, etc. Map any source columns that look like fund codes, fund names, or fund amounts to these.

SOURCE FILE COLUMNS:
{cols_str}

SAMPLE DATA (first 3 rows):
{sample_str}

INSTRUCTIONS:
- For each destination field, identify the best matching source column.
- If no good match exists, return null for that field.
- Also return a confidence level: "High", "Medium", or "Low".
- For fund/project columns, return a separate "fund_mappings" array.
- Return ONLY valid JSON. No explanation, no markdown, no preamble.

Return this exact structure:
{{
  "mappings": {{
    "FirstName":            {{"source": "ColumnName or null", "confidence": "High|Medium|Low"}},
    "LastName":             {{"source": "ColumnName or null", "confidence": "High|Medium|Low"}},
    "Email":                {{"source": "ColumnName or null", "confidence": "High|Medium|Low"}},
    "PaymentMethodType":    {{"source": "ColumnName or null", "confidence": "High|Medium|Low"}},
    "PaymentMethodId":      {{"source": "ColumnName or null", "confidence": "High|Medium|Low"}},
    "Amount":               {{"source": "ColumnName or null", "confidence": "High|Medium|Low"}},
    "Currency":             {{"source": "ColumnName or null", "confidence": "High|Medium|Low"}},
    "Frequency":            {{"source": "ColumnName or null", "confidence": "High|Medium|Low"}},
    "NextPaymentDate":      {{"source": "ColumnName or null", "confidence": "High|Medium|Low"}},
    "LegacyId":             {{"source": "ColumnName or null", "confidence": "High|Medium|Low"}},
    "CustomerId":           {{"source": "ColumnName or null", "confidence": "High|Medium|Low"}},
    "SegmentCode":          {{"source": "ColumnName or null", "confidence": "High|Medium|Low"}},
    "PlatformReferenceId":  {{"source": "ColumnName or null", "confidence": "High|Medium|Low"}},
    "DonorPaidCosts":       {{"source": "ColumnName or null", "confidence": "High|Medium|Low"}}
  }},
  "fund_mappings": [
    {{"index": 1, "code": "ColumnName or null", "name": "ColumnName or null", "amount": "ColumnName or null"}}
  ]
}}"""

    response = requests.post(
        ANTHROPIC_API_URL,
        headers={
            "Content-Type": "application/json",
            "x-api-key": st.secrets["ANTHROPIC_API_KEY"],
            "anthropic-version": "2023-06-01"
        },
        json={
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": prompt}]
        }
    )

    raw = response.json()["content"][0]["text"].strip()
    raw = re.sub(r"^```json|^```|```$", "", raw, flags=re.MULTILINE).strip()
    return json.loads(raw)

# -----------------------------
# Sidebar Uploads
# -----------------------------
st.sidebar.header("Upload Files")
token_file    = st.sidebar.file_uploader("Token File (CSV)", type=["csv"])
schedule_file = st.sidebar.file_uploader("Schedule File", type=["csv", "xlsx"])
st.sidebar.markdown("---")

if not token_file or not schedule_file:
    st.sidebar.warning("Waiting for files")
    st.stop()

st.sidebar.success("Files uploaded")

# -----------------------------
# Load Files
# -----------------------------
with st.spinner("Loading files..."):
    tokens = pd.read_csv(token_file, dtype=str, keep_default_na=False)

    if schedule_file.name.endswith(".csv"):
        schedule = pd.read_csv(schedule_file, dtype=str, keep_default_na=False)
    else:
        schedule = pd.read_excel(schedule_file, dtype=str)

    source_columns = schedule.columns.tolist()
    sample_rows    = schedule.head(3).to_dict(orient="records")

# -----------------------------
# Step 1 — Raw File Preview
# -----------------------------
st.subheader("Source File Preview")
st.dataframe(schedule.head(10), use_container_width=True)
st.write("")

# -----------------------------
# Step 2 — AI Mapping
# -----------------------------
if "ai_mapping" not in st.session_state:
    with st.spinner("Analysing columns with AI..."):
        try:
            st.session_state.ai_mapping = get_ai_mapping(source_columns, sample_rows)
        except Exception as e:
            st.error(f"AI mapping failed: {e}")
            st.stop()

ai_result    = st.session_state.ai_mapping
ai_mappings  = ai_result.get("mappings", {})
ai_fund_maps = ai_result.get("fund_mappings", [])

# -----------------------------
# Step 3 — Review & Edit Mapping
# -----------------------------
st.subheader("Column Mapping")
st.info("Review the AI-suggested mappings below. Adjust any dropdowns before generating the output.")

blank_option      = "— please select —"
column_options    = [blank_option] + source_columns
confirmed_mapping = {}

CONFIDENCE_LABELS = {
    "High":   ("✅ High",    "confidence-high"),
    "Medium": ("⚠️ Medium", "confidence-medium"),
    "Low":    ("🔴 Low",    "confidence-low"),
    None:     ("— Unmapped", "unmapped-warning"),
}

# Core fields
st.markdown("#### Core Fields")
cols_per_row  = 3
field_chunks  = [DESTINATION_FIELDS[i:i+cols_per_row] for i in range(0, len(DESTINATION_FIELDS), cols_per_row)]

for chunk in field_chunks:
    row_cols = st.columns(cols_per_row)
    for col_ui, field in zip(row_cols, chunk):
        with col_ui:
            ai_info    = ai_mappings.get(field, {})
            suggested  = ai_info.get("source")
            confidence = ai_info.get("confidence")

            conf_label, conf_class = CONFIDENCE_LABELS.get(
                confidence if suggested else None,
                ("— Unmapped", "unmapped-warning")
            )

            default_idx = (
                column_options.index(suggested)
                if suggested and suggested in column_options
                else 0
            )

            st.markdown(f'<span class="{conf_class}">{conf_label}</span>', unsafe_allow_html=True)
            selected = st.selectbox(
                field,
                options=column_options,
                index=default_idx,
                key=f"map_{field}"
            )
            confirmed_mapping[field] = selected if selected != blank_option else None

# Fund/project split fields
st.markdown("#### Fund / Project Split Fields")
st.caption("Map fund code, name, and amount columns for each project split detected in the source file.")

confirmed_fund_mappings = []
num_funds = max(len(ai_fund_maps), 1)

for i in range(1, num_funds + 1):
    ai_fund = next((f for f in ai_fund_maps if f.get("index") == i), {})
    st.markdown(f"**Fund {i}**")
    f_cols = st.columns(3)

    fund_entry = {}
    for col_ui, sub_field, ai_key in zip(f_cols, ["Code", "Name", "Amount"], ["code", "name", "amount"]):
        with col_ui:
            suggested   = ai_fund.get(ai_key)
            default_idx = (
                column_options.index(suggested)
                if suggested and suggested in column_options
                else 0
            )
            selected = st.selectbox(
                f"Project{i}{sub_field}",
                options=column_options,
                index=default_idx,
                key=f"fund_{i}_{sub_field}"
            )
            fund_entry[sub_field.lower()] = selected if selected != blank_option else None

    confirmed_fund_mappings.append({"index": i, **fund_entry})

# Unmapped field warning
unmapped = [f for f, v in confirmed_mapping.items() if v is None]
if unmapped:
    st.warning(f"The following fields are unmapped and will be left blank in the output: {', '.join(unmapped)}")

st.write("")

# -----------------------------
# Step 4 — Generate Output
# -----------------------------
if st.button("Generate Migration File"):

    with st.spinner("Building output..."):

        # Merge token data
        payment_id_col = confirmed_mapping.get("PaymentMethodId")
        merged = schedule.merge(
            tokens[["source_old_id", "created_customer", "source_new_id"]],
            left_on=payment_id_col,
            right_on="source_old_id",
            how="left"
        ).drop(columns=["source_old_id"], errors="ignore")

        # Remove cancelled schedules
        status_candidates = [c for c in merged.columns if "status" in c.lower()]
        if status_candidates:
            status_col = status_candidates[0]
            merged = merged[merged[status_col].str.upper() != "CANCELLED"]

        # Build output
        output = pd.DataFrame()

        for dest_field, source_col in confirmed_mapping.items():
            if dest_field in ("PaymentMethodId", "CustomerId"):
                continue
            if source_col and source_col in merged.columns:
                output[dest_field] = merged[source_col]
            else:
                output[dest_field] = ""

        # Token-derived fields
        output["PaymentMethodId"] = merged.get("source_new_id", "")
        output["CustomerId"]      = merged.get("created_customer", "")

        # PaymentMethodType normalisation
        if "PaymentMethodType" in output.columns:
            output["PaymentMethodType"] = output["PaymentMethodType"].replace({"CC": "Credit"})

        # NextPaymentDate formatting
        if "NextPaymentDate" in output.columns:
            output["NextPaymentDate"] = pd.to_datetime(
                output["NextPaymentDate"], errors="coerce"
            ).dt.strftime("%m/%d/%Y")

        # Default DonorPaidCosts
        output["DonorPaidCosts"] = False

        # Fund/project splits
        for fund in confirmed_fund_mappings:
            i          = fund["index"]
            code_src   = fund.get("code")
            name_src   = fund.get("name")
            amount_src = fund.get("amount")

            output[f"Project{i}Code"]   = merged[code_src]   if code_src   and code_src   in merged.columns else ""
            output[f"Project{i}Name"]   = merged[name_src]   if name_src   and name_src   in merged.columns else ""
            output[f"Project{i}Amount"] = merged[amount_src] if amount_src and amount_src in merged.columns else ""

        # Remove CREDITCARDCOSTS and adjust Amount
        project_amount_cols = [c for c in output.columns if re.match(r"Project\d+Amount", c)]
        for i in range(1, len(confirmed_fund_mappings) + 1):
            code_col   = f"Project{i}Code"
            name_col   = f"Project{i}Name"
            amount_col = f"Project{i}Amount"
            if code_col in output.columns:
                mask     = output[code_col] == "CREDITCARDCOSTS"
                cc_costs = pd.to_numeric(output.loc[mask, amount_col], errors="coerce").fillna(0)
                output.loc[mask, "Amount"] = (
                    pd.to_numeric(output.loc[mask, "Amount"], errors="coerce") - cc_costs
                ).round(2)
                output.loc[mask, [code_col, name_col, amount_col]] = ""
                output.loc[mask, "DonorPaidCosts"] = True

        # Split mismatch detection
        if project_amount_cols:
            output["ProjectTotal"]   = output[project_amount_cols].apply(pd.to_numeric, errors="coerce").sum(axis=1)
            output["AmountMismatch"] = pd.to_numeric(output["Amount"], errors="coerce") != output["ProjectTotal"]
        else:
            output["ProjectTotal"]   = 0
            output["AmountMismatch"] = False

    # -----------------------------
    # Summary Dashboard
    # -----------------------------
    st.subheader("Migration Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Schedules Processed", len(output))
    missing_tokens    = (output["PaymentMethodId"] == "").sum()
    mismatched_splits = output["AmountMismatch"].sum()
    col2.metric("Missing Tokens", missing_tokens)
    col3.metric("Split / Amount Mismatches", mismatched_splits)

    st.subheader("Data Quality Report")
    if missing_tokens > 0:
        st.error(f"{missing_tokens} schedules are missing payment tokens.")
    if mismatched_splits > 0:
        st.warning(f"{mismatched_splits} schedules have project splits that do not equal the schedule amount.")
    if missing_tokens == 0 and mismatched_splits == 0:
        st.success("No major data issues detected.")

    st.subheader("Output Preview")
    display_cols = [c for c in output.columns if c not in ("ProjectTotal", "AmountMismatch")]
    st.dataframe(output[display_cols], use_container_width=True)

    # -----------------------------
    # Downloads
    # -----------------------------
    clean_output = output.drop(columns=["ProjectTotal", "AmountMismatch"], errors="ignore")
    st.download_button(
        "Download Migration File",
        clean_output.to_csv(index=False).encode("utf-8"),
        "recurring_schedule_import.csv",
        "text/csv"
    )

    problem_rows = output[(output["AmountMismatch"]) | (output["PaymentMethodId"] == "")]
    if len(problem_rows) > 0:
        st.subheader("Download Problem Rows")
        st.download_button(
            "Download Problem Rows",
            problem_rows.drop(columns=["ProjectTotal", "AmountMismatch"], errors="ignore").to_csv(index=False).encode("utf-8"),
            "migration_problem_rows.csv",
            "text/csv"
        )

st.markdown("""
<div class="hub-footer">
    Built for efficient recurring data migrations &nbsp;·&nbsp; LRD Tools
</div>
""", unsafe_allow_html=True)
