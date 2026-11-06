from pathlib import Path
import duckdb

RAW = Path("data/raw")
PARQUET = Path("data/parquet")
PARQUET.mkdir(parents=True, exist_ok=True)

FILES = {
    "business": "yelp_academic_dataset_business.json",
    "review": "yelp_academic_dataset_review.json",
    "user": "yelp_academic_dataset_user.json",
    "tip": "yelp_academic_dataset_tip.json",
}

con = duckdb.connect()
for name, fname in FILES.items():
    src, dst = RAW / fname, PARQUET / f"{name}.parquet"
    if dst.exists():
        print(f"skip {name} (already converted)")
        continue
    print(f"converting {name}...")
    con.execute(f"""
        COPY (
            SELECT * FROM read_json(
                '{src.as_posix()}',
                format = 'newline_delimited',
                maximum_object_size = 33554432
            )
        ) TO '{dst.as_posix()}' (FORMAT PARQUET, COMPRESSION ZSTD)
    """)
print("done")