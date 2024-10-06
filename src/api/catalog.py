from typing import Tuple
from fastapi import APIRouter
from pydantic import BaseModel
from utils import potions_util

router = APIRouter()


class Catalog(BaseModel):
    sku: str
    name: str
    quantity: int
    price: int
    potion_type: Tuple[int, int, int, int]


@router.get("/catalog/", tags=["catalog"])
def get_catalog():

<<<<<<< Updated upstream
    # Lists out all green potions in stock, if none are in stock return empty array.
    current_stock = sqlalchemy.text("SELECT num_green_potions FROM global_inventory")

    with db.engine.begin() as connection:
        result = connection.execute(current_stock).mappings().first()

    current_catalog = []
    if result["num_green_potions"] > 0:
        current_catalog.append(
            Catalog(
                sku="GREEN_POTION_0",
                name="green potion",
                quantity=result["num_green_potions"],
                price=50,
                potion_type=(0, 100, 0, 0),
            )
        )
    print(f"Catalog: {current_catalog}")
    return current_catalog
=======
    catalog = potions_util.get_current_catalog()

    return catalog
>>>>>>> Stashed changes
