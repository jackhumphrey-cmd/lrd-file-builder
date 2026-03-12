import pandas as pd
import streamlit as st
import re

st.title("Recurring Schedule Migration Builder")

# Upload files
token_file = st.file_uploader("Upload Token File")
schedule_file = st.file_uploader("Upload Schedule File")

if token_file and schedule_file:
    # Read token file
    tokens = pd.read_csv(token_file)

    # Read schedule file (CSV or Excel)
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

    # Convert TenderType values
    merged["TenderType"] = merged["TenderType"].replace({"CC": "Credit"})

    # Zero out timestamps in NextPaymentDate
    if "NextPaymentDate" in merged.columns:
        merged["NextPaymentDate"] = pd.to_datetime(merged["NextPaymentDate"], errors="coerce").dt.strftime("%m/%d/%Y")

    # Initialize output DataFrame
    output = pd.DataFrame()

    # Column mapping
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

    # Populate output columns
    for out_col, source_col in mapping.items():
        if source_col in merged.columns:
            output[out_col] = merged[source_col]
        else:
            output[out_col] = ""

    # Add DonorPaidCosts column with default FALSE
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

    # Step 7: Remove CREDITCARDCOSTS projects and update DonorPaidCosts
for i in range(1, max_funds + 1):
    code_col = f"Project{i}Code"
    name_col = f"Project{i}Name"
    amount_col = f"Project{i}Amount"

    if code_col in output.columns:
        mask = output[code_col] == "CREDITCARDCOSTS"
        output.loc[mask, [code_col, name_col, amount_col]] = ""
        output.loc[mask, "DonorPaidCosts"] = True

    # Display preview
    st.write("Output Preview", output.head())

    # Prepare CSV for download
    csv = output.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Migration File",
        csv,
        "recurring_schedule_import.csv",
        "text/csv"
    )
