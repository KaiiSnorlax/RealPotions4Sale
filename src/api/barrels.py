from typing import Tuple
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)


class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int, int, int, int]
    price: int

    quantity: int


class BarrelOrder(BaseModel):
    sku: str
    quantity: int


@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):

    # Updates inventory stock considering a. how many barrels bought and b. barrel price

    for barrel in barrels_delivered:
        update_global_inventory = sqlalchemy.text(
            "UPDATE global_inventory SET num_green_ml = num_green_ml + (:ml_per_barrel * :quantity), gold = gold - (:price * :quantity)"
        ).bindparams(
            ml_per_barrel=barrel.ml_per_barrel,
            quantity=barrel.quantity,
            price=barrel.price,
        )

        with db.engine.begin() as connection:
            connection.execute(update_global_inventory)

    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"


# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):

    # Purchase a green barrel if I have less than 10 green potions, enough gold, and if enough space in inventory (assuming I get 10000)

    with db.engine.begin() as connection:
        inventory = (
            connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
            .mappings()
            .first()
        )

    free_space = 10000 - inventory["num_green_ml"]
    barrels_to_buy = []

    current_gold = inventory["gold"]
    for barrel in wholesale_catalog:
        if (
            inventory["num_green_potions"] < 10
            and (current_gold >= barrel.price)
            and (barrel.potion_type == [0, 1, 0, 0])
            and (free_space >= barrel.ml_per_barrel)
        ):
            current_gold -= barrel.price
            free_space -= barrel.ml_per_barrel
            barrels_to_buy.append(BarrelOrder(sku=barrel.sku, quantity=1))

    print(f"Barrel catalog: {wholesale_catalog}, Barrel plan: {barrels_to_buy}")

    return barrels_to_buy
