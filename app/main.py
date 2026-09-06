from fastapi import FastAPI

from app.admin.api import router as admin_router
from app.auth.api import router as auth_router
from app.core.error_handlers import register_exception_handlers
from app.events.api import router as events_router
from app.venues.api import router as venues_router

app = FastAPI(title="Event Ticketing")

register_exception_handlers(app)


app.include_router(auth_router)
app.include_router(venues_router)
app.include_router(events_router)
app.include_router(admin_router)
