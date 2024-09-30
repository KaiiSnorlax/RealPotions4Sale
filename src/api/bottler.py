from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)


class BottlePlan(BaseModel):
    potion_type: list[int]
    quantity: int


class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int


@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):

    # Increment amount of green_potions based on quantity from BottlePlan

    for potion in potions_delivered:
        update_global_inventory = sqlalchemy.text(
            "UPDATE global_inventory SET num_green_potions = num_green_potions + :quantity"
        ).bindparams(quantity=potion.quantity)

        with db.engine.begin() as connection:
            connection.execute(update_global_inventory)

    print(f"potions delievered: {potions_delivered} order_id: {order_id}")

    return "OK"


@router.post("/plan")
def get_bottle_plan():

    # Creates a BottlePlan depending on how many multiples of 100ml of green I have and how much space I have left (assuming I get 50)

    with db.engine.begin() as connection:
        inventory = (
            connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
            .mappings()
            .first()
        )

    free_space = 50 - inventory["num_green_potions"]
    possible_potions = inventory["num_green_ml"] // 100

    potions_to_bottle = []

    if (free_space == 0) or (possible_potions == 0):
        print(f"Bottle plan: {potions_to_bottle}")
        return potions_to_bottle
    
    elif possible_potions >= free_space:
        potions_to_bottle.append(
            BottlePlan(
                potion_type=[0, 100, 0, 0],
                quantity=possible_potions - (possible_potions - free_space),
            )
        )

    else:
        potions_to_bottle.append(
            BottlePlan(potion_type=[0, 100, 0, 0], quantity=possible_potions)
        )

    print(f"Bottle plan: {potions_to_bottle}")
    return potions_to_bottle


if __name__ == "__main__":
    print(get_bottle_plan())
