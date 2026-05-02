import os
from pathlib import Path
import re
import time
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

BASE_DIR = Path(__file__).resolve().parents[1]
CSV_PATH = Path(os.getenv("CSV_PATH", BASE_DIR / "data" / "netflix_titles.csv"))

def parse_date(value):
    if pd.isna(value):
        return None
    parsed = pd.to_datetime(value, format="%B %d, %Y", errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.date()


def parse_duration(value):
    if pd.isna(value) or value is None:
        return None, None

    value = str(value).strip()
    match = re.match(r"^(\d+)\s+([A-Za-z]+)$", value)
    if not match:
        return None, None

    duration_value = int(match.group(1))
    duration_unit = match.group(2).lower()
    return duration_value, duration_unit


def looks_like_duration(value):
    if pd.isna(value) or value is None:
        return False
    value = str(value).strip().lower()
    return bool(re.match(r"^\d+\s+(min|season|seasons)$", value))


def main():
    start_time = time.time()

    print("1. Loading .env ...")
    load_dotenv(BASE_DIR / ".env")

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("No DATABASE_URL found in .env file")

    print("2. Loading CSV...")
    df = pd.read_csv(CSV_PATH)

    print(f"   Rows loaded: {len(df)}")
    print(f"   Columns: {list(df.columns)}")

    # Renaming columns to match the database schema
    rename_map = {
        "type": "content_type",
        "cast": "cast_members",
        "duration": "duration_raw",
        "genre": "listed_in"
    }
    df = df.rename(columns=rename_map)

    # If the dataset doesn't have listed_in, but does have genre, we've already renamed it above.
    # If there's no date_added, we create an empty column.
    if "date_added" not in df.columns:
        df["date_added"] = None

    if "rating" not in df.columns:
        df["rating"] = None

    if "duration_raw" not in df.columns:
        df["duration_raw"] = None

    print("3. Fixing rows where duration accidentally fell into rating...")
    mask_shifted = df["duration_raw"].isna() & df["rating"].apply(looks_like_duration)
    shifted_count = mask_shifted.sum()

    if shifted_count > 0:
        df.loc[mask_shifted, "duration_raw"] = df.loc[mask_shifted, "rating"]
        df.loc[mask_shifted, "rating"] = None

    print(f"   Fixed rows: {shifted_count}")

    print("4. Transforming date_added...")
    df["date_added"] = df["date_added"].apply(parse_date)

    print("5. Transforming duration...")
    parsed_duration = df["duration_raw"].apply(parse_duration)
    df["duration_value"] = parsed_duration.apply(lambda x: x[0])
    df["duration_unit"] = parsed_duration.apply(lambda x: x[1])

    required_columns = [
        "show_id",
        "content_type",
        "title",
        "director",
        "cast_members",
        "country",
        "date_added",
        "release_year",
        "rating",
        "duration_raw",
        "duration_value",
        "duration_unit",
        "listed_in",
        "description",
    ]

    print("6. Checking required columns...")
    for col in required_columns:
        if col not in df.columns:
            df[col] = None

    df = df[required_columns]

    df = df.astype(object)
    df = df.where(pd.notnull(df), None)

    # Additional cleaning of records before insertion
    records = []
    for record in df.to_dict(orient="records"):
        clean_record = {}
        for key, value in record.items():
            if pd.isna(value):
                clean_record[key] = None
            else:
                clean_record[key] = value
        records.append(clean_record)

    print("7. Connecting to the database...")
    engine = create_engine(database_url, pool_pre_ping=True)

    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    print("   Connection successful")

    insert_sql = text("""
        INSERT INTO netflix_titles (
            show_id,
            content_type,
            title,
            director,
            cast_members,
            country,
            date_added,
            release_year,
            rating,
            duration_raw,
            duration_value,
            duration_unit,
            listed_in,
            description
        )
        VALUES (
            :show_id,
            :content_type,
            :title,
            :director,
            :cast_members,
            :country,
            :date_added,
            :release_year,
            :rating,
            :duration_raw,
            :duration_value,
            :duration_unit,
            :listed_in,
            :description
        )
        ON CONFLICT (show_id) DO NOTHING
    """)

    print("8. Starting import...")
    with engine.begin() as connection:
        connection.execute(insert_sql, records)

    elapsed = time.time() - start_time
    print(f"Import completed successfully in {elapsed:.2f} seconds.")
    print(f"Rows processed: {len(records)}")


if __name__ == "__main__":
    main()