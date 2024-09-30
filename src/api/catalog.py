from typing import Tuple
from fastapi import APIRouter
from pydantic import BaseModel
import sqlalchemy
from src import database as db

router = APIRouter()


class Catalog(BaseModel):
    sku: str
    name: str
    quantity: int
    price: int
    potion_type: Tuple[int, int, int, int]


@router.get("/catalog/", tags=["catalog"])
def get_catalog():

    # Lists out all green potions in stock, if none are in stock return empty array.

    current_stock = "SELECT num_green_potions FROM global_inventory"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(current_stock)).mappings().first()
    if result["num_green_potions"] > 0:
        return Catalog(
            sku="GREEN_POTION_0",
            name="green potion",
            quantity=result["num_green_potions"],
            price=50,
            potion_type=(0, 100, 0, 0),
        )
    else:
        return []
