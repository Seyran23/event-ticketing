from fastapi import FastAPI

from app.auth.api import router as auth_router

app = FastAPI(title="Event Ticketing")


app.include_router(auth_router)