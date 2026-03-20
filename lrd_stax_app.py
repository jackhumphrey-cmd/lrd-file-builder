import pandas as pd
import streamlit as st
import re

st.set_page_config(
    page_title="💳 LRD Migration Schedule Builder",
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

/* ── Page title ── */
.page-header {
    padding: 1.8rem 0 0.5rem;
}
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

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid rgba(11,126,163,0.1) !important;
}
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown p {
    color: #0d2d3d !important;
}
[data-testid="stSidebarHeader"] { display: none; }

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid rgba(11,126,163,0.1);
    border-radius: 14px;
    padding: 1.4rem 1.6rem !important;
    box-shadow: 0 1px 3px rgba(11,126,163,0.05), 0 4px 12px rgba(11,126,163,0.06);
}
[data-testid="stMetricLabel"] {
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: unset !important;
    line-height: 1.35 !important;
    margin-bottom: 0.4rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.68rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    color: #7aaabb !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.4rem !important;
    font-weight: 700 !important;
    color: #0d2d3d !important;
}

/* ── Section headings ── */
h2, h3 {
    font-family: 'Syne', sans-serif !important;
    color: #0d2d3d !important;
    letter-spacing: -0.02em !important;
}

/* ── File uploaders ── */
[data-testid="stFileUploader"] {
    border: 1px solid rgba(11,126,163,0.2) !important;
    border-radius: 12px !important;
    padding: 0.5rem 0.75rem !important;
    background: rgba(240,247,251,0.6) !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(11,126,163,0.4) !important;
}

/* ── Alerts ── */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    border-left-color: #0b7ea3 !important;
}

/* ── Buttons ── */
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

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border-radius: 14px !important;
    overflow: hidden;
    border: 1px solid rgba(11,126,163,0.1) !important;
    box-shadow: 0 1px 3px rgba(11,126,163,0.04) !important;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: #0b7ea3 !important; }

