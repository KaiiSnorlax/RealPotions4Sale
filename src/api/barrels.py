from typing import Tuple
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
<<<<<<< Updated upstream
import sqlalchemy
from src import database as db
=======
from utils import barrels_util, ledger
>>>>>>> Stashed changes

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)


class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int


@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):

    # Updates inventory stock considering a. how many barrels bought and b. barrel price

    for barrel in barrels_delivered:
<<<<<<< Updated upstream
        update_global_inventory = sqlalchemy.text(
            "UPDATE global_inventory SET num_green_ml = num_green_ml + (:ml_per_barrel * :quantity), gold = gold - (:price * :quantity)"
        ).bindparams(
            ml_per_barrel=barrel.ml_per_barrel,
            quantity=barrel.quantity,
            price=barrel.price,
=======
        barrels_util.barrel_delivered(
            Barrel(
                sku=barrel.sku,
                ml_per_barrel=barrel.ml_per_barrel,
                potion_type=barrel.potion_type,
                price=barrel.price,
                quantity=barrel.quantity,
            )
>>>>>>> Stashed changes
        )

        with db.engine.begin() as connection:
            connection.execute(update_global_inventory)

    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"


# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):

    # Purchase a green barrel if I have less than 10 green potions, enough gold, and if enough space in inventory (assuming I get 10000)
<<<<<<< Updated upstream

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
=======

    barrels_to_buy = barrels_util.create_barrel_plan(wholesale_catalog)

    # if ledger.account_amount("green_potion") < 10:
    #     for barrel in wholesale_catalog:
    #         if (
    #             barrel.potion_type == [0, 1, 0, 0]
    #             and ledger.account_amount("gold") >= barrel.price
    #             and ledger.account_amount("ml_capacity") >= barrel.ml_per_barrel
    #         ):
    #             ledger.gold_entry(-barrel.price)
    #             ledger.ml_capacity_entry(-barrel.ml_per_barrel)
    #             barrels_to_buy.append(BarrelOrder(sku=barrel.sku, quantity=1))

    # print(f"Barrel catalog: {wholesale_catalog}")
    # print(f"Barrel plan: {barrels_to_buy}")
    # return barrels_to_buy

    # with db.engine.begin() as connection:
    #     inventory = (
    #         connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
    #         .mappings()
    #         .first()
    #     )

    # free_space = 10000 - inventory["num_green_ml"]
    # barrels_to_buy = []

    # for barrel in wholesale_catalog:
    #     if (
    #         inventory["num_green_potions"] < 10
    #         and (current_gold >= barrel.price)
    #         and (barrel.potion_type == [0, 1, 0, 0])
    #         and (free_space >= barrel.ml_per_barrel)
    #     ):
    #         current_gold -= barrel.price
    #         free_space -= barrel.ml_per_barrel
    #         barrels_to_buy.append(BarrelOrder(sku=barrel.sku, quantity=1))
>>>>>>> Stashed changes

    print(f"Barrel catalog: {wholesale_catalog}")
    print(f"Barrel plan: {barrels_to_buy}")
    return barrels_to_buy
