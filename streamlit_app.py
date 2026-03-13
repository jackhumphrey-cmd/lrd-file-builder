import pandas as pd
import streamlit as st
import re

st.set_page_config(page_title="Recurring Schedule Migration Builder", layout="wide")

st.title("Recurring Schedule Migration Builder")
st.markdown("Upload your **Token File** and **Schedule File** to generate the migration import.")

# Layout columns for uploads
col1, col2 = st.columns(2)

with col1:
    token_file = st.file_uploader("Upload Token File", type=["csv"])

with col2:
    schedule_file = st.file_uploader("Upload Schedule File", type=["csv", "xlsx"])

if token_file and schedule_file:

    with st.spinner("Processing files..."):

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
        )

        merged = merged.drop(columns=["source_old_id"])

        # Convert TenderType
        merged["TenderType"] = merged["TenderType"].replace({"CC": "Credit"})

        # Format next charge date
        if "Schedule_NextChargeDate" in merged.columns:
            merged["Schedule_NextChargeDate"] = pd.to_datetime(
                merged["Schedule_NextChargeDate"], errors="coerce"
            ).dt.strftime("%m/%d/%Y")

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

        # Default donor paid costs
        output["DonorPaidCosts"] = False

        # Detect fund splits
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

        # Remove CREDITCARDCOSTS projects
        for i in range(1, max_funds + 1):

            code_col = f"Project{i}Code"
            name_col = f"Project{i}Name"
            amount_col = f"Project{i}Amount"

            if code_col in output.columns:
                mask = output[code_col] == "CREDITCARDCOSTS"
                output.loc[mask, [code_col, name_col, amount_col]] = ""
                output.loc[mask, "DonorPaidCosts"] = True

    st.success("Migration file generated successfully!")

    st.subheader("Preview")
    st.dataframe(output, use_container_width=True)

    csv = output.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Migration File",
        csv,
        "recurring_schedule_import.csv",
        "text/csv"
    )
