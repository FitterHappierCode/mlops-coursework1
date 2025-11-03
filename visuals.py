import os
import pandas as pd
import matplotlib.pyplot as plt

# === paths ===
CSV = "data/incidents_clean.csv"
OUT_DIR = "data/figures"
os.makedirs(OUT_DIR, exist_ok=True)

# === load cleaned data ===
df = pd.read_csv(CSV, low_memory=False)

# 1) Incidents per priority (bar)
plt.figure()
(df["final_priority"].fillna("Unknown").value_counts().sort_index()).plot(kind="bar")
plt.title("Incidents per Priority")
plt.xlabel("Priority")
plt.ylabel("Count")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "incidents_per_priority.png"), dpi=160)
plt.close()

# 2) SLA breach distribution (bar)
plt.figure()
(df["sla_breached"]
   .fillna(-1)
   .replace({-1:"Missing",0:"Met (≤24h)",1:"Breached (>24h)"})
   .value_counts()
).plot(kind="bar")
plt.title("SLA Breach Distribution")
plt.xlabel("Status")
plt.ylabel("Count")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "sla_breach_distribution.png"), dpi=160)
plt.close()

# 3) Resolution time histogram (clipped)
plt.figure()
if df["resolution_hours"].notna().any():
    clip_val = df["resolution_hours"].dropna().quantile(0.99)
    df["resolution_hours"].dropna().clip(upper=clip_val).hist(bins=30)
    plt.title("Resolution Time (hours) — clipped at 99th percentile")
    plt.xlabel("Hours")
    plt.ylabel("Count")
else:
    plt.text(0.5, 0.5, "No resolution_hours available", ha="center", va="center")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "resolution_time_hist.png"), dpi=160)
plt.close()

# 4) Simple pipeline diagram (boxes + arrows)
plt.figure(figsize=(8,4))
ax = plt.gca()
ax.axis("off")

def box(text, x, y):
    ax.add_patch(plt.Rectangle((x-0.08, y-0.1), 0.16, 0.18, fill=False))
    ax.text(x, y, text, ha="center", va="center")

boxes = [
    ("Ingestion\n(read CSV)", 0.12, 0.6),
    ("Validation\n(drop dups,\ncheck required)", 0.37, 0.6),
    ("Cleaning\n(parse dates,\nfix labels,\nrecompute duration)", 0.62, 0.6),
    ("Output\n(save clean CSV)", 0.87, 0.6),
]
for text,x,y in boxes:
    box(text, x, y)
for i in range(len(boxes)-1):
    x1,y1 = boxes[i][1], boxes[i][2]
    x2,y2 = boxes[i+1][1], boxes[i+1][2]
    ax.annotate("", xy=(x2-0.16, y2), xytext=(x1+0.08, y1),
                arrowprops=dict(arrowstyle="->", lw=1.5))

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "pipeline_diagram.png"), dpi=160)
plt.close()

print("✅ Saved figures to:", OUT_DIR)
