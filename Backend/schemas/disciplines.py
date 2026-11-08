from pydantic import BaseModel, ConfigDict, Field


class DisciplineCreateSchema(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class DisciplineUpdateSchema(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class DisciplineResponseSchema(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)