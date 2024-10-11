from src.utils import ledger
from pydantic import BaseModel
from src.api.barrels import Barrel

colors = ["red_ml", "green_ml", "blue_ml", "dark_ml"]


class LiquidInventory(BaseModel):
    red_ml: int
    green_ml: int
    blue_ml: int
    dark_ml: int

    @staticmethod
    def from_tuple(potion: tuple[int, int, int, int]):
        return LiquidInventory(
            red_ml=potion[0], green_ml=potion[1], blue_ml=potion[2], dark_ml=potion[3]
        )


class BarrelOrder(BaseModel):
    sku: str
    quantity: int


def get_liquid_amount() -> LiquidInventory:
    liquid_in_inventory = LiquidInventory.from_tuple(
        (
            ledger.liquid_ledger_sum("red_ml"),
            ledger.liquid_ledger_sum("green_ml"),
            ledger.liquid_ledger_sum("blue_ml"),
            ledger.liquid_ledger_sum("dark_ml"),
        )
    )

    return liquid_in_inventory


def get_avaliable_liquid_space(liquid_in_inventory: LiquidInventory) -> int:
    liquid_capacity: int = ledger.liquid_capacity_sum()

    avaliable_space: int = liquid_capacity - (
        liquid_in_inventory.red_ml
        + liquid_in_inventory.green_ml
        + liquid_in_inventory.blue_ml
        + liquid_in_inventory.dark_ml
    )

    return avaliable_space


def get_barrel_type(barrel: Barrel) -> str:
    if barrel.potion_type[0] == 1:
        return "red_ml"
    elif barrel.potion_type[1] == 1:
        return "green_ml"
    elif barrel.potion_type[2] == 1:
        return "blue_ml"
    else:
        return "dark_ml"


# Creates a barrel plan depending of colors with stocks of 0.
# ** Will need to change in future when potions are not only 100ml of one color **
def create_barrel_plan(wholesale_catalog: list[Barrel]) -> list[BarrelOrder]:
    liquid_in_inventory: LiquidInventory = get_liquid_amount()
    avaliable_space: int = get_avaliable_liquid_space(liquid_in_inventory)
    avaliable_gold: int = ledger.gold_ledger_sum()

    barrels_to_buy: list[BarrelOrder] = []
    for color in colors:

        if getattr(liquid_in_inventory, color) <= 100:
            largest_barrel = get_largest_barrel(
                color, wholesale_catalog, avaliable_gold, avaliable_space
            )[0]
            avaliable_gold = get_largest_barrel(
                color, wholesale_catalog, avaliable_gold, avaliable_space
            )[1]
            avaliable_space = get_largest_barrel(
                color, wholesale_catalog, avaliable_gold, avaliable_space
            )[2]

            if largest_barrel is None:
                continue
            else:
                barrels_to_buy.append(largest_barrel)

    return barrels_to_buy


# Returns the largest barrel that a. we can afford, and b. wont overflow our storage.
def get_largest_barrel(
    color: str,
    wholesale_catalog: list[Barrel],
    avaliable_gold: int,
    avaliable_space: int,
) -> tuple[BarrelOrder | None, int, int]:
    largest_barrel: Barrel | None = None

    for barrel in wholesale_catalog:
        if (
            ((get_barrel_type(barrel) == color)
            and color != 'dark_ml'
            and (avaliable_gold >= barrel.price)
            and (avaliable_space >= barrel.ml_per_barrel)
            and barrel.ml_per_barrel <= 2500)
        ):
            if largest_barrel is None:
                largest_barrel = barrel

            elif barrel.ml_per_barrel > largest_barrel.ml_per_barrel:
                largest_barrel = barrel
        elif (
            ((get_barrel_type(barrel) == color)
            and color == 'dark_ml'
            and (avaliable_gold >= barrel.price)
            and (avaliable_space >= barrel.ml_per_barrel)
            and barrel.ml_per_barrel <= 10000)
        ):
            if largest_barrel is None:
                largest_barrel = barrel

            elif barrel.ml_per_barrel > largest_barrel.ml_per_barrel:
                largest_barrel = barrel

    if largest_barrel is None:
        return None, avaliable_gold, avaliable_space

    avaliable_gold -= largest_barrel.price
    avaliable_space -= largest_barrel.ml_per_barrel

    return (
        BarrelOrder(sku=largest_barrel.sku, quantity=1),
        avaliable_gold,
        avaliable_space,
    )


def barrel_delivered(barrel: Barrel) -> None:

    ledger.barrel_bought(barrel)
