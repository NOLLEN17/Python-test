from pydantic import BaseModel

class Movietop(BaseModel):
    id: int
    name: str
    cost: int
    director: str #