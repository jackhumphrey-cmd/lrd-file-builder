import pandas as pd
import streamlit as st
import re

# ----------------------------
# App Config
# ----------------------------
st.set_page_config(
    page_title="LRD Migration Schedule Builder",
    page_icon="💳",
    layout="wide"
)

st.title("💳 LRD Migration Schedule Builder")
st.markdown("Generate recurring schedule migration files from legacy exports.")

# ----------------------------
# Landing Page: Choose workflow
# ----------------------------
workflow = st.radio(
    "Select Migration Type:",
    ["Stripe/Authorize.net Migration", "Stax Migration"]
)

st.markdown("---")

# ----------------------------
# Helper Functions
# ----------------------------
def process_output(merged, token_col, customer_col):
    """Process merged schedule + token data into final output with project splits, CREDITCARDCOSTS handling, etc."""
    output = pd.DataFrame()
    mapping = {
        "FirstName": "Donor_FirstName",
        "LastName": "Donor_LastName",
        "Email": "Donor_EmailAddress",
        "PaymentMethodType": "TenderType",
        "PaymentMethodId": token_col,
        "Amount": "Schedule_Amount",
        "Currency": "Schedule_Currency",
        "Frequency": "Schedule_Frequency",
        "NextPaymentDate": "Schedule_NextChargeDate",
        "LegacyId": "RD_Schedule_Id",
        "CustomerId": customer_col,
        "SegmentCode": "Schedule_Meta_MotivationCode",
        "PlatformReferenceId": "RD_Schedule_Id"
    }

    # Map columns
    for out_col, source_col in mapping.items():
        output[out_col] = merged[source_col] if source_col in merged else ""

    # Default DonorPaidCosts
    output["DonorPaidCosts"] = False

    # Detect project splits
    fund_pattern = re.compile(r"Fund(\d+)_Code")
    fund_numbers = sorted([
        int(fund_pattern.match(col).group(1))
        for col in merged.columns if fund_pattern.match(col)
    ])
    max_funds = max(fund_numbers) if fund_numbers else 0

    for i in range(1, max_funds + 1):
        code_col = f"Fund{i}_Code"
        name_col = f"Fund{i}_Name"
        amount_col = f"Fund{i}_Amount"

        output[f"Project{i}Code"] = merged[code_col] if code_col in merged else ""
        output[f"Project{i}Name"] = merged[name_col] if name_col in merged else ""
        output[f"Project{i}Amount"] = merged[amount_col] if amount_col in merged else ""

    # Handle CREDITCARDCOSTS
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

    # Calculate total of remaining project splits
    project_amount_cols = [col for col in output.columns if "Project" in col and "Amount" in col]
    output["ProjectTotal"] = output[project_amount_cols].apply(pd.to_numeric, errors="coerce").sum(axis=1) if project_amount_cols else 0

    # Identify mismatched splits
    output["AmountMismatch"] = pd.to_numeric(output["Amount"], errors="coerce") != output["ProjectTotal"]

    return output

def display_dashboard(output):
    """Show metrics and preview"""
    st.subheader("Migration Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Schedules Processed", len(output))
    missing_tokens = output["PaymentMethodId"].isna().sum()
    col2.metric("Missing Tokens", missing_tokens)
    mismatched_splits = output["AmountMismatch"].sum()
    col3.metric("Split / Amount Mismatches", mismatched_splits)

    st.subheader("Data Quality Report")
    if missing_tokens > 0:
        st.error(f"{missing_tokens} schedules are missing payment tokens")
    if mismatched_splits > 0:
        st.warning(f"{mismatched_splits} schedules have project splits that do not equal the schedule amount")
    if missing_tokens == 0 and mismatched_splits == 0:
        st.success("No major data issues detected")

    st.subheader("Output Preview")
    st.dataframe(output, use_container_width=True)

    csv = output.to_csv(index=False).encode("utf-8")
    st.download_button("Download Migration File", csv, "recurring_schedule_import.csv", "text/csv")

    problem_rows = output[(output["AmountMismatch"]) | (output["PaymentMethodId"].isna())]
    if len(problem_rows) > 0:
        st.subheader("Download Problem Rows")
        st.download_button("Download Problem Rows", problem_rows.to_csv(index=False).encode("utf-8"), "migration_problem_rows.csv", "text/csv")

# ----------------------------
# Stripe/Authorize.net Workflow
# ----------------------------
if workflow == "Stripe/Authorize.net Migration":
    st.subheader("Stripe/Authorize.net Migration")
    token_file = st.file_uploader("Token File", type=["csv"], key="stripe_token")
    schedule_file = st.file_uploader("Schedule File", type=["csv", "xlsx"], key="stripe_schedule")

    if token_file and schedule_file:
        with st.spinner("Processing Stripe/Authorize.net migration..."):
            tokens = pd.read_csv(token_file)
            if schedule_file.name.endswith(".csv"):
                schedule = pd.read_csv(schedule_file)
            else:
                schedule = pd.read_excel(schedule_file)

            merged = schedule.merge(
                tokens[["source_old_id", "created_customer", "source_new_id"]],
                left_on="Gateway_PaymentTokenId",
                right_on="source_old_id",
                how="left"
            ).drop(columns=["source_old_id"])

            if "Schedule_Status" in merged.columns:
                merged = merged[merged["Schedule_Status"].str.upper() != "CANCELLED"]

            merged["TenderType"] = merged["TenderType"].replace({"CC": "Credit"})

            if "Schedule_NextChargeDate" in merged.columns:
                merged["Schedule_NextChargeDate"] = pd.to_datetime(
                    merged["Schedule_NextChargeDate"], errors="coerce"
                ).dt.strftime("%m/%d/%Y")

            output = process_output(merged, "source_new_id", "created_customer")
            display_dashboard(output)

# ----------------------------
# Stax Workflow
# ----------------------------
elif workflow == "Stax Migration":
    st.subheader("Stax Migration")
    stax_token = st.file_uploader("Token File", type=["csv"], key="stax_token")
    stax_schedule = st.file_uploader("Schedule File", type=["csv"], key="stax_schedule")
    stax_mapping = st.file_uploader("Mapping File", type=["csv"], key="stax_mapping")

    if stax_token and stax_schedule and stax_mapping:
        st.session_state.stax_token = stax_token
        st.session_state.stax_schedule = stax_schedule
        st.session_state.stax_mapping = stax_mapping

        import stax_workflow  # Runs the full Stax workflow using uploaded session state
