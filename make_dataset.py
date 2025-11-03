import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# make sure your 'data' folder exists
os.makedirs("data", exist_ok=True)

# we will make 2000 fake incidents
n = 2000
random.seed(42)
now = datetime.now()

data = []
for i in range(n):
    number = f"INC{100000 + i}"
    priority = random.choice(["1 - Critical", "2 - High", "3 - Moderate", "4 - Low"])
    opened = now - timedelta(days=random.randint(0, 60), hours=random.randint(0, 23))
    duration = timedelta(hours=random.randint(1, 72))  # how long it took to resolve
    resolved = opened + duration
    closed = resolved + timedelta(hours=random.randint(1, 5))
    assignment = random.choice(["Network", "Database", "Application", "Security"])
    state = random.choice(["Resolved", "Closed"])
    events = random.randint(1, 10)
    resolution_hours = round(duration.total_seconds() / 3600, 2)

    data.append({
        "number": number,
        "first_opened_at": opened,
        "last_resolved_at": resolved,
        "last_closed_at": closed,
        "final_state": state,
        "final_priority": priority,
        "assignment_group_mode": assignment,
        "events_count": events,
        "resolution_hours": resolution_hours
    })

df = pd.DataFrame(data)
df.to_csv("data/incidents_aggregated_5k.csv", index=False)
out_path = "data/incidents_aggregated_5k.csv"
print(f"✅ Fake incident dataset created: {out_path}")
print(f"- rows generated: {len(df)}")
print("- sample rows:\n", df.head(3).to_string(index=False))
