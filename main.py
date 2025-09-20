from fastapi import FastAPI
from routers import webhooks, functions, bots

# Create FastAPI app
app = FastAPI(
    title="Medical Intake Agent",
    description="Backend for a Medical AI Intake Agent using OpenMic API",
    version="1.0.0"
)

# Register routers
app.include_router(webhooks.router, tags=["Webhooks"])
app.include_router(functions.router, tags=["Functions"])
app.include_router(bots.router, tags=["Bots"])


@app.get("/")
async def root():
    return {"message": "Medical Intake Agent backend is running"}
