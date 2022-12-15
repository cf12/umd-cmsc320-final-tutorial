import pandas as pd
import requests
import os
from ratelimit import limits, sleep_and_retry
from pathlib import Path

DATA_DIR = Path("./data").resolve()
CSV_PATH = os.path.join(DATA_DIR, "salaries.csv")

Path(DATA_DIR).mkdir(parents=True, exist_ok=True)


# @sleep_and_retry
# @limits(calls=2, period=1)
def call_api(page: int, year: int):
    try:
        r = requests.get(
            f"https://api.dbknews.com/salary/year/{year}", params={"page": page}
        )
        return r.json()
    except Exception as e:
        print(e)
        return []


if os.path.exists(CSV_PATH):
    print("[i] salaries.csv exists, skipping...")
    exit(1)

# max_pages = 3
max_pages = float("inf")

salaries = []

# Diamondback has data from 2013 to 2022
for year in range(2013, 2023):
    page = 1
    page_data = [0]

    while page_data and page <= max_pages:
        print(f"[i] Getting page {page} for year {year}")
        data = call_api(page, year)["data"]

        page_data = list(map(lambda x: {"year": year, **x}, data))
        page += 1
        salaries += page_data

df = pd.DataFrame.from_records(salaries)
df.columns = df.columns.str.lower()

df.to_csv(CSV_PATH, index=False)
print(f"[i] Writing to {CSV_PATH}")
