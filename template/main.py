from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from database import engine, Base, get_db
import models

app = FastAPI(title="Generated API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok"}


# AGENT: write your Pydantic schemas here
# Rules:
# 1. Every resource needs: {Resource}Create, {Resource}Update, {Resource}Out
# 2. {Resource}Out must have: model_config = ConfigDict(from_attributes=True)
# 3. {Resource}Update fields must all be Optional


# AGENT: write your endpoints STRICTLY in this order:
#
# STEP 1 - Collection routes (no path parameter)
#   GET    /items         list all (paginated, use skip + limit)
#   POST   /items         create one
#
# STEP 2 - Aggregation routes (named paths, MUST come before /{id})
#   GET    /items/stats   counts, averages, totals
#
# STEP 3 - Single resource routes (path parameter LAST)
#   GET    /items/{id}    get one
#   PUT    /items/{id}    update one
#   DELETE /items/{id}    delete one
#
# WARNING: Never define /{id} before /stats.
# FastAPI matches top to bottom. /todos/{id} will swallow /todos/stats
# treating "stats" as an id, making the stats endpoint unreachable.