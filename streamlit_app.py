import streamlit as st
import pandas as pd
import re

st.set_page_config(
    page_title="💳 LRD Migration Schedule Builder",
    page_icon="💳",
    layout="wide"
)

st.title("💳 LRD Migration Schedule Builder")
st.markdown("Select the workflow you want to run:")

# -----------------------------
# Landing page selection
# -----------------------------
workflow = st.radio(
    "Choose your migration workflow:",
    ("Stripe/Authorize.net Migration", "Stax Migration")
)

# -----------------------------
# Stripe / Authorize.net workflow
# -----------------------------
if workflow == "Stripe/Authorize.net Migration":
    st.info("Stripe/Authorize.net workflow selected.")

    # Sidebar Uploads
    st.sidebar.header("Upload Files")
    token_file = st.sidebar.file_uploader("Token File (CSV)", type=["csv"])
    schedule_file = st.sidebar.file_uploader("Schedule File (CSV or XLSX)", type=["csv", "xlsx"])
    st.sidebar.markdown("---")

    if not token_file or not schedule_file:
        st.sidebar.warning("Waiting for files")
    if token_file and schedule_file:
        st.sidebar.success("Files uploaded")
        with st.spinner("Processing data..."):
            # --- Load files ---
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

            # --- Initialize output ---
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
                output[out_col] = merged[source_col] if source_col in merged else ""

            output["DonorPaidCosts"] = False

            # --- Handle project splits ---
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

            # Remove CREDITCARDCOSTS
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

            # Project totals and mismatches
            project_amount_cols = [col for col in output.columns if "Project" in col and "Amount" in col]
            output["ProjectTotal"] = output[project_amount_cols].apply(pd.to_numeric, errors="coerce").sum(axis=1) if project_amount_cols else 0
            output["AmountMismatch"] = pd.to_numeric(output["Amount"], errors="coerce") != output["ProjectTotal"]

            # Metrics
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
                problem_csv = problem_rows.to_csv(index=False).encode("utf-8")
                st.download_button("Download Problem Rows", problem_csv, "migration_problem_rows.csv", "text/csv")

# -----------------------------
# Stax workflow
# -----------------------------
elif workflow == "Stax Migration":
    st.info("Stax workflow selected.")

    # Sidebar Uploads
    st.sidebar.header("Upload Files for Stax Migration")
    token_file = st.sidebar.file_uploader("Token File (CSV)", type=["csv"], key="stax_token")
    schedule_file = st.sidebar.file_uploader("Schedule File (CSV)", type=["csv"], key="stax_schedule")
    mapping_file = st.sidebar.file_uploader("Mapping File (CSV)", type=["csv"], key="stax_mapping")
    st.sidebar.markdown("---")

    if not token_file or not schedule_file or not mapping_file:
        st.sidebar.warning("Please upload all three files to proceed.")

    if token_file and schedule_file and mapping_file:
        st.sidebar.success("All files uploaded")
        with st.spinner("Processing Stax data..."):
            # --- Insert Stax code exactly as in your previous snippet ---
            # All logic for first-successful mapping, project splits, CREDITCARDCOSTS, metrics, downloads
            exec(open("stax_processing_code.py").read())  # Example: you can place the Stax snippet in a separate file
