import pandas as pd
import numpy as np

SRC = "data/incidents_dirty.csv"      # <- read the DIRTY file now
OUT = "data/incidents_clean.csv"      # <- cleaned output

# 1) load
df = pd.read_csv(SRC, low_memory=False)
print(f"Loaded dirty file: {SRC}")
print(f"- starting rows: {len(df)}")

# 2) drop exact duplicates
df = df.drop_duplicates()
print(f"Step: drop exact duplicates -> rows: {len(df)}")

# 3) standardise priority labels (fix variants + keep originals if you want)
priority_map = {
    "1 - Critical": ["1 - Critical", "critical", "Critical", "1-critical", "P1"],
    "2 - High":     ["2 - High", "high", "High", "2-high", "P2"],
    "3 - Moderate": ["3 - Moderate", "moderate", "Moderate", "3-mod", "P3"],
    "4 - Low":      ["4 - Low", "low", "Low", "4-low", "P4"]
}

def normalise_priority(x):
    if pd.isna(x):
        return np.nan
    for canon, variants in priority_map.items():
        if str(x) in variants:
            return canon
    return x  # unknown values pass through unchanged

if "final_priority" in df.columns:
    df["final_priority"] = df["final_priority"].apply(normalise_priority)
    print("Step: normalised final_priority values (mapped variants to canonical labels)")

# 4) parse date/time columns (handle mixed formats + bad strings)
def parse_dt(s):
    # tries multiple formats, returns NaT if it can’t parse
    return pd.to_datetime(s, errors="coerce", dayfirst=True, utc=False)

for c in ["first_opened_at", "last_resolved_at", "last_closed_at"]:
    if c in df.columns:
        df[c] = parse_dt(df[c])
        print(f"Step: parsed/normalized date column: {c}")

# 5) remove rows with no opened time (can’t use them)
df = df.dropna(subset=["first_opened_at"])
print(f"Step: dropped rows with missing first_opened_at -> rows: {len(df)}")

# 6) fix time order issues: if resolved before opened, set resolved to NaT
if {"first_opened_at","last_resolved_at"}.issubset(df.columns):
    bad = df["last_resolved_at"] < df["first_opened_at"]
    df.loc[bad, "last_resolved_at"] = pd.NaT
    print(f"Step: corrected timestamp ordering -> set last_resolved_at to NaT for {bad.sum()} rows")

# 7) rebuild resolution_hours from timestamps when possible
if {"first_opened_at","last_resolved_at"}.issubset(df.columns):
    dur = (df["last_resolved_at"] - df["first_opened_at"]).dt.total_seconds() / 3600.0
    df["resolution_hours_from_time"] = dur
    print("Step: computed resolution_hours_from_time from timestamps (hours)")

# choose best available resolution_hours
if "resolution_hours" in df.columns and "resolution_hours_from_time" in df.columns:
    # prefer computed duration, else fall back to original
    df["resolution_hours"] = np.where(
        pd.notna(df["resolution_hours_from_time"]),
        df["resolution_hours_from_time"],
        pd.to_numeric(df["resolution_hours"], errors="coerce")
    )
    print("Step: merged resolution_hours_from_time into resolution_hours (prefer computed values)")
elif "resolution_hours_from_time" in df.columns:
    df["resolution_hours"] = df["resolution_hours_from_time"]
    print("Step: using computed resolution_hours_from_time as resolution_hours")

# 8) clip/clean bad durations: drop negatives, cap extreme outliers
neg_before = (pd.to_numeric(df["resolution_hours"], errors="coerce") < 0).sum()
df = df[(df["resolution_hours"].isna()) | (df["resolution_hours"] >= 0)]
print(f"Step: dropped rows with negative resolution_hours -> removed {neg_before} rows; rows now: {len(df)}")
q99 = df["resolution_hours"].quantile(0.99)
df.loc[df["resolution_hours"] > q99, "resolution_hours"] = q99  # simple cap for coursework
print(f"Step: capped resolution_hours at 99th percentile -> cap value: {q99:.2f} hours")

# 9) keep just the columns we care about
keep = [
    "number",
    "first_opened_at",
    "last_resolved_at",
    "last_closed_at",
    "final_priority",
    "final_state",
    "assignment_group_mode",
    "events_count",
    "resolution_hours",
]
df = df[[c for c in keep if c in df.columns]]

# 10) add labels (same as before)
df["sla_breached"] = (df["resolution_hours"] > 24).astype("Int64")
df["quick_resolution"] = (df["resolution_hours"] < 12).astype("Int64")
print("Step: computed sla_breached (>24h) and quick_resolution (<12h) flags")

priority_num = {"1 - Critical":1, "2 - High":2, "3 - Moderate":3, "4 - Low":4}
df["priority_label"] = df["final_priority"].map(priority_num).astype("Int64")

# 11) save
df.to_csv(OUT, index=False)
print(f"✅ cleaned file saved → {OUT}")
print(f"rows: {len(df)}")
print("Preview (first 3 rows):")
print(df.head(3).to_string(index=False))
