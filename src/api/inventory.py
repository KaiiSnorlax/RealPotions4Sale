from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
from src.utils import ledger

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
    """
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional
    capacity unit costs 1000 gold.
    """

    return {"potion_capacity": 0, "ml_capacity": 0}


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

    return "OK"
