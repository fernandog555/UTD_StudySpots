-- Load CSV files into tables
\copy students(netid, created_at, hashed_password) FROM '/docker-entrypoint-initdb.d/students.csv' DELIMITER ',' CSV HEADER;
\copy study_spots(name, building_code, area_description, seating_capacity, power_outlets, natural_light, open_24_7, is_active, created_at) FROM '/docker-entrypoint-initdb.d/study_spots.csv' DELIMITER ',' CSV HEADER;
\copy categories(slug, display_name) FROM '/docker-entrypoint-initdb.d/categories.csv' DELIMITER ',' CSV HEADER;
\copy votes(student_id, spot_id, category_id, created_at, rating, comment) FROM '/docker-entrypoint-initdb.d/votes.csv' DELIMITER ',' CSV HEADER;
