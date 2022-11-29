import pandas as pd
import requests
import os
from ratelimit import limits, sleep_and_retry
from pathlib import Path

DATA_DIR = Path("./data").resolve()
CSV_PATH = os.path.join(DATA_DIR, "pt_ratings.csv")


@sleep_and_retry
@limits(calls=2, period=1)
def call_api(offset: int):
    try:
        r = requests.get(
            "https://planetterp.com/api/v1/professors",
            params={"offset": offset, "reviews": "true", "limit": 100},
        )
        return r.json()
    except Exception as e:
        print(e)
        return []


if os.path.exists(CSV_PATH):
    print(f"[i] {CSV_PATH} exists, skipping...")
    exit(1)

rows = []
offset = 0
page_data = [0]
max_pages = float("inf")

while len(page_data) and offset < max_pages * 100:
    print(f"[i] Getting offset {offset}")
    page_data = call_api(offset)
    offset += 100
    rows += page_data

print("[i] Creating dataframe...")
df = pd.DataFrame(rows)
df.columns = df.columns.str.lower()

print(f"[i] Writing to {CSV_PATH}")
df.to_csv(CSV_PATH, index=False)
