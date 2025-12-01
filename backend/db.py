import psycopg
from psycopg.rows import dict_row
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    """
    Returns a fresh PostgreSQL connection.
    Each route should call get_connection() inside a 'with' block.
    """
    if DATABASE_URL is None:
        raise RuntimeError("DATABASE_URL is not set in .env")

    conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    return conn
