import pandas as pd
import streamlit as st
import re

st.set_page_config(
    page_title="LRD Migration Schedule Builder",
    page_icon="💳",
    layout="wide"
)

st.title("LRD Migration Schedule Builder")
st.markdown("Generate recurring schedule migration files from legacy exports.")

# Sidebar Uploads
st.sidebar.header("Upload Files")
token_file = st.sidebar.file_uploader("Token File", type=["csv"])
schedule_file = st.sidebar.file_uploader("Schedule File", type=["csv", "xlsx"])
st.sidebar.markdown("---")

if not token_file or not schedule_file:
    st.sidebar.warning("Waiting for files")

if token_file and schedule_file:

    st.sidebar.success("Files uploaded")

    with st.spinner("Processing data..."):

        # Read files
        tokens = pd.read_csv(token_file)
        if schedule_file.name.endswith(".csv"):
            schedule = pd.read_csv(schedule_file)
        else:
            schedule = pd.read_excel(schedule_file)

        # Merge token data
        merged = schedule.merge(
            tokens[["source_old_id", "created_customer", "source_new_id"]],
            left_on="Gateway_PaymentTokenId",
            right_on="source_old_id",
            how="left"
        ).drop(columns=["source_old_id"])

        # Remove cancelled schedules
        if "Schedule_Status" in merged.columns:
            merged = merged[merged["Schedule_Status"].str.upper() != "CANCELLED"]

        # Convert TenderType values
        merged["TenderType"] = merged["TenderType"].replace({"CC": "Credit"})

        # Format NextPaymentDate
        if "Schedule_NextChargeDate" in merged.columns:
            merged["Schedule_NextChargeDate"] = pd.to_datetime(
                merged["Schedule_NextChargeDate"], errors="coerce"
            ).dt.strftime("%m/%d/%Y")

        # Initialize output
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

        # Map columns
        for out_col, source_col in mapping.items():
            output[out_col] = merged[source_col] if source_col in merged else ""

        # Default DonorPaidCosts
        output["DonorPaidCosts"] = False

        # Detect fund/project splits
        fund_pattern = re.compile(r"Fund(\d+)_Code")
        fund_numbers = sorted([
            int(fund_pattern.match(col).group(1))
            for col in merged.columns
            if fund_pattern.match(col)
        ])
        max_funds = max(fund_numbers) if fund_numbers else 0

        for i in range(1, max_funds + 1):
            code_col = f"Fund{i}_Code"
            name_col = f"Fund{i}_Name"
            amount_col = f"Fund{i}_Amount"

            output[f"Project{i}Code"] = merged[code_col] if code_col in merged else ""
            output[f"Project{i}Name"] = merged[name_col] if name_col in merged else ""
            output[f"Project{i}Amount"] = merged[amount_col] if amount_col in merged else ""

        # Remove CREDITCARDCOSTS and subtract from Schedule Amount
        for i in range(1, max_funds + 1):
            code_col = f"Project{i}Code"
            name_col = f"Project{i}Name"
            amount_col = f"Project{i}Amount"

            if code_col in output.columns:
                mask = output[code_col] == "CREDITCARDCOSTS"

                # Subtract the amount from Schedule Amount
                cc_costs = pd.to_numeric(output.loc[mask, amount_col], errors="coerce").fillna(0)
                output.loc[mask, "Amount"] = (
                    pd.to_numeric(output.loc[mask, "Amount"], errors="coerce") - cc_costs
                ).round(2)

                # Remove the project split
                output.loc[mask, [code_col, name_col, amount_col]] = ""

                # Set DonorPaidCosts flag
                output.loc[mask, "DonorPaidCosts"] = True

        # Calculate total of remaining project splits
        project_amount_cols = [col for col in output.columns if "Project" in col and "Amount" in col]
        if project_amount_cols:
            output["ProjectTotal"] = output[project_amount_cols].apply(pd.to_numeric, errors="coerce").sum(axis=1)
        else:
            output["ProjectTotal"] = 0

        # Identify mismatched splits
        output["AmountMismatch"] = pd.to_numeric(output["Amount"], errors="coerce") != output["ProjectTotal"]

    # Migration Summary Dashboard
    st.subheader("Migration Summary")
    col1, col2, col3 = st.columns(3)

    col1.metric("Schedules Processed", len(output))
    missing_tokens = output["PaymentMethodId"].isna().sum()
    col2.metric("Missing Tokens", missing_tokens)
    mismatched_splits = output["AmountMismatch"].sum()
    col3.metric("Split / Amount Mismatches", mismatched_splits)

    # Data Quality Report
    st.subheader("Data Quality Report")
    if missing_tokens > 0:
        st.error(f"{missing_tokens} schedules are missing payment tokens")
    if mismatched_splits > 0:
        st.warning(f"{mismatched_splits} schedules have project splits that do not equal the schedule amount")
    if missing_tokens == 0 and mismatched_splits == 0:
        st.success("No major data issues detected")

    # Output preview
    st.subheader("Output Preview")
    st.dataframe(output, use_container_width=True)

    # Download full migration file
    csv = output.to_csv(index=False).encode("utf-8")
    st.download_button("Download Migration File", csv, "recurring_schedule_import.csv", "text/csv")

    # Download problem rows
    problem_rows = output[(output["AmountMismatch"]) | (output["PaymentMethodId"].isna())]
    if len(problem_rows) > 0:
        st.subheader("Download Problem Rows")
        problem_csv = problem_rows.to_csv(index=False).encode("utf-8")
        st.download_button("Download Problem Rows", problem_csv, "migration_problem_rows.csv", "text/csv")
