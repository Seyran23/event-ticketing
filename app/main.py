from fastapi import FastAPI

app = FastAPI(title="Event Ticketing")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
