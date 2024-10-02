from pydantic import BaseModel
from typing import List

class ItemInCart(BaseModel):
    id: int
    name: str
    quantity: int
    available: bool

class Cart(BaseModel):
    id: int
    items: List[ItemInCart]
    price: float

class Item(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool = False