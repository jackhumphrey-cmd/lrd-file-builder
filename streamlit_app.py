import pandas as pd
import streamlit as st
import re

st.set_page_config(
    page_title="💳 LRD Migration Schedule Builder",
    page_icon="💳",
    layout="wide"
)

st.title("💳 LRD Migration Schedule Builder")
st.markdown("Generate recurring schedule migration files from Token, Schedule, and Mapping files.")

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
        tokens["source_old_id"] = tokens.get("old_id", tokens.get("source_old_id")).astype(str).fillna("")
        tokens_unique = tokens.groupby("source_old_id", as_index=False).agg({
            "created_customer": "first",
            "source_new_id": "first"
        })

        # -----------------------------
        # Load Schedule File
        # -----------------------------
        schedule = pd.read_csv(schedule_file)
        schedule["Gateway_PaymentTokenId"] = schedule["Gateway_PaymentTokenId"].astype(str).fillna("")

        # -----------------------------
        # Load Mapping File
        # -----------------------------
        mapping_df = pd.read_csv(mapping_file)
        mapping_df = mapping_df.rename(columns={
            "reference_token": "source_old_id",
            "stax_payment_method_id": "Gateway_PaymentTokenId"
        })
        mapping_df["source_old_id"] = mapping_df["source_old_id"].astype(str).fillna("")
        mapping_df["Gateway_PaymentTokenId"] = mapping_df["Gateway_PaymentTokenId"].astype(str).fillna("")

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
        # Map tokens for each schedule row (first successful match)
        # -----------------------------
        created_customers = []
        source_new_ids = []

        for _, sched_row in schedule.iterrows():
            gateway = str(sched_row["Gateway_PaymentTokenId"])
            mapped = False
            if gateway in gateway_to_token_rows:
                for map_row in gateway_to_token_rows[gateway]:
                    old_id = str(map_row["source_old_id"])
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

        # Drop unmapped rows
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