/* ── Footer ── */
.hub-footer {
    text-align: center;
    margin-top: 2.5rem;
    font-size: 0.71rem;
    color: #a8c8d8;
    letter-spacing: 0.04em;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
    <div class="page-badge">LRD Internal Tools</div>
    <h1 class="page-title">Migration <span>Schedule Builder</span></h1>
    <p class="page-sub">Generate recurring schedule migration files from Token, Schedule, and Mapping files.</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Sidebar Uploads
# -----------------------------
st.sidebar.header("Upload Files")
token_file = st.sidebar.file_uploader("Token File (CSV)", type=["csv"])
schedule_file = st.sidebar.file_uploader("Schedule File (CSV)", type=["csv"])
mapping_file = st.sidebar.file_uploader("Mapping File (CSV)", type=["csv"])
st.sidebar.markdown("---")

if not token_file or not schedule_file or not mapping_file:
    st.sidebar.warning("Please upload all three files to proceed.")

if token_file and schedule_file and mapping_file:
    st.sidebar.success("All files uploaded")

    with st.spinner("Processing data..."):

        # -----------------------------
        # Load Token File
        # -----------------------------
        tokens = pd.read_csv(token_file)
        tokens["source_old_id"] = tokens.get("old_id", tokens.get("source_old_id")).astype(str).str.strip()
        tokens_unique = tokens.groupby("source_old_id", as_index=False).agg({
            "created_customer": "first",
            "source_new_id": "first"
        })

        # -----------------------------
        # Load Schedule File
        # -----------------------------
        schedule = pd.read_csv(schedule_file)
        schedule["Gateway_PaymentTokenId"] = schedule["Gateway_PaymentTokenId"].astype(str).str.strip()

        # -----------------------------
        # Load Mapping File safely
        # -----------------------------
        mapping_df = pd.read_csv(mapping_file)

        expected_cols = ["reference_token", "stax_payment_method_id"]
        for col in expected_cols:
            if col not in mapping_df.columns:
                st.error(f"Mapping file is missing required column: '{col}'")
                st.stop()

        mapping_df = mapping_df.rename(columns={
            "reference_token": "old_id",
            "stax_payment_method_id": "Gateway_PaymentTokenId"
        })
        mapping_df["old_id"] = mapping_df["old_id"].astype(str).str.strip()
        mapping_df["Gateway_PaymentTokenId"] = mapping_df["Gateway_PaymentTokenId"].astype(str).str.strip()

        # -----------------------------
        # Build lookup for first-successful mapping
        # -----------------------------
        gateway_to_token_rows = {}
        for idx, row in mapping_df.iterrows():
            gateway = row["Gateway_PaymentTokenId"]
            if gateway not in gateway_to_token_rows:
                gateway_to_token_rows[gateway] = []
            gateway_to_token_rows[gateway].append(row)

        # -----------------------------
        # Map tokens for each schedule row
        # -----------------------------
        created_customers = []
        source_new_ids = []

        for _, sched_row in schedule.iterrows():
            gateway = str(sched_row["Gateway_PaymentTokenId"])
            mapped = False
            if gateway in gateway_to_token_rows:
                for map_row in gateway_to_token_rows[gateway]:
                    old_id = str(map_row["old_id"])
                    token_match = tokens_unique[tokens_unique["source_old_id"] == old_id]
                    if not token_match.empty:
                        created_customers.append(token_match["created_customer"].values[0])
                        source_new_ids.append(token_match["source_new_id"].values[0])
                        mapped = True
                        break
            if not mapped:
                created_customers.append(None)
                source_new_ids.append(None)

        schedule["created_customer"] = created_customers
        schedule["source_new_id"] = source_new_ids

        schedule = schedule[schedule["created_customer"].notna()]

        # -----------------------------
        # Remove cancelled schedules
        # -----------------------------
        if "Schedule_Status" in schedule.columns:
            schedule = schedule[schedule["Schedule_Status"].str.upper() != "CANCELLED"]

        # -----------------------------
        # Convert TenderType values
        # -----------------------------
        schedule["TenderType"] = schedule["TenderType"].replace({"CC": "Credit"})

        # -----------------------------
        # Format NextPaymentDate
        # -----------------------------
        if "Schedule_NextChargeDate" in schedule.columns:
            schedule["Schedule_NextChargeDate"] = pd.to_datetime(
                schedule["Schedule_NextChargeDate"], errors="coerce"
            ).dt.strftime("%m/%d/%Y")

        # -----------------------------
        # Initialize output
        # -----------------------------
        output = pd.DataFrame()
        mapping = {
            "FirstName": "Donor_FirstName",
            "LastName": "Donor_LastName",
            "Email": "Donor_EmailAddress",
            "PaymentMethodType": "TenderType",
            "PaymentMethodId": "source_new_id",
            "Amount": "Schedule_Amount",
            "Currency": "Schedule_Currency",
            "Frequency": "Schedule_Frequency",
            "NextPaymentDate": "Schedule_NextChargeDate",
            "LegacyId": "RD_Schedule_Id",
            "CustomerId": "created_customer",
            "SegmentCode": "Schedule_Meta_MotivationCode",
            "PlatformReferenceId": "RD_Schedule_Id"
        }

        for out_col, source_col in mapping.items():
            output[out_col] = schedule[source_col] if source_col in schedule else ""

        output["DonorPaidCosts"] = False

        # -----------------------------
        # Detect fund/project splits
        # -----------------------------
        fund_pattern = re.compile(r"Fund(\d+)_Code")
        fund_numbers = sorted([
            int(fund_pattern.match(col).group(1))
            for col in schedule.columns
            if fund_pattern.match(col)
        ])
        max_funds = max(fund_numbers) if fund_numbers else 0

        for i in range(1, max_funds + 1):
            code_col = f"Fund{i}_Code"
            name_col = f"Fund{i}_Name"
            amount_col = f"Fund{i}_Amount"

            output[f"Project{i}Code"] = schedule[code_col] if code_col in schedule else ""
            output[f"Project{i}Name"] = schedule[name_col] if name_col in schedule else ""
            output[f"Project{i}Amount"] = schedule[amount_col] if amount_col in schedule else ""

        # -----------------------------
        # Remove CREDITCARDCOSTS and adjust Amount
        # -----------------------------
        for i in range(1, max_funds + 1):
            code_col = f"Project{i}Code"
            name_col = f"Project{i}Name"
            amount_col = f"Project{i}Amount"

            if code_col in output.columns:
                mask = output[code_col] == "CREDITCARDCOSTS"
                cc_costs = pd.to_numeric(output.loc[mask, amount_col], errors="coerce").fillna(0)
                output.loc[mask, "Amount"] = (
                    pd.to_numeric(output.loc[mask, "Amount"], errors="coerce") - cc_costs
                ).round(2)
                output.loc[mask, [code_col, name_col, amount_col]] = ""
                output.loc[mask, "DonorPaidCosts"] = True

        # -----------------------------
        # Calculate total of remaining project splits
        # -----------------------------
        project_amount_cols = [col for col in output.columns if "Project" in col and "Amount" in col]
        if project_amount_cols:
            output["ProjectTotal"] = output[project_amount_cols].apply(pd.to_numeric, errors="coerce").sum(axis=1)
        else:
            output["ProjectTotal"] = 0

        # -----------------------------
        # Identify mismatched splits
        # -----------------------------
        output["AmountMismatch"] = pd.to_numeric(output["Amount"], errors="coerce") != output["ProjectTotal"]

    # -----------------------------
    # Migration Summary Dashboard
    # -----------------------------
    st.subheader("Migration Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Schedules Processed", len(output))
    missing_tokens = output["PaymentMethodId"].isna().sum()
    col2.metric("Missing Tokens", missing_tokens)
    mismatched_splits = output["AmountMismatch"].sum()
    col3.metric("Split / Amount Mismatches", mismatched_splits)

    # -----------------------------
    # Data Quality Report
    # -----------------------------
    st.subheader("Data Quality Report")
    if missing_tokens > 0:
        st.error(f"{missing_tokens} schedules are missing payment tokens")
    if mismatched_splits > 0:
        st.warning(f"{mismatched_splits} schedules have project splits that do not equal the schedule amount")
    if missing_tokens == 0 and mismatched_splits == 0:
        st.success("No major data issues detected")

    # -----------------------------
    # Output preview
    # -----------------------------
    st.subheader("Output Preview")
    st.dataframe(output, use_container_width=True)

    # -----------------------------
    # Download full migration file
    # -----------------------------
    csv = output.to_csv(index=False).encode("utf-8")
    st.download_button("Download Migration File", csv, "recurring_schedule_import.csv", "text/csv")

    # -----------------------------
    # Download problem rows
    # -----------------------------
    problem_rows = output[(output["AmountMismatch"]) | (output["PaymentMethodId"].isna())]
    if len(problem_rows) > 0:
        st.subheader("Download Problem Rows")
        problem_csv = problem_rows.to_csv(index=False).encode("utf-8")
        st.download_button("Download Problem Rows", problem_csv, "migration_problem_rows.csv", "text/csv")

st.markdown("""
<div class="hub-footer">
    Built for efficient recurring data migrations &nbsp;·&nbsp; LRD Tools
</div>
""", unsafe_allow_html=True)
