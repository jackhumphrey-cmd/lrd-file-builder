import pandas as pd
import streamlit as st
import re

st.set_page_config(
    page_title="LRD Migration Schedule Builder",
    page_icon="💳",
    layout="wide"
)

st.title("💳 LRD Migration Schedule Builder")
st.markdown("Generate recurring schedule migration files from legacy exports.")

# -----------------------------
# Sidebar Uploads
# -----------------------------
st.sidebar.header("Upload Files")
token_file = st.sidebar.file_uploader("Token File", type=["csv"])
schedule_file = st.sidebar.file_uploader("Schedule File", type=["csv", "xlsx"])
mapping_file = st.sidebar.file_uploader("Mapping File (Optional)", type=["csv", "xlsx"])

if not token_file or not schedule_file:
    st.sidebar.warning("Waiting for required files...")

# -----------------------------
# Main Processing
# -----------------------------
if token_file and schedule_file:

    with st.spinner("Processing data..."):

        # Load files
        tokens = pd.read_csv(token_file)

        if schedule_file.name.endswith(".csv"):
            schedule = pd.read_csv(schedule_file)
        else:
            schedule = pd.read_excel(schedule_file)

        # -----------------------------
        # FIX: Ensure no duplicate token columns
        # -----------------------------
        if "source_old_id" not in tokens.columns:
            if "old_id" in tokens.columns:
                tokens = tokens.rename(columns={"old_id": "source_old_id"})
        else:
            if "old_id" in tokens.columns:
                tokens = tokens.drop(columns=["old_id"])

        # Safety check
        if tokens.columns.duplicated().any():
            st.error("Duplicate columns detected in token file")
            st.write(tokens.columns)
            st.stop()

        # -----------------------------
        # Optional Mapping File Logic
        # -----------------------------
        if mapping_file:
            if mapping_file.name.endswith(".csv"):
                mapping_df = pd.read_csv(mapping_file)
            else:
                mapping_df = pd.read_excel(mapping_file)

            st.sidebar.success("Mapping file applied")

            # Ensure correct names
            mapping_df = mapping_df.rename(columns={
                "reference_token": "source_old_id",
                "stax_payment_method_id": "mapped_payment_id"
            })

            # Convert to strings to avoid merge type issues
            schedule["Gateway_PaymentTokenId"] = schedule["Gateway_PaymentTokenId"].astype(str)
            mapping_df["mapped_payment_id"] = mapping_df["mapped_payment_id"].astype(str)
            mapping_df["source_old_id"] = mapping_df["source_old_id"].astype(str)
            tokens["source_old_id"] = tokens["source_old_id"].astype(str)

            # Merge mapping into schedule to replace Gateway_PaymentTokenId
            schedule = schedule.merge(
                mapping_df[["source_old_id", "mapped_payment_id"]],
                left_on="Gateway_PaymentTokenId",
                right_on="source_old_id",
                how="left"
            )

            schedule["Gateway_PaymentTokenId"] = schedule["mapped_payment_id"].combine_first(
                schedule["Gateway_PaymentTokenId"]
            )

            schedule = schedule.drop(columns=["source_old_id", "mapped_payment_id"], errors="ignore")

        else:
            st.sidebar.info("No mapping file (standard processing)")

        # -----------------------------
        # Merge token data
        # -----------------------------
        merged = schedule.merge(
            tokens[["source_old_id", "created_customer", "source_new_id"]],
            left_on="Gateway_PaymentTokenId",
            right_on="source_old_id",
            how="left"
        ).drop(columns=["source_old_id"])

        # -----------------------------
        # Mapping Preview Table
        # -----------------------------
        st.subheader("Token Mapping Preview")
        preview_cols = ["RD_Schedule_Id", "Gateway_PaymentTokenId", "created_customer", "source_new_id"]
        existing_cols = [col for col in preview_cols if col in merged.columns]

        if existing_cols:
            st.dataframe(merged[existing_cols].head(20), use_container_width=True)
            st.info("Check that 'created_customer' and 'source_new_id' are correctly populated based on the token mapping.")
        else:
            st.warning("Mapping preview columns not found in merged data.")

        # -----------------------------
        # Remove Cancelled
        # -----------------------------
        if "Schedule_Status" in merged.columns:
            merged = merged[merged["Schedule_Status"].str.upper() != "CANCELLED"]

        # -----------------------------
        # Tender Type Fix
        # -----------------------------
        merged["TenderType"] = merged["TenderType"].replace({"CC": "Credit"})

        # -----------------------------
        # Date Formatting
        # -----------------------------
        if "Schedule_NextChargeDate" in merged.columns:
            merged["Schedule_NextChargeDate"] = pd.to_datetime(
                merged["Schedule_NextChargeDate"], errors="coerce"
            ).dt.strftime("%m/%d/%Y")

        # -----------------------------
        # Build Output
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
            output[out_col] = merged[source_col] if source_col in merged else ""

        output["DonorPaidCosts"] = False

        # -----------------------------
        # Project Splits
        # -----------------------------
        fund_pattern = re.compile(r"Fund(\d+)_Code")
        fund_numbers = sorted([
            int(fund_pattern.match(col).group(1))
            for col in merged.columns
            if fund_pattern.match(col)
        ])

        max_funds = max(fund_numbers) if fund_numbers else 0

        for i in range(1, max_funds + 1):
            output[f"Project{i}Code"] = merged.get(f"Fund{i}_Code", "")
            output[f"Project{i}Name"] = merged.get(f"Fund{i}_Name", "")
            output[f"Project{i}Amount"] = merged.get(f"Fund{i}_Amount", "")

        # -----------------------------
        # CREDITCARDCOSTS Logic
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
                )

                output.loc[mask, [code_col, name_col, amount_col]] = ""
                output.loc[mask, "DonorPaidCosts"] = True

        # -----------------------------
        # Split Validation
        # -----------------------------
        project_amount_cols = [col for col in output.columns if "Project" in col and "Amount" in col]

        if project_amount_cols:
            output["ProjectTotal"] = output[project_amount_cols].apply(
                pd.to_numeric, errors="coerce"
            ).sum(axis=1)
        else:
            output["ProjectTotal"] = 0

        output["AmountMismatch"] = (
            pd.to_numeric(output["Amount"], errors="coerce") != output["ProjectTotal"]
        )

        # -----------------------------
        # Clean Number Formatting
        # -----------------------------
        def clean_number(x):
            try:
                num = float(x)
                if num == int(num):
                    return str(int(num))
                return str(round(num, 2))
            except:
                return ""

        output["Amount"] = output["Amount"].apply(clean_number)

        for col in output.columns:
            if "Project" in col and "Amount" in col:
                output[col] = output[col].apply(clean_number)

    # -----------------------------
    # Dashboard
    # -----------------------------
    st.subheader("Migration Summary")

    col1, col2, col3 = st.columns(3)
    col1.metric("Schedules Processed", len(output))
    col2.metric("Missing Tokens", output["PaymentMethodId"].isna().sum())
    col3.metric("Split Mismatches", output["AmountMismatch"].sum())

    # -----------------------------
    # Data Quality
    # -----------------------------
    st.subheader("Data Quality Report")

    if output["PaymentMethodId"].isna().sum() > 0:
        st.error("Some schedules are missing payment tokens")

    if output["AmountMismatch"].sum() > 0:
        st.warning("Some schedules have mismatched project totals")

    if (
        output["PaymentMethodId"].isna().sum() == 0
        and output["AmountMismatch"].sum() == 0
    ):
        st.success("No major data issues detected")

    # -----------------------------
    # Highlighting
    # -----------------------------
    def highlight(row):
        if row["AmountMismatch"]:
            return ['background-color: #FF9999'] * len(row)
        if pd.isna(row["PaymentMethodId"]):
            return ['background-color: #FFCC99'] * len(row)
        return [''] * len(row)

    st.subheader("Output Preview")
    st.dataframe(output.style.apply(highlight, axis=1), use_container_width=True)

    # -----------------------------
    # Downloads
    # -----------------------------
    csv = output.to_csv(index=False).encode("utf-8")
    st.download_button("Download Migration File", csv, "migration.csv")

    problem_rows = output[
        (output["AmountMismatch"]) | (output["PaymentMethodId"].isna())
    ]

    if len(problem_rows) > 0:
        st.subheader("Download Problem Rows")
        st.download_button(
            "Download Issues",
            problem_rows.to_csv(index=False).encode("utf-8"),
            "issues.csv"
        )
