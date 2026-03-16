from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from .db import engine
from .schemas import TitleCreate, TitleUpdate

app = FastAPI(
    title="Netflix Content API",
    description="REST API for working with the Netflix Content Analysis database",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def normalize_genres(value: str | None) -> set[str]:
    if not value:
        return set()
    return {part.strip().lower() for part in value.split(",") if part.strip()}


@app.get("/")
def root():
    return {"message": "Netflix Content API is running"}


# =========================
# 3.0 - GET everything
# =========================
@app.get("/titles")
def get_titles(
    type: str | None = Query(default=None, alias="type"),
    rating: str | None = None,
    country: str | None = None,
    title: str | None = None,
    limit: int = 100,
    offset: int = 0
):
    conditions = []
    params = {"limit": limit, "offset": offset}

    if type:
        conditions.append("content_type = :content_type")
        params["content_type"] = type

    if rating:
        conditions.append("rating = :rating")
        params["rating"] = rating

    if country:
        conditions.append("country ILIKE :country")
        params["country"] = f"%{country}%"

    if title:
        conditions.append("title ILIKE :title")
        params["title"] = f"%{title}%"

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    sql = f"""
        SELECT
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
        FROM netflix_titles
        {where_clause}
        ORDER BY title
        LIMIT :limit OFFSET :offset
    """

    with engine.connect() as connection:
        rows = connection.execute(text(sql), params).mappings().all()

    return rows


@app.get("/titles/{show_id}")
def get_title_by_id(show_id: str):
    sql = """
        SELECT
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
        FROM netflix_titles
        WHERE show_id = :show_id
    """

    with engine.connect() as connection:
        row = connection.execute(text(sql), {"show_id": show_id}).mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="Record not found")

    return row


# =========================
# 4.0 - POST
# =========================
@app.post("/titles", status_code=201)
def create_title(item: TitleCreate):
    sql = text("""
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
        RETURNING
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
    """)

    try:
        with engine.begin() as connection:
            row = connection.execute(text(sql.text), item.model_dump()).mappings().first()
        return row
    except IntegrityError:
        raise HTTPException(status_code=409, detail="show_id already exists")


# =========================
# 4.5 - PUT
# =========================
@app.put("/titles/{show_id}")
def update_title(show_id: str, item: TitleUpdate):
    payload = item.model_dump(exclude_none=True)

    if not payload:
        raise HTTPException(status_code=400, detail="No data provided for update")

    set_clause = ", ".join([f"{field} = :{field}" for field in payload.keys()])
    payload["show_id"] = show_id

    sql = f"""
        UPDATE netflix_titles
        SET {set_clause}
        WHERE show_id = :show_id
        RETURNING
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
    """

    with engine.begin() as connection:
        row = connection.execute(text(sql), payload).mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="Record not found")

    return row


# =========================
# 5.0 - Advanced stats
# =========================
@app.get("/stats/top-genres")
def get_top_genres(limit: int = 10):
    sql = """
        SELECT
            TRIM(genre) AS genre,
            COUNT(*) AS count
        FROM netflix_titles,
        LATERAL unnest(string_to_array(listed_in, ',')) AS genre
        WHERE listed_in IS NOT NULL
        GROUP BY TRIM(genre)
        ORDER BY count DESC
        LIMIT :limit
    """

    with engine.connect() as connection:
        rows = connection.execute(text(sql), {"limit": limit}).mappings().all()

    return rows


@app.get("/stats/releases-by-year")
def get_releases_by_year():
    sql = """
        SELECT
            release_year,
            COUNT(*) AS count
        FROM netflix_titles
        GROUP BY release_year
        ORDER BY release_year
    """

    with engine.connect() as connection:
        rows = connection.execute(text(sql)).mappings().all()

    return rows


# =========================
# 5.0 - Recommendations
# =========================
@app.get("/recommendations")
def get_recommendations(title: str, limit: int = 5):
    target_sql = """
        SELECT
            show_id,
            content_type,
            title,
            director,
            cast_members,
            country,
            release_year,
            rating,
            listed_in,
            description
        FROM netflix_titles
        WHERE title ILIKE :title
        LIMIT 1
    """

    with engine.connect() as connection:
        target = connection.execute(
            text(target_sql),
            {"title": title}
        ).mappings().first()

        if not target:
            raise HTTPException(status_code=404, detail="Title not found")

        candidates_sql = """
            SELECT
                show_id,
                content_type,
                title,
                director,
                cast_members,
                country,
                release_year,
                rating,
                listed_in,
                description
            FROM netflix_titles
            WHERE content_type = :content_type
              AND show_id <> :show_id
            LIMIT 500
        """

        candidates = connection.execute(
            text(candidates_sql),
            {
                "content_type": target["content_type"],
                "show_id": target["show_id"]
            }
        ).mappings().all()

    target_genres = normalize_genres(target["listed_in"])
    target_director = (target["director"] or "").strip().lower()
    target_country = (target["country"] or "").strip().lower()
    target_rating = (target["rating"] or "").strip().lower()
    target_year = target["release_year"]

    scored = []

    for item in candidates:
        score = 0

        item_genres = normalize_genres(item["listed_in"])
        same_genres = target_genres.intersection(item_genres)
        score += len(same_genres) * 3

        if (item["rating"] or "").strip().lower() == target_rating and target_rating:
            score += 2

        if (item["director"] or "").strip().lower() == target_director and target_director:
            score += 2

        if (item["country"] or "").strip().lower() == target_country and target_country:
            score += 1

        if item["release_year"] is not None and target_year is not None:
            year_diff = abs(item["release_year"] - target_year)
            if year_diff <= 3:
                score += 1
        else:
            year_diff = 999

        if score > 0:
            scored.append({
                "show_id": item["show_id"],
                "title": item["title"],
                "content_type": item["content_type"],
                "release_year": item["release_year"],
                "rating": item["rating"],
                "listed_in": item["listed_in"],
                "score": score
            })

    scored.sort(key=lambda x: (-x["score"], x["title"]))

    return {
        "target_title": target["title"],
        "recommendations": scored[:limit]
    }