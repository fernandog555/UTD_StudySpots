import os
from typing import Optional
from fastapi import APIRouter, HTTPException
from datetime import datetime
from pydantic import BaseModel, constr
import bcrypt
from ..db import get_connection

# Toggle to intentionally allow unsafe login logic (for demo only)
USE_UNSAFE_LOGIN = os.getenv("USE_UNSAFE_LOGIN", "0") == "1"

router = APIRouter(prefix="/auth", tags=["auth"])

class RegisterRequest(BaseModel):
    netid: constr(strip_whitespace=True, min_length=3, max_length=16)
    password: constr(min_length=6, max_length=72)

class LoginRequest(BaseModel):
    netid: constr(strip_whitespace=True, min_length=3, max_length=16)
    password: constr(min_length=6, max_length=72)

class StudentOut(BaseModel):
    student_id: int
    netid: str
    created_at: datetime


class UpdateRequest(BaseModel):
    student_id: int
    netid: Optional[constr(strip_whitespace=True, min_length=3, max_length=16)] = None
    password: Optional[constr(min_length=6, max_length=72)] = None
    current_password: Optional[constr(min_length=6, max_length=72)] = None

@router.post("/login", response_model=StudentOut)
def login(data: LoginRequest):
    with get_connection() as conn:
        with conn.cursor() as cur:
            if USE_UNSAFE_LOGIN:
                # Intentionally vulnerable: string concatenation, no bcrypt check
                unsafe_query = f"""
                    SELECT student_id, netid, hashed_password, created_at
                    FROM students
                    WHERE netid = '{data.netid}' AND hashed_password = '{data.password}'
                """
                cur.execute(unsafe_query)
                user = cur.fetchone()
                if not user:
                    raise HTTPException(status_code=401, detail="Invalid credentials (unsafe mode)")
                return user
            else:
                # Safe: prepared statement + bcrypt verification
                cur.execute(
                    """
                    SELECT student_id, netid, hashed_password, created_at
                    FROM students
                    WHERE netid = %s
                    """,
                    (data.netid,)
                )
                user = cur.fetchone()

                if not user:
                    raise HTTPException(status_code=401, detail="Invalid credentials")

                stored_hash = user["hashed_password"].encode()
                if not bcrypt.checkpw(data.password.encode(), stored_hash):
                    raise HTTPException(status_code=401, detail="Invalid credentials")

                return user


# --------------------------------------------------------------------
# demo endpoints to illustrate SQL injection vs. prepared statements
# demo only. do not use for real auth
# --------------------------------------------------------------------
@router.post("/login-demo/unsafe")
def login_demo_unsafe(data: LoginRequest):
    """
    Intentionally vulnerable login that concatenates user input directly
    into the SQL string. Use for demonstrating injection only.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            unsafe_query = f"""
                SELECT student_id, netid, created_at
                FROM students
                WHERE netid = '{data.netid}' AND hashed_password = '{data.password}'
            """
            cur.execute(unsafe_query)
            rows = cur.fetchall()
            return {
                "query": unsafe_query.strip(),
                "row_count": len(rows),
                "rows": rows,
            }


@router.post("/login-demo/safe")
def login_demo_safe(data: LoginRequest):
    """
    Safe login using prepared statements; same inputs as the unsafe demo.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            query = """
                SELECT student_id, netid, created_at
                FROM students
                WHERE netid = %s AND hashed_password = %s
            """
            params = [data.netid, data.password]
            cur.execute(query, params)
            rows = cur.fetchall()
            return {
                "query": query.strip(),
                "params": params,
                "row_count": len(rows),
                "rows": rows,
            }

@router.post("/register", response_model=StudentOut)
def register(data: RegisterRequest):
    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                "SELECT student_id FROM students WHERE netid = %s",
                (data.netid,)
            )
            exists = cur.fetchone()

            if exists:
                raise HTTPException(400, "NetID already registered")

            hashed_pw = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt()).decode()

            cur.execute(
                """
                INSERT INTO students (netid, hashed_password)
                VALUES (%s, %s)
                RETURNING student_id, netid, created_at
                """,
                (data.netid, hashed_pw)
            )

            created = cur.fetchone()
            conn.commit()
            return created


@router.put("/update", response_model=StudentOut)
def update_user(data: UpdateRequest):
    if not data.netid and not data.password:
        raise HTTPException(status_code=400, detail="No updates provided")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT student_id, netid, hashed_password, created_at
                FROM students
                WHERE student_id = %s
                """,
                (data.student_id,),
            )
            existing = cur.fetchone()
            if not existing:
                raise HTTPException(status_code=404, detail="User not found")

            # Require current_password if password change requested
            if data.password:
                if not data.current_password:
                    raise HTTPException(status_code=400, detail="Current password required")
                stored_hash = existing["hashed_password"].encode()
                if not bcrypt.checkpw(data.current_password.encode(), stored_hash):
                    raise HTTPException(status_code=401, detail="Invalid current password")

            fields = []
            values = []

            if data.netid and data.netid != existing["netid"]:
                fields.append("netid = %s")
                values.append(data.netid)

            if data.password:
                hashed_pw = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt()).decode()
                fields.append("hashed_password = %s")
                values.append(hashed_pw)

            if not fields:
                return existing

            values.append(data.student_id)

            try:
                cur.execute(
                    f"""
                    UPDATE students
                    SET {', '.join(fields)}
                    WHERE student_id = %s
                    RETURNING student_id, netid, created_at
                    """,
                    tuple(values),
                )
            except Exception as exc:
                conn.rollback()
                raise HTTPException(status_code=400, detail=str(exc))

            updated = cur.fetchone()
            conn.commit()
            return updated
