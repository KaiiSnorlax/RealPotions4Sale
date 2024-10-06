from utils import ledger
from pydantic import BaseModel
from src.api.barrels import Barrel


class LiquidInventory(BaseModel):

    red_ml: int
    green_ml: int
    blue_ml: int
    dark_ml: int

    def from_tuple(potion: tuple[int, int, int, int]):
        return LiquidInventory(
            red_ml=potion[0], green_ml=potion[1], blue_ml=potion[2], dark_ml=potion[3]
        )


class BarrelOrder(BaseModel):
    sku: str
    quantity: int


def get_liquid_amount():

    liquid_in_inventory = LiquidInventory.from_tuple(
        (
            ledger.liquid_ledger_sum("red_ml"),
            ledger.liquid_ledger_sum("green_ml"),
            ledger.liquid_ledger_sum("blue_ml"),
            ledger.liquid_ledger_sum("dark_ml"),
        )
    )

    return liquid_in_inventory


def create_barrel_plan(wholesale_catalog: list[Barrel]):
    barrels_to_buy = []

    liquid_in_inventory = get_liquid_amount()
    current_gold = ledger.gold_ledger_sum()
    current_liquid_capacity = ledger.liquid_capacity_sum()

    free_space = current_liquid_capacity - (
        liquid_in_inventory.red_ml
        + liquid_in_inventory.green_ml
        + liquid_in_inventory.blue_ml
        + liquid_in_inventory.dark_ml
    )

    priority_color = min(liquid_in_inventory, key=lambda x: x[1])[0]

    for i in range(4):

        for barrel in wholesale_catalog:
            if (
                get_barrel_type(barrel) == priority_color
                and barrel.price <= current_gold
                and free_space >= current_liquid_capacity
            ):
                current_gold -= barrel.price
                barrels_to_buy.append(BarrelOrder(sku=barrel.sku, quantity=1))

                setattr(
                    liquid_in_inventory,
                    priority_color,
                    (
                        getattr(liquid_in_inventory, priority_color)
                        + barrel.ml_per_barrel
                    ),
                )

                free_space -= barrel.ml_per_barrel

                priority_color = min(liquid_in_inventory, key=lambda x: x[1])[0]

    return barrels_to_buy


def get_barrel_type(barrel: Barrel):
    if barrel.potion_type[0] == 1:
        return "red_ml"
    elif barrel.potion_type[1] == 1:
        return "green_ml"
    elif barrel.potion_type[2] == 1:
        return "blue_ml"
    else:
        return "dark_ml"


def barrel_delivered(barrel: Barrel):

    ledger.barrel_bought(barrel)
