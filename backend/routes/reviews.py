from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, conint
from typing import List, Optional

from ..db import get_connection

router = APIRouter(prefix="/reviews", tags=["reviews"])


class ReviewIn(BaseModel):
    student_id: int
    spot_id: int
    rating: conint(ge=1, le=5)
    comment: str


class ReviewOut(BaseModel):
    id: int
    student_id: int
    spot_id: int
    author: str
    rating: int
    text: Optional[str] = None
    created_at: datetime


def _map_review(row: dict) -> ReviewOut:
    return ReviewOut(
        id=row["review_id"],
        student_id=row["student_id"],
        spot_id=row["spot_id"],
        author=row.get("netid") or "anonymous",
        rating=row.get("rating") or 0,
        text=row.get("comment"),
        created_at=row.get("created_at") or datetime.utcnow(),
    )


@router.get("/spot/{spot_id}", response_model=List[ReviewOut])
def list_reviews_for_spot(spot_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT r.review_id,
                       r.student_id,
                       r.spot_id,
                       r.rating,
                       r.comment,
                       COALESCE(r.created_at, now()) AS created_at,
                       s.netid
                FROM reviews r
                JOIN students s ON s.student_id = r.student_id
                WHERE r.spot_id = %s
                ORDER BY created_at DESC
                """,
                (spot_id,),
            )

            rows = cur.fetchall()
            return [_map_review(r) for r in rows]


@router.get("/user/{student_id}", response_model=List[ReviewOut])
def list_reviews_for_user(student_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT r.review_id,
                       r.student_id,
                       r.spot_id,
                       r.rating,
                       r.comment,
                       COALESCE(r.created_at, now()) AS created_at,
                       s.netid
                FROM reviews r
                JOIN students s ON s.student_id = r.student_id
                WHERE r.student_id = %s
                ORDER BY created_at DESC
                """,
                (student_id,),
            )

            rows = cur.fetchall()
            return [_map_review(r) for r in rows]


@router.post("/", response_model=ReviewOut)
def submit_review(data: ReviewIn):
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    INSERT INTO reviews (student_id, spot_id, rating, comment)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (student_id, spot_id)
                    DO UPDATE SET rating = EXCLUDED.rating,
                                  comment = EXCLUDED.comment,
                                  created_at = now()
                    RETURNING review_id, student_id, spot_id, rating, comment, created_at
                    """,
                    (data.student_id, data.spot_id, data.rating, data.comment),
                )
                row = cur.fetchone()
            except Exception as exc:
                conn.rollback()
                raise HTTPException(status_code=400, detail=str(exc))

            # Attach author/netid
            cur.execute(
                "SELECT netid FROM students WHERE student_id = %s",
                (row["student_id"],),
            )
            user = cur.fetchone()
            conn.commit()

            row["netid"] = user.get("netid") if user else "anonymous"
            return _map_review(row)
