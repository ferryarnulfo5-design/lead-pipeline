import os
import pandas as pd

df = pd.read_csv("input/business_list.csv", dtype=str, encoding="utf-8-sig", sep=None, engine="python")
rows = []
for _, r in df.iterrows():
    name = str(r.iloc[0]).strip()
    if not name or name == "nan":
        continue
    rows.append({"business": name,
                 "dork": f'site:linkedin.com/in ("CEO" OR "Owner" OR "Founder") "{name}"'})
os.makedirs("output", exist_ok=True)
pd.DataFrame(rows).to_csv("output/dorks.csv", index=False)
print("dorks.csv ready:", len(rows), "rows")
