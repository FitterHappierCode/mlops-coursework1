# Figures produced from the incidents dataset

This document lists the figures saved under `data/figures/` and provides a short explanation for each image to help interpretation.

---

## incidents_over_time.png

![incidents_over_time](incidents_over_time.png)

This plot shows the daily count of incidents (light line) with a 7-day rolling average (darker line) to reduce day-to-day noise. The x-axis is date (based on `first_opened_at`) and the y-axis is number of incidents opened that day. Use the rolling line to see trends; individual spikes may be single-day events.

---

## incidents_dirty_vs_clean.png

![incidents_dirty_vs_clean](incidents_dirty_vs_clean.png)

A simple bar chart comparing the total number of rows in the original dirty CSV vs the cleaned CSV. This helps verify how many rows were removed by cleaning (duplicates, invalid timestamps, etc.). Large differences indicate substantial filtering during cleaning.

---

## incidents_per_priority.png

![incidents_per_priority](incidents_per_priority.png)

Counts of incidents grouped by the canonical `final_priority` values (e.g., "1 - Critical" to "4 - Low"). Missing or unknown priorities are labelled as "Unknown". This shows the distribution of severity levels seen after normalization in the pipeline.

---

## missingness_heatmap.png

![missingness_heatmap](missingness_heatmap.png)

Bar chart of percent missing values per column in the cleaned dataset. Columns near 100% missing are effectively absent and may be dropped for modelling; columns with moderate missingness may need imputation. This view is based on the cleaned file, so it reflects missingness after data cleaning steps.

---

## top_assignment_groups.png

![top_assignment_groups](top_assignment_groups.png)

Top 10 assignment groups by incident count (uses `assignment_group_mode` with missing shown as "(missing)"). This tells you which teams or groups receive the most incidents and can highlight operational hotspots.

---

## sla_rate_by_month.png

![sla_rate_by_month](sla_rate_by_month.png)

Monthly time series of the proportion of incidents that breached SLA (where `sla_breached == 1`). The y-axis shows the fraction breached (0–1). This helps identify seasonal or operational trends in SLA performance.

---

## resolution_by_priority.png

![resolution_by_priority](resolution_by_priority.png)

Boxplots of `resolution_hours` grouped by `final_priority`. The vertical scale uses a symmetric log transform to handle skew (small values near zero shown linearly, large values compressed). Compare medians and spread across priorities to see if higher-priority incidents are resolved faster.

---

## resolution_time_hist.png

![resolution_time_hist](resolution_time_hist.png)

Histogram of resolution times (in hours), clipped at the 99th percentile to avoid extreme outliers dominating the plot. Use the histogram to understand the overall distribution and where most incidents fall (e.g., short vs long resolutions).

---

## sla_breach_distribution.png

![sla_breach_distribution](sla_breach_distribution.png)

Bar chart showing counts of SLA statuses: Met (≤24h), Breached (>24h), and Missing. This gives a quick snapshot of how many incidents meet vs miss the SLA threshold.

---

## pipeline_diagram.png

![pipeline_diagram](pipeline_diagram.png)

A simple diagram of the processing pipeline used in `pipeline.py`: ingestion → validation → cleaning → output. This is a visual aid to understand the major steps taken during cleaning and how the cleaned CSV was produced.

---

Notes and caveats

- All figures are generated from `data/incidents_clean.csv` (except the dirty vs clean comparison which reads `data/incidents_dirty.csv`).
- Several plots perform clipping or transformations (e.g., resolution clipping at 99th percentile, symlog scale for boxplots) to make visual comparison easier; check the raw numbers if exact values are needed.
- If you'd like a single HTML report (with images and narrative) instead of a markdown file, I can produce that next.

If you'd like shorter or longer explanations, or a version with statistical summaries under each figure, tell me which style you prefer and I will update this file.
