import requests
import numpy as np
import pandas as pd
import os
from pathlib import Path

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = os.path.join(SCRIPT_PATH, "data")

Path(DATA_DIR).mkdir(parents=True, exist_ok=True)

# max_pages = 3
max_pages = float("inf")

# Diamondback has data from 2013 to 2022
for year in range(2013, 2023):
    salaries = []
    page = 1
    page_data = [0]

    while len(page_data) and page <= max_pages:
        print(f"Getting page {page} for year {year}")
        r = requests.get(
            f"https://api.dbknews.com/salary/year/{year}", params={"page": page}
        )

        page_data = r.json()["data"]
        page += 1

        salaries += page_data

    df = pd.DataFrame.from_records(salaries)
    csv_path = os.path.join(DATA_DIR, f"salaries_{year}.csv")
    df.to_csv(csv_path)
    print(f"Writing to {csv_path}")

