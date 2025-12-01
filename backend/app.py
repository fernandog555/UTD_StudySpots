from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import auth, ratings, spots, saved_spots, reviews

app = FastAPI(title="Study Spots @ UTD API", version="0.1.0")


@app.get("/")
def root():
    return {"message": "Backend is running!"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # during development; can restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(spots.router)
app.include_router(ratings.router)
app.include_router(saved_spots.router)
app.include_router(reviews.router)
