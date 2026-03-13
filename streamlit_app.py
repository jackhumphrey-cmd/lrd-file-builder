import pandas as pd
import streamlit as st
import re

st.set_page_config(
    page_title="Recurring Schedule Migration Tool",
    page_icon="💳",
    layout="wide"
)

st.title("💳 Recurring Schedule Migration Tool")
st.markdown("Generate recurring schedule import files from legacy exports.")

# Sidebar
st.sidebar.header("Upload Files")

token_file = st.sidebar.file_uploader("Token File", type=["csv"])
schedule_file = st.sidebar.file_uploader("Schedule File", type=["csv","xlsx"])

st.sidebar.markdown("---")
st.sidebar.write("Tool Status")

if not token_file or not schedule_file:
    st.sidebar.warning("Waiting for files")

if token_file and schedule_file:

    st.sidebar.success("Files Uploaded")

    with st.spinner("Processing data..."):

        tokens = pd.read_csv(token_file)

        if schedule_file.name.endswith(".csv"):
            schedule = pd.read_csv(schedule_file)
        else:
            schedule = pd.read_excel(schedule_file)

        merged = schedule.merge(
            tokens[["source_old_id","created_customer","source_new_id"]],
            left_on="Gateway_PaymentTokenId",
            right_on="source_old_id",
            how="left"
        )

        merged = merged.drop(columns=["source_old_id"])

        merged["TenderType"] = merged["TenderType"].replace({"CC":"Credit"})

        if "Schedule_NextChargeDate" in merged.columns:
            merged["Schedule_NextChargeDate"] = pd.to_datetime(
                merged["Schedule_NextChargeDate"], errors="coerce"
            ).dt.strftime("%m/%d/%Y")

        output = pd.DataFrame()

        mapping = {
            "FirstName":"Donor_FirstName",
            "LastName":"Donor_LastName",
            "Email":"Donor_EmailAddress",
            "PaymentMethodType":"TenderType",
            "PaymentMethodId":"source_new_id",
            "Amount":"Schedule_Amount",
            "Currency":"Schedule_Currency",
            "Frequency":"Schedule_Frequency",
            "NextPaymentDate":"Schedule_NextChargeDate",
            "LegacyId":"RD_Schedule_Id",
            "CustomerId":"created_customer",
            "SegmentCode":"Schedule_Meta_MotivationCode",
            "PlatformReferenceId":"RD_Schedule_Id"
        }

        for out_col, source_col in mapping.items():
            output[out_col] = merged[source_col] if source_col in merged else ""

        output["DonorPaidCosts"] = False

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

        for i in range(1, max_funds + 1):

            code_col = f"Project{i}Code"
            name_col = f"Project{i}Name"
            amount_col = f"Project{i}Amount"

            if code_col in output.columns:
                mask = output[code_col] == "CREDITCARDCOSTS"

                output.loc[mask, [code_col, name_col, amount_col]] = ""
                output.loc[mask, "DonorPaidCosts"] = True

    # Dashboard metrics
    st.subheader("Migration Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric("Schedules Processed", len(output))

    missing_tokens = output["PaymentMethodId"].isna().sum()
    col2.metric("Missing Tokens", missing_tokens)

    missing_dates = output["NextPaymentDate"].isna().sum()
    col3.metric("Missing Charge Dates", missing_dates)

    # Data quality warnings
    st.subheader("Data Quality Report")

    if missing_tokens > 0:
        st.error(f"{missing_tokens} schedules are missing payment tokens")

    if missing_dates > 0:
        st.warning(f"{missing_dates} schedules have no next charge date")

    if missing_tokens == 0 and missing_dates == 0:
        st.success("No major data issues detected")

    # Preview
    st.subheader("Output Preview")

    st.dataframe(output, use_container_width=True)

    # Download
    csv = output.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Migration File",
        csv,
        "recurring_schedule_import.csv",
        "text/csv"
    )
