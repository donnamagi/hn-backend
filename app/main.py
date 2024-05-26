from fastapi import FastAPI
from app.routers import db

app = FastAPI()

app.include_router(db.router)

@app.get("/")
async def root():
  return {"message": "Hello World"}
