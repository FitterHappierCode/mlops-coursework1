import pandas as pd

df = pd.read_csv("data/incidents_clean.csv")

print("total incidents:", len(df))
print("\nby priority:")
print(df["final_priority"].value_counts(dropna=False))

print("\nSLA breached ( >24hr ) counts:")
print(df["sla_breached"].value_counts(dropna=False))

print("\naverage resolution hours (ignore missing):")
print(df["resolution_hours"].dropna().mean())
