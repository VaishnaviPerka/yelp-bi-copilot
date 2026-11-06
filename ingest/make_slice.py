from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parents[1]   # repo root (yelp-bi-copilot)
PARQUET = ROOT / "data" / "parquet"

CITIES = [("Boise", "ID"),
    ("Clearwater", "FL"),
    ("Meridian", "ID")]  # <- replace with real picks

city_filter = ", ".join(f"('{c}', '{s}')" for c, s in CITIES)
con = duckdb.connect(str(ROOT / "yelp.duckdb"))

def p(name):
    return (PARQUET / f"{name}.parquet").as_posix()

con.execute(f"""
    CREATE OR REPLACE TABLE business_slice AS
    SELECT * FROM '{p("business")}'
    WHERE categories LIKE '%Restaurants%'
      AND (city, state) IN ({city_filter})
""")
con.execute(f"""
    CREATE OR REPLACE TABLE review_slice AS
    SELECT * FROM '{p("review")}'
    WHERE business_id IN (SELECT business_id FROM business_slice)
""")
con.execute(f"""
    CREATE OR REPLACE TABLE user_slice AS
    SELECT * FROM '{p("user")}'
    WHERE user_id IN (SELECT user_id FROM review_slice)
""")
con.execute(f"""
    CREATE OR REPLACE TABLE tip_slice AS
    SELECT * FROM '{p("tip")}'
    WHERE business_id IN (SELECT business_id FROM business_slice)
""")

for t in ["business_slice", "review_slice", "user_slice", "tip_slice"]:
    n = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(t, n)

con.close()