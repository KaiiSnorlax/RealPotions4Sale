from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
from src.utils import ledger
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)


class Inventory(BaseModel):
    potions: int
    liquids: int
    gold: int


@router.get("/audit")
def get_inventory():
    inventory = Inventory(
        potions=ledger.all_potions_sum(),
        liquids=ledger.all_liquid_sum(),
        gold=ledger.gold_ledger_sum(),
    )

    print(f"Audit: {inventory}")

    return {
        "number_of_potions": inventory.potions,
        "ml_in_barrels": inventory.liquids,
        "gold": inventory.gold,
    }


# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    potion_capacity_upgrade: int = 0
    liquid_capacity_upgrade: int = 0
    with db.engine.begin() as connection:
        capacity_plan = connection.execute(
            sqlalchemy.text(
                """
                SELECT potion_capacity_upgrade, liquid_capacity_upgrade FROM parameter
                WHERE (
                    SELECT coalesce(sum(change), 0) as total_gold FROM gold_ledger
                ) - (potion_capacity_upgrade + liquid_capacity_upgrade) * 1000 >= 100
                """
            )
        )
        for row in capacity_plan:
            potion_capacity_upgrade = row.potion_capacity_upgrade
            liquid_capacity_upgrade = row.liquid_capacity_upgrade

    print(
        f"Capacity plan: potion inventory upgraded by {potion_capacity_upgrade * 50}, liquid inventory upgrade by {liquid_capacity_upgrade * 10000}"
    )
    return {
        "potion_capacity": potion_capacity_upgrade,
        "ml_capacity": liquid_capacity_upgrade,
    }


class CapacityPurchase(BaseModel):
    potion_capacity: int
    ml_capacity: int


# Gets called once a day
@router.post("/deliver/{order_id}")
def deliver_capacity_plan(capacity_purchase: CapacityPurchase, order_id: int):
    """
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional
    capacity unit costs 1000 gold.
    """
    ledger.capacity_upgrade(capacity_purchase.ml_capacity, capacity_purchase.potion_capacity)

    return "OK"
