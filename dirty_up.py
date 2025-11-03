import pandas as pd
import numpy as np
import random
from datetime import timedelta

# read your clean-ish base file
src = "data/incidents_aggregated_5k.csv"  # change if needed
dst = "data/incidents_dirty.csv"

df = pd.read_csv(src, low_memory=False)
df_dirty = df.copy()

print(f"Loaded source: {src}")
print(f"- starting rows: {len(df)}")

n = len(df_dirty)
rng = np.random.default_rng(42)

# 1) add ~1% duplicate rows
dupes = df_dirty.sample(frac=0.01, random_state=42)
df_dirty = pd.concat([df_dirty, dupes], ignore_index=True)
print(f"Injected duplicates: {len(dupes)} rows (1%) -> rows now: {len(df_dirty)})")

# 2) introduce missing values (~2%) in key columns
if "final_priority" in df_dirty.columns:
    idx = df_dirty.sample(frac=0.02, random_state=1).index
    df_dirty.loc[idx, "final_priority"] = np.nan
    print(f"Introduced missing final_priority: {len(idx)} rows (~2%)")

if "assignment_group_mode" in df_dirty.columns:
    idx = df_dirty.sample(frac=0.02, random_state=2).index
    df_dirty.loc[idx, "assignment_group_mode"] = np.nan
    print(f"Introduced missing assignment_group_mode: {len(idx)} rows (~2%)")

# 3) inconsistent priority labels (~1%)
if "final_priority" in df_dirty.columns:
    map_variants = {
        "1 - Critical": ["critical", "Critical", "1-critical", "P1"],
        "2 - High": ["high", "High", "2-high", "P2"],
        "3 - Moderate": ["moderate", "Moderate", "3-mod", "P3"],
        "4 - Low": ["low", "Low", "4-low", "P4"],
    }
    idx = df_dirty.sample(frac=0.01, random_state=3).index
    for i in idx:
        val = df_dirty.at[i, "final_priority"]
        if pd.isna(val):
            continue
        # pick a variant for the current value if known
        variants = map_variants.get(val, None)
        if variants:
            df_dirty.at[i, "final_priority"] = random.choice(variants)
    print(f"Corrupted priority labels (variants applied): {len(idx)} rows (~1%)")

# 4) dirty up date formats (first_opened_at) (~1.5%)
def to_weird_formats(s):
    # expect a datetime-like string; keep original if issue
    try:
        dt = pd.to_datetime(s, errors="coerce")
        if pd.isna(dt):  # already bad -> leave it
            return s
        choice = rng.choice([0,1,2,3])
        if choice == 0:
            return dt.strftime("%d/%m/%Y %H:%M")        # European
        elif choice == 1:
            return dt.strftime("%m/%d/%Y %H:%M")        # US style
        elif choice == 2:
            return dt.strftime("%Y/%m/%d %H:%M")        # ISO-ish with slashes
        else:
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")    # ISO with Z
    except Exception:
        return s

if "first_opened_at" in df_dirty.columns:
    idx = df_dirty.sample(frac=0.015, random_state=4).index
    df_dirty.loc[idx, "first_opened_at"] = df_dirty.loc[idx, "first_opened_at"].astype(str).map(to_weird_formats)

    # add a few outright invalid strings (~0.3%)
    idx_bad = df_dirty.sample(frac=0.003, random_state=5).index
    df_dirty.loc[idx_bad, "first_opened_at"] = "not a date"
    print(f"Changed date formats for first_opened_at: {len(idx)} rows (~1.5%)")
    print(f"Inserted invalid date strings: {len(idx_bad)} rows (~0.3%)")

# 5) make some bad durations in resolution_hours
if "resolution_hours" in df_dirty.columns:
    # ~0.5% negative
    idx_neg = df_dirty.sample(frac=0.005, random_state=6).index
    df_dirty.loc[idx_neg, "resolution_hours"] = -abs(pd.to_numeric(df_dirty.loc[idx_neg, "resolution_hours"], errors="coerce"))

    # ~0.5% huge outliers
    idx_huge = df_dirty.sample(frac=0.005, random_state=7).index
    df_dirty.loc[idx_huge, "resolution_hours"] = 9999
    print(f"Injected negative durations: {len(idx_neg)} rows (~0.5%)")
    print(f"Injected huge outliers (9999): {len(idx_huge)} rows (~0.5%)")

# 6) make some resolved earlier than opened (~0.5%) to simulate time order bugs
if {"first_opened_at","last_resolved_at"}.issubset(df_dirty.columns):
    idx_swap = df_dirty.sample(frac=0.005, random_state=8).index
    opened = pd.to_datetime(df_dirty.loc[idx_swap, "first_opened_at"], errors="coerce")
    resolved = pd.to_datetime(df_dirty.loc[idx_swap, "last_resolved_at"], errors="coerce")
    # push resolved 5 hours before opened (only where both parse)
    mask = opened.notna() & resolved.notna()
    adj_idx = df_dirty.loc[idx_swap].index[mask]
    df_dirty.loc[adj_idx, "last_resolved_at"] = (opened[mask] - pd.Timedelta(hours=5)).astype(str)
    print(f"Swapped timestamps (resolved before opened) for {len(adj_idx)} rows (~0.5% attempted)")

# 7) add extra spaces in assignment group (~1%)
if "assignment_group_mode" in df_dirty.columns:
    idx = df_dirty.sample(frac=0.01, random_state=9).index
    df_dirty.loc[idx, "assignment_group_mode"] = df_dirty.loc[idx, "assignment_group_mode"].astype(str).apply(lambda x: f" {x}  ")
    print(f"Added extra spaces to assignment_group_mode for {len(idx)} rows (~1%)")

# write out dirty file
df_dirty.to_csv(dst, index=False)
print(f"✅ Wrote dirty dataset → {dst}")
print(f"Rows (including dupes): {len(df_dirty)}")
