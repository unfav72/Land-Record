from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import engine
import models
from config import settings

# Import routers
from routers import auth, documents, records, dashboard, search, export, users
from seed_data import seed_db

# Ensure tables are created and data is seeded
models.Base.metadata.create_all(bind=engine)
seed_db()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exactly the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(documents.router)
app.include_router(records.router)
app.include_router(dashboard.router)
app.include_router(search.router)
app.include_router(export.router)

@app.get("/")
def root():
    return {"message": "Welcome to Intelligent Land Record Digitization API"}
