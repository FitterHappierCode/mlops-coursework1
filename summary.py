import pandas as pd

SRC = "data/incidents_clean.csv"

df = pd.read_csv(SRC)

total = len(df)
print(f"Loaded cleaned data: {SRC}")
print(f"Total incidents (cleaned): {total}\n")

print("By priority (count, percent):")
pri = df["final_priority"].value_counts(dropna=False)
pri_pct = df["final_priority"].value_counts(normalize=True, dropna=False) * 100
for k,v in pri.items():
	print(f"- {k}: {v} ({pri_pct[k]:.1f}%)")

print("\nSLA summary:")
sla_counts = df["sla_breached"].value_counts(dropna=False)
sla_pct = df["sla_breached"].value_counts(normalize=True, dropna=False) * 100
for k,v in sla_counts.items():
	label = "breached (1)" if str(k) == '1' else ("not breached (0)" if str(k) == '0' else str(k))
	print(f"- {label}: {v} ({sla_pct[k]:.1f}%)")

print("\nQuick resolution (<12h) percent:")
if "quick_resolution" in df.columns:
	qr_pct = df["quick_resolution"].mean() * 100
	print(f"- quick_resolution: {qr_pct:.1f}%")
else:
	print("- quick_resolution column not present")

res = df["resolution_hours"].dropna()
print("\nResolution hours (cleaned):")
print(f"- count (non-missing): {len(res)}")
print(f"- mean: {res.mean():.2f} hours")
print(f"- median: {res.median():.2f} hours")
print(f"- 90th percentile: {res.quantile(0.9):.2f} hours")
print(f"- 99th percentile: {res.quantile(0.99):.2f} hours")

print("\nTop 5 longest resolution_hours:")
print(res.sort_values(ascending=False).head(5).to_string(index=False))

print("\nSummary complete.")
