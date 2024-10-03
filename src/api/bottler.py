from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from utils import potions_util, ledger

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)


class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int


@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):

    # Increment amount of green_potions based on quantity from BottlePlan

    for potion in potions_delivered:
        sku = potions_util.potion_delivered(
            potions_util.PotionType(
                (
                    potion.potion_type[0],
                    potion.potion_type[1],
                    potion.potion_type[2],
                    potion.potion_type[3],
                )
            ),
            potion.quantity,
        )
        print(ledger.account_amount(sku))

    return "OK"


@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Creates a BottlePlan depending on how many multiples of 100ml of green I have and how much space I have left (assuming I get 50)
    plan = potions_util.get_potion_recipe()
    print(f"Bottle plan: {plan}")
    return plan


if __name__ == "__main__":
    print(get_bottle_plan())
