DROP TABLE IF EXISTS netflix_titles;

CREATE TABLE netflix_titles (
    show_id         VARCHAR(20) PRIMARY KEY,
    content_type    VARCHAR(20) NOT NULL CHECK (content_type IN ('Movie', 'TV Show')),
    title           TEXT NOT NULL,
    director        TEXT,
    cast_members    TEXT,
    country         TEXT,
    date_added      DATE,
    release_year    INTEGER NOT NULL CHECK (release_year BETWEEN 1900 AND 2100),
    rating          VARCHAR(20),
    duration_raw    VARCHAR(30),
    duration_value  INTEGER,
    duration_unit   VARCHAR(20),
    listed_in       TEXT,
    description     TEXT NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_netflix_content_type ON netflix_titles(content_type);
CREATE INDEX idx_netflix_release_year ON netflix_titles(release_year);
CREATE INDEX idx_netflix_rating ON netflix_titles(rating);
CREATE INDEX idx_netflix_country ON netflix_titles(country);
CREATE INDEX idx_netflix_title_lower ON netflix_titles((lower(title)));