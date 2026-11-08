from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from contextlib import asynccontextmanager

from core.database import init_db
from api import auth, users, disciplines

from models.users import *
from models.disciplines import *


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(disciplines.router)

@app.get("/")
def read_root():
    return {"stauts": "ok"}