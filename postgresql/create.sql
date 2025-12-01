-- STUDENTS
CREATE TABLE students (
    student_id      SERIAL PRIMARY KEY,
    netid           VARCHAR(16) UNIQUE NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    hashed_password VARCHAR(120) NOT NULL  
);

-- STUDY_SPOTS
CREATE TABLE study_spots (
    spot_id          SERIAL PRIMARY KEY,
    student_id       INTEGER REFERENCES students(student_id) ON DELETE SET NULL,
    name             VARCHAR(120) NOT NULL,
    building_code    VARCHAR(16) NOT NULL,
    area_description TEXT,
    seating_capacity INTEGER CHECK (seating_capacity >= 0),
    power_outlets    BOOLEAN NOT NULL DEFAULT FALSE,
    natural_light    BOOLEAN NOT NULL DEFAULT FALSE,
    open_24_7        BOOLEAN NOT NULL DEFAULT FALSE,
    is_active        BOOLEAN NOT NULL DEFAULT TRUE,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (name, building_code)
);

-- CATEGORIES
CREATE TABLE categories (
    category_id  SERIAL PRIMARY KEY,
    slug         VARCHAR(40) UNIQUE NOT NULL,
    display_name VARCHAR(120) NOT NULL
);

-- SAVED_SPOTS
CREATE TABLE saved_spots (
    student_id INTEGER NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    spot_id    INTEGER NOT NULL REFERENCES study_spots(spot_id) ON DELETE CASCADE,
    PRIMARY KEY (student_id, spot_id)
);

-- REVIEWS
CREATE TABLE reviews (
    review_id   SERIAL PRIMARY KEY,
    student_id  INTEGER NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    spot_id     INTEGER NOT NULL REFERENCES study_spots(spot_id) ON DELETE CASCADE,
    rating      INTEGER CHECK (rating BETWEEN 1 AND 5),
    comment     TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (student_id, spot_id)
);

-- VOTES
CREATE TABLE votes (
    vote_id     BIGSERIAL PRIMARY KEY,
    student_id  INTEGER NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    spot_id     INTEGER NOT NULL REFERENCES study_spots(spot_id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES categories(category_id) ON DELETE CASCADE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    rating      INTEGER CHECK (rating BETWEEN 1 AND 5),
    comment     TEXT,
    UNIQUE (student_id, spot_id, category_id)
);
