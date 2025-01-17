import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from constants import CLEANED_DATA_FOLDER, DATA_FOLDER
from routes.uploads import upload_router
from routes.query import query_router

app = FastAPI(title="RAG Pipeline")
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.on_event("startup")
def startup():
    os.makedirs(DATA_FOLDER, exist_ok=True)
    os.makedirs(CLEANED_DATA_FOLDER, exist_ok=True)

@app.get("/api_docs")
async def api_docs():
    with open("openapi.json", "r") as f:
        data = json.load(f)
        return data

app.include_router(upload_router, prefix="/upload")
app.include_router(query_router, prefix="/query")
