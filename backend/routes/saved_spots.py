from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from ..db import get_connection

router = APIRouter(prefix="/saved-spots", tags=["saved_spots"])


class SavedSpotIn(BaseModel):
    student_id: int
    spot_id: int


class SavedSpotOut(BaseModel):
    spot_id: int
    name: str
    building_code: str
    area_description: Optional[str] = None
    seating_capacity: int
    power_outlets: bool
    natural_light: bool
    open_24_7: bool
    is_active: bool


@router.get("/{student_id}", response_model=List[SavedSpotOut])
def list_saved_spots(student_id: int):
    """Return all saved/bookmarked spots for a student (joined with spot details)."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT s.spot_id,
                       s.name,
                       s.building_code,
                       s.area_description,
                       s.seating_capacity,
                       s.power_outlets,
                       s.natural_light,
                       s.open_24_7,
                       s.is_active
                FROM saved_spots ss
                JOIN study_spots s ON s.spot_id = ss.spot_id
                WHERE ss.student_id = %s
                ORDER BY s.name ASC
                """,
                (student_id,),
            )

            return cur.fetchall()


@router.post("/", response_model=SavedSpotIn)
def save_spot(data: SavedSpotIn):
    """Save/bookmark a spot for a student."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    INSERT INTO saved_spots (student_id, spot_id)
                    VALUES (%s, %s)
                    ON CONFLICT (student_id, spot_id) DO NOTHING
                    RETURNING student_id, spot_id
                    """,
                    (data.student_id, data.spot_id),
                )
            except Exception as exc:
                conn.rollback()
                raise HTTPException(status_code=400, detail=str(exc))

            row = cur.fetchone()
            conn.commit()

            # If the row already existed, return the input for idempotency
            return {"student_id": data.student_id, "spot_id": data.spot_id} if not row else row


@router.delete("/{student_id}/{spot_id}")
def delete_saved_spot(student_id: int, spot_id: int):
    """Remove a bookmarked spot for a student."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM saved_spots WHERE student_id = %s AND spot_id = %s RETURNING spot_id",
                (student_id, spot_id),
            )
            deleted = cur.fetchone()
            conn.commit()

            if not deleted:
                raise HTTPException(status_code=404, detail="Bookmark not found")

            return {"success": True, "spot_id": deleted["spot_id"]}
