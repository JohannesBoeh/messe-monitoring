"""
Run this once to see every field the AUMA API returns.
Add to your repo as scripts/debug_api.py and trigger via Actions,
or add this as a step in your workflow.
"""
import json, requests

r = requests.get(
    "https://www.auma.de/api/TradeFairData/getWebOverviewTradeFairData"
    "?intFilterYearFrom=2025&intFilterYearTo=2025"
    "&intFilterMonthFrom=1&intFilterMonthTo=1&strLanguage=de",
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=30,
)
data = r.json()
print(f"Total records: {len(data)}\n")

first = data[0]
print("=== ALL API FIELDS (first record) ===")
for k, v in first.items():
    print(f"  {k!r:40s} = {str(v)[:100]}")

print("\n=== FULL JSON ===")
print(json.dumps(first, indent=2, ensure_ascii=False))
