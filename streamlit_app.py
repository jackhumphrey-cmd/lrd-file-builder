# Merge token data
merged = schedule.merge(
    tokens[["source_old_id", "created_customer", "source_new_id"]],
    left_on="Gateway_PaymentTokenId",
    right_on="source_old_id",
    how="left"
).drop(columns=["source_old_id"])

# **REMOVE CANCELLED SCHEDULES**
if "Schedule_Status" in merged.columns:
    merged = merged[merged["Schedule_Status"].str.upper() != "CANCELLED"]

# Continue with TenderType conversion, NextPaymentDate formatting, etc.
merged["TenderType"] = merged["TenderType"].replace({"CC": "Credit"})
