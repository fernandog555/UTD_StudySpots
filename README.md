# 📚 Study Spots @ UTD

Welcome to **Study Spots @ UTD**, a web application designed to help students at The University of Texas at Dallas discover the best places to study on campus. Whether you're seeking a quiet nook, a collaborative workspace, or a cozy lounge, this app makes it easy to find and rate study environments that suit your needs.

---

## 🚀 Features

- **🔍 Search & Discover**  
  Find study spots by name or keyword. Explore popular locations like ECSW, McDermott Library, and the Student Union. Each spot includes a description, ratings, and student feedback.

- **📊 Rate & Vote**  
  Vote on study spots based on categories like quietness, comfort, Wi-Fi quality, and more. Your input helps fellow Comets find the best places to focus.

- **🧑‍💻 Create an Account**  
  Sign up to submit new spots, leave reviews, and track your favorites. Authentication is done via student ID.

- **🖥️ Web Interface**  
  Built with Vue.js (TypeScript), the UI includes:
  - A landing page with login/explorer
  - Search bar for keywords
  - Pop-up menus with spot details and voting options
  - Account creation/login popups
---

## 🧩 Problem Statement

Students often struggle to find suitable study environments on campus. Our centralized database allows users to search for spots that match their preferences and contribute real-time feedback. Unlike Excel, a database supports dynamic updates, relational queries, and secure user interactions.

---

## 🎯 Target Users

- **Students**: Search, rate, and contribute study spot data.
- **Group 3 (Developers)**: Maintain and update the database as needed.

---

## 🗃️ Database Design

### Relations (Tables)

students Table

| Column Name      | Data Type     | Constraints                          |
|------------------|---------------|--------------------------------------|
| student_id       | SERIAL        | PRIMARY KEY                          |
| netid            | VARCHAR(16)   | UNIQUE, NOT NULL                     |
| created_at       | TIMESTAMPTZ   | DEFAULT now(), NOT NULL              |
| hashed_password  | VARCHAR(120)  | NOT NULL                             |

study_spots Table

| Column Name       | Data Type     | Constraints                          |
|-------------------|---------------|--------------------------------------|
| spot_id           | SERIAL        | PRIMARY KEY                          |
| name              | VARCHAR(120)  | NOT NULL                             |
| building_code     | VARCHAR(16)   | NOT NULL                             |
| area_description  | TEXT          |                                      |
| seating_capacity  | INTEGER       | CHECK (>= 0)                         |
| power_outlets     | BOOLEAN       | DEFAULT FALSE                        |
| natural_light     | BOOLEAN       | DEFAULT FALSE                        |
| open_24_7         | BOOLEAN       | DEFAULT FALSE                        |
| is_active         | BOOLEAN       | DEFAULT TRUE                         |
| created_at        | TIMESTAMPTZ   | DEFAULT now(), NOT NULL              |
| UNIQUE            | (name, building_code) |                              |

categories Table 

| Column Name   | Data Type     | Constraints                          |
|---------------|---------------|--------------------------------------|
| category_id   | SERIAL        | PRIMARY KEY                          |
| slug          | VARCHAR(40)   | UNIQUE, NOT NULL                     |
| display_name  | VARCHAR(60)   | NOT NULL                             |

votes Table

| Column Name   | Data Type     | Constraints                          |
|---------------|---------------|--------------------------------------|
| vote_id       | BIGSERIAL     | PRIMARY KEY                          |
| student_id    | INTEGER       | FOREIGN KEY → students(student_id)   |
| spot_id       | INTEGER       | FOREIGN KEY → study_spots(spot_id)   |
| category_id   | INTEGER       | FOREIGN KEY → categories(category_id)|
| score         | SMALLINT      | CHECK (BETWEEN 1 AND 5)              |



## 📥 Data Collection

- Manual Observation: Team members will survey campus locations.
- External Sources: UTD websites and Google Maps.
- User Contributions: Via Google Forms or custom submission forms.
- Rating Aggregation: Average scores calculated from multiple user votes.


## 🛠️ Tech Stack

- Frontend: Vue (TypeScript)
- Backend: PHP
- Database: MySQL
- Hosting: Github Pages (Frontend), External Server (Backend & Database)
