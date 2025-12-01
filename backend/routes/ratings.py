from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, conint
from typing import Dict, List, Optional, Sequence, Tuple
from ..db import get_connection

router = APIRouter(prefix="/ratings", tags=["ratings"])

DEFAULT_CATEGORIES: Sequence[Tuple[str, str]] = (
    ("quietness", "Quietness"),
    ("lighting", "Lighting"),
    ("seating_comfort", "Seating Comfort"),
    ("accessibility", "Accessibility"),
)


def _get_vote_table_metadata(cur) -> Dict[str, object]:
    """
    Inspect the votes table to understand what columns are currently present
    (older datasets may still use `score` and omit comment/created_at).
    """
    cur.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'votes'
        """
    )
    cols = {row["column_name"] for row in cur.fetchall()}

    rating_column = "rating" if "rating" in cols else "score" if "score" in cols else "rating"

    return {
        "rating_column": rating_column,
        "has_comment": "comment" in cols,
        "has_created_at": "created_at" in cols,
        "columns": cols,
    }


# ========================
# Pydantic models
# ========================
class RatingIn(BaseModel):
    student_id: int
    spot_id: int
    category_id: int
    rating: conint(ge=1, le=5)
    comment: Optional[str] = None


class RatingOut(BaseModel):
    vote_id: int
    student_id: int
    spot_id: int
    category_id: int
    rating: int
    comment: Optional[str] = None
    created_at: Optional[datetime] = None


class CategoryOut(BaseModel):
    category_id: int
    slug: str
    display_name: str


# ------------------------
def _ensure_default_categories(cur) -> None:
    """Seed the categories table with defaults if it is empty."""

    cur.executemany(
        """
        INSERT INTO categories (slug, display_name)
        VALUES (%s, %s)
        ON CONFLICT (slug) DO NOTHING
        """,
        DEFAULT_CATEGORIES,
    )


def _normalize_vote_row(row: dict, meta: Dict[str, object]) -> dict:
    """Ensure the returned vote row always exposes a `rating` field."""
    normalized = dict(row) if row else {}
    rating_column = meta["rating_column"]
    if "rating" not in normalized and rating_column in normalized:
        normalized["rating"] = normalized[rating_column]
    if not meta["has_comment"]:
        normalized.setdefault("comment", None)
    if not meta["has_created_at"]:
        normalized.setdefault("created_at", None)
    return normalized


# ========================
# Submit or update a rating
# ========================
@router.post("/", response_model=RatingOut)
def submit_rating(data: RatingIn):

    with get_connection() as conn:
        with conn.cursor() as cur:
            meta = _get_vote_table_metadata(cur)
            rating_column = meta["rating_column"]

            # Attempt UPDATE first
            update_sets = [f"{rating_column} = %s"]
            update_values = [data.rating]

            if meta["has_comment"]:
                update_sets.append("comment = COALESCE(%s, votes.comment)")
                update_values.append(data.comment)

            if meta["has_created_at"]:
                update_sets.append("created_at = now()")

            where_values = [data.student_id, data.spot_id, data.category_id]

            cur.execute(
                f"""
                UPDATE votes
                SET {", ".join(update_sets)}
                WHERE student_id = %s AND spot_id = %s AND category_id = %s
                RETURNING *
                """,
                tuple(update_values + where_values),
            )

            row = cur.fetchone()

            if not row:
                insert_columns = ["student_id", "spot_id", "category_id", rating_column]
                insert_values = [data.student_id, data.spot_id, data.category_id, data.rating]

                if meta["has_comment"]:
                    insert_columns.append("comment")
                    insert_values.append(data.comment)

                placeholders = ", ".join(["%s"] * len(insert_columns))
                columns_sql = ", ".join(insert_columns)

                try:
                    cur.execute(
                        f"""
                        INSERT INTO votes ({columns_sql})
                        VALUES ({placeholders})
                        RETURNING *
                        """,
                        tuple(insert_values),
                    )
                except Exception as exc:
                    conn.rollback()
                    raise HTTPException(status_code=400, detail=str(exc))

                row = cur.fetchone()

            conn.commit()
            return _normalize_vote_row(row, meta)


# ========================
# Get rating categories
# ========================
@router.get("/categories", response_model=List[CategoryOut])
def list_categories():
    with get_connection() as conn:
        with conn.cursor() as cur:
            _ensure_default_categories(cur)
            conn.commit()

            cur.execute(
                """
                SELECT category_id, slug, display_name
                FROM categories
                ORDER BY category_id ASC
                """
            )
            return cur.fetchall()


# ========================
# Get average rating for a spot
# ========================
@router.get("/spot/{spot_id}")
def get_spot_ratings(spot_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            meta = _get_vote_table_metadata(cur)
            rating_column = meta["rating_column"]
            cur.execute(
                f"""
                SELECT
                    c.category_id,
                    c.display_name,
                    AVG(v.{rating_column})::numeric(10,2) AS avg_rating,
                    COUNT(v.vote_id) AS vote_count
                FROM votes v
                JOIN categories c ON c.category_id = v.category_id
                WHERE v.spot_id = %s
                GROUP BY c.category_id, c.display_name
                ORDER BY c.category_id
                """,
                (spot_id,),
            )

            return cur.fetchall()


# ========================
# Get user votes (for a specific user)
# ========================
@router.get("/user/{student_id}")
def get_user_votes(student_id: int):
    """Get all votes cast by a specific user"""
    with get_connection() as conn:
        with conn.cursor() as cur:
            meta = _get_vote_table_metadata(cur)
            rating_column = meta["rating_column"]
            
            cur.execute(
                f"""
                SELECT
                    v.vote_id,
                    v.student_id,
                    v.spot_id,
                    s.name as spot_name,
                    v.category_id,
                    c.slug,
                    c.display_name,
                    v.{rating_column} as rating,
                    v.comment,
                    v.created_at
                FROM votes v
                JOIN study_spots s ON s.spot_id = v.spot_id
                JOIN categories c ON c.category_id = v.category_id
                WHERE v.student_id = %s
                ORDER BY v.created_at DESC
                """,
                (student_id,),
            )
            
            return cur.fetchall()


# ========================
# Submit a vote (simplified for upvote/downvote)
# ========================
class SimpleVoteIn(BaseModel):
    student_id: int
    spot_id: int
    category_slug: str
    direction: int  # 1 for upvote, -1 for downvote


class SimpleVoteOut(BaseModel):
    vote_id: int
    student_id: int
    spot_id: int
    category_id: int
    rating: int
    created_at: Optional[datetime] = None


@router.post("/submit", response_model=SimpleVoteOut)
def submit_vote(data: SimpleVoteIn):
    """Submit or update a vote (1-5 scale where 1=strong downvote, 5=strong upvote)"""
    if data.direction not in [-1, 1]:
        raise HTTPException(status_code=400, detail="direction must be 1 or -1")
    
    # Convert direction to rating: -1 -> 1, 1 -> 5
    rating = 5 if data.direction == 1 else 1
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Get category_id from slug
            cur.execute(
                "SELECT category_id FROM categories WHERE slug = %s",
                (data.category_slug,),
            )
            category = cur.fetchone()
            if not category:
                raise HTTPException(status_code=400, detail="Category not found")
            
            category_id = category["category_id"]
            
            # Try to update existing vote
            cur.execute(
                """
                UPDATE votes
                SET rating = %s, created_at = now()
                WHERE student_id = %s AND spot_id = %s AND category_id = %s
                RETURNING *
                """,
                (rating, data.student_id, data.spot_id, category_id),
            )
            
            row = cur.fetchone()
            
            if not row:
                # Insert new vote
                try:
                    cur.execute(
                        """
                        INSERT INTO votes (student_id, spot_id, category_id, rating)
                        VALUES (%s, %s, %s, %s)
                        RETURNING *
                        """,
                        (data.student_id, data.spot_id, category_id, rating),
                    )
                    row = cur.fetchone()
                except Exception as exc:
                    conn.rollback()
                    raise HTTPException(status_code=400, detail=str(exc))
            
            conn.commit()
            return _normalize_vote_row(row, _get_vote_table_metadata(cur))


# ========================
# Delete a vote
# ========================
@router.delete("/vote/{vote_id}")
def delete_vote(vote_id: int):
    """Delete a specific vote"""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM votes WHERE vote_id = %s RETURNING vote_id",
                (vote_id,),
            )
            deleted = cur.fetchone()
            conn.commit()
            
            if not deleted:
                raise HTTPException(status_code=404, detail="Vote not found")
            
            return {"success": True, "vote_id": deleted["vote_id"]}
