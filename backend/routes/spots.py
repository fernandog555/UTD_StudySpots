from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, constr
from typing import Optional, List
from ..db import get_connection

router = APIRouter(prefix="/spots", tags=["spots"])


# ========================
# Pydantic models
# ========================
class SpotIn(BaseModel):
    name: constr(strip_whitespace=True, max_length=120)
    building_code: constr(strip_whitespace=True, max_length=16)
    area_description: Optional[str] = None
    seating_capacity: int = 0
    power_outlets: bool = False
    natural_light: bool = False
    open_24_7: bool = False
    is_active: bool = True
    student_id: Optional[int] = None


class SpotUpdate(BaseModel):
    name: Optional[constr(strip_whitespace=True, max_length=120)] = None
    building_code: Optional[constr(strip_whitespace=True, max_length=16)] = None
    area_description: Optional[str] = None
    seating_capacity: Optional[int] = None
    power_outlets: Optional[bool] = None
    natural_light: Optional[bool] = None
    open_24_7: Optional[bool] = None
    is_active: Optional[bool] = None


class SpotOut(BaseModel):
    spot_id: int
    name: str
    building_code: str
    area_description: Optional[str]
    seating_capacity: int
    power_outlets: bool
    natural_light: bool
    open_24_7: bool
    is_active: bool
    created_at: datetime
    student_id: Optional[int] = None


# ========================
# Get all spots
# ========================
@router.get("/", response_model=List[SpotOut])
def list_spots():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM study_spots ORDER BY name ASC")
            return cur.fetchall()


# ========================
# Get spots by student (contributed spots)
# ========================
@router.get("/user/{student_id}", response_model=List[SpotOut])
def list_spots_by_student(student_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM study_spots WHERE student_id = %s ORDER BY created_at DESC",
                (student_id,),
            )
            return cur.fetchall()


# ========================
# Create a new study spot
# ========================
@router.post("/", response_model=SpotOut)
def create_spot(data: SpotIn):

    with get_connection() as conn:
        with conn.cursor() as cur:

            # Ensure no duplicates by name + building
            cur.execute(
                "SELECT spot_id FROM study_spots WHERE name = %s AND building_code = %s",
                (data.name, data.building_code)
            )
            exists = cur.fetchone()

            if exists:
                raise HTTPException(400, "Spot already exists in this building")

            cur.execute(
                """
                INSERT INTO study_spots (
                    name, building_code, area_description,
                    seating_capacity, power_outlets, natural_light,
                    open_24_7, is_active, student_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
                """,
                (
                    data.name,
                    data.building_code,
                    data.area_description,
                    data.seating_capacity,
                    data.power_outlets,
                    data.natural_light,
                    data.open_24_7,
                    data.is_active,
                    data.student_id,
                )
            )

            new_spot = cur.fetchone()
            conn.commit()
            return new_spot


# ========================
# Update an existing study spot
# ========================
@router.put("/{spot_id}", response_model=SpotOut)
def update_spot(spot_id: int, data: SpotUpdate):
    if not any([
        data.name is not None,
        data.building_code is not None,
        data.area_description is not None,
        data.seating_capacity is not None,
        data.power_outlets is not None,
        data.natural_light is not None,
        data.open_24_7 is not None,
        data.is_active is not None,
    ]):
        raise HTTPException(status_code=400, detail="No fields to update")

    with get_connection() as conn:
        with conn.cursor() as cur:
            # Ensure spot exists
            cur.execute("SELECT * FROM study_spots WHERE spot_id = %s", (spot_id,))
            existing = cur.fetchone()
            if not existing:
                raise HTTPException(status_code=404, detail="Spot not found")

            # Duplicate check if updating name/building_code
            if data.name is not None or data.building_code is not None:
                new_name = data.name if data.name is not None else existing["name"]
                new_building = data.building_code if data.building_code is not None else existing["building_code"]
                cur.execute(
                    "SELECT spot_id FROM study_spots WHERE name = %s AND building_code = %s AND spot_id <> %s",
                    (new_name, new_building, spot_id),
                )
                duplicate = cur.fetchone()
                if duplicate:
                    raise HTTPException(status_code=400, detail="Another spot already uses this name/building")

            fields = []
            values = []
            for col, val in (
                ("name", data.name),
                ("building_code", data.building_code),
                ("area_description", data.area_description),
                ("seating_capacity", data.seating_capacity),
                ("power_outlets", data.power_outlets),
                ("natural_light", data.natural_light),
                ("open_24_7", data.open_24_7),
                ("is_active", data.is_active),
            ):
                if val is not None:
                    fields.append(f"{col} = %s")
                    values.append(val)

            values.append(spot_id)

            cur.execute(
                f"""
                UPDATE study_spots
                SET {', '.join(fields)}
                WHERE spot_id = %s
                RETURNING *
                """,
                tuple(values),
            )

            updated = cur.fetchone()
            conn.commit()
            return updated


# ========================
# Delete a study spot
# ========================
@router.delete("/{spot_id}")
def delete_spot(spot_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM study_spots WHERE spot_id = %s RETURNING spot_id",
                (spot_id,)
            )

            deleted = cur.fetchone()
            conn.commit()

            if not deleted:
                raise HTTPException(status_code=404, detail="Spot not found")

            return {"success": True, "spot_id": deleted["spot_id"]}

# ========================
# Get a single study spot by ID
# ========================
@router.get("/{spot_id}", response_model=SpotOut)
def get_spot(spot_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                "SELECT * FROM study_spots WHERE spot_id = %s",
                (spot_id,)
            )
            spot = cur.fetchone()

            if not spot:
                raise HTTPException(status_code=404, detail="Spot not found")

            return spot
