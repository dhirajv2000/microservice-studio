from typing import List
from pydantic import BaseModel, Field


class PlanField(BaseModel):
    name: str = Field(description="Field name, e.g. 'title' or 'created_at'")
    type: str = Field(
        description="SQLAlchemy column type: Integer, String, DateTime, Float, Boolean"
    )
    nullable: bool = Field(default=True)


class PlanModel(BaseModel):
    name: str = Field(description="Class name in PascalCase, e.g. 'Todo'")
    table_name: str = Field(description="Database table name in snake_case plural, e.g. 'todos'")
    fields: List[PlanField] = Field(
        description="All fields EXCEPT id — id is added automatically"
    )


class PlanEndpoint(BaseModel):
    method: str = Field(description="HTTP method: GET, POST, PUT, DELETE")
    path: str = Field(description="URL path, e.g. '/todos' or '/todos/stats' or '/todos/{id}'")
    description: str = Field(description="One sentence describing what this endpoint does")


class ArchitecturePlan(BaseModel):
    models: List[PlanModel]
    endpoints: List[PlanEndpoint]
    notes: str = Field(default="", description="Optional implementation notes for the developer")