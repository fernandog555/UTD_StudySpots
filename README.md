# 📚 Study Spots @ UTD

Welcome to **Study Spots @ UTD**, a full-stack web application designed to help students at The University of Texas at Dallas discover the best places to study on campus. Whether you're seeking a quiet nook, a collaborative workspace, or a cozy lounge, this app makes it easy to search for spots, read ratings, and save your favorite study environments.

---

## 🚀 Features

- **🔍 Search & Discover**  
  Search for study spots by name or building. Each spot includes a description, building code, seating info, and aggregated student ratings.

- **⭐ Rate & Review**  
  Leave 1–5 star ratings and optional comments on study spots. Ratings are tied to user accounts to prevent duplicates.

- **❤️ Save Favorite Spots**  
  Students can bookmark their preferred study spots and view them in their personal saved list.

- **🔐 Secure User Accounts**  
  Users can sign up and log in using their UTD NetID. Passwords are securely hashed using bcrypt.

- **🖥️ Modern Web Interface**  
  Built with Vue + TypeScript and a responsive UI, including:
  - A clean landing page  
  - Spot search interface  
  - Pop-up info cards  
  - Login and signup dialogs  

---

## 🧩 Problem Statement

Students often struggle to find suitable study environments on campus. This project centralizes information—including locations, amenities, and real student feedback—allowing students to quickly find a study spot that fits their needs.

A traditional Excel sheet cannot handle relational data, authentication, dynamic ratings, or user-specific saved items. A full database-backed web application solves these issues.

---

## 🎯 Target Users

- **UTD Students:** Find, rate, and save study spots.
- **Developers / Maintainers:** Extend the dataset, improve UI/UX, and maintain backend and database.

---

## 🗃️ Database Design

Below is the **final production schema** implemented in PostgreSQL via FastAPI:

### **students Table**

| Column Name      | Data Type     | Constraints                          |
|------------------|---------------|--------------------------------------|
| student_id       | SERIAL        | PRIMARY KEY                          |
| netid            | VARCHAR(16)   | UNIQUE, NOT NULL                     |
| created_at       | TIMESTAMPTZ   | DEFAULT now(), NOT NULL              |
| hashed_password  | VARCHAR(120)  | NOT NULL                             |

---

### **study_spots Table**

| Column Name       | Data Type     | Constraints                          |
|-------------------|---------------|--------------------------------------|
| spot_id           | SERIAL        | PRIMARY KEY                          |
| name              | VARCHAR(120)  | NOT NULL                             |
| building_code     | VARCHAR(16)   | NOT NULL                             |
| area_description  | TEXT          |                                      |
| seating_capacity  | INTEGER       | CHECK (seating_capacity >= 0)        |
| power_outlets     | BOOLEAN       | DEFAULT FALSE                        |
| natural_light     | BOOLEAN       | DEFAULT FALSE                        |
| open_24_7         | BOOLEAN       | DEFAULT FALSE                        |
| is_active         | BOOLEAN       | DEFAULT TRUE                         |
| created_at        | TIMESTAMPTZ   | DEFAULT now(), NOT NULL              |
| UNIQUE            | (name, building_code) |                              |

---

### **saved_spots Table**

| Column Name   | Data Type | Constraints                                           |
|---------------|-----------|-------------------------------------------------------|
| student_id    | INTEGER   | FK → students(student_id) ON DELETE CASCADE          |
| spot_id       | INTEGER   | FK → study_spots(spot_id) ON DELETE CASCADE          |
| PRIMARY KEY   | (student_id, spot_id) |                                           |

---

### **reviews Table**

| Column Name   | Data Type     | Constraints                                           |
|---------------|---------------|-------------------------------------------------------|
| review_id     | SERIAL        | PRIMARY KEY                                           |
| student_id    | INTEGER       | FK → students(student_id) ON DELETE CASCADE          |
| spot_id       | INTEGER       | FK → study_spots(spot_id) ON DELETE CASCADE          |
| rating        | INTEGER       | CHECK (rating BETWEEN 1 AND 5)                        |
| comment       | TEXT          |                                                       |
| created_at    | TIMESTAMPTZ   | DEFAULT now(), NOT NULL                               |
| UNIQUE        | (student_id, spot_id) |                                                |

---

### **categories Table (optional — only if categories are used)**

> ⚠️ *Categories are currently not used in the production version. Remove this table if unused.*

---

## 📥 Data Collection

- Direct observations of campus locations  
- UTD building information  
- User-submitted reviews and ratings  
- Aggregated average ratings calculated dynamically from the reviews table  

---

## 🛠️ Tech Stack

- **Frontend:** Vue (TypeScript), HTML/CSS, Vite  
- **Backend:** FastAPI (Python), Uvicorn  
- **Database:** PostgreSQL  
- **ORM/Driver:** Psycopg  
- **Auth:** bcrypt password hashing  
- **Hosting:** Render / Local Docker setup  
- **Version Control:** Git + GitHub  
