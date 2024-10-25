from pydantic import BaseModel
import sqlalchemy
from src import database as db
from src.utils.barrels_util import LiquidType
from src.utils import barrels_util, ledger


colors = ["red_ml", "green_ml", "blue_ml", "dark_ml"]


class PotionRecipe(BaseModel):
    potion_id: int
    sku: str
    name: str
    price: int

    potion_type: LiquidType


class PotionInventory(BaseModel):
    recipe: PotionRecipe
    stock: int


class BottlePlan(BaseModel):
    potion_type: tuple[int, int, int, int]
    quantity: int


def get_potion_plan() -> list[BottlePlan]:
    potions = get_craftable_potions()
    craftables: dict[tuple[int, int, int, int], int] = {}

    free_space = ledger.potion_capacity_sum() - ledger.all_potions_sum()

    avaliable_liquid = barrels_util.get_liquid_amount()

    print(avaliable_liquid)
    while len(potions) > 0 and free_space > 0:
        lowest_stock = min(potions, key=lambda potion: potion.stock)

        if not craftable(lowest_stock.recipe.potion_type, avaliable_liquid):
            potions.pop(potions.index(lowest_stock))

        else:
            lowest_stock.stock += 1
            free_space -= 1
            avaliable_liquid = update_avaliable_liquid(
                avaliable_liquid, lowest_stock.recipe.potion_type
            )

            if lowest_stock.recipe.potion_type.to_tuple() in craftables:
                craftables[lowest_stock.recipe.potion_type.to_tuple()] += 1

            else:
                craftables[lowest_stock.recipe.potion_type.to_tuple()] = 1

    if len(craftables) > 0:
        return add_potions_to_plan(craftables)
    else:
        return []


def craftable(potion: LiquidType, liquid_in_inventory: LiquidType):
    for i in range(4):
        if liquid_in_inventory.to_tuple()[i] < potion.to_tuple()[i]:
            return False

    return True


def add_potions_to_plan(craftables: dict[tuple[int, int, int, int], int]):
    bottle_plan: list[BottlePlan] = []
    for key in craftables:
        bottle_plan.append(BottlePlan(potion_type=key, quantity=craftables[key]))
    return bottle_plan


def update_avaliable_liquid(
    avaliable_liquid: LiquidType, potion: LiquidType
) -> LiquidType:
    for color in colors:
        if getattr(potion, color) != 0:
            setattr(
                avaliable_liquid,
                color,
                getattr(avaliable_liquid, color) - getattr(potion, color),
            )
    return avaliable_liquid


def get_craftable_potions() -> list[PotionInventory]:
    potion_inventory: list[PotionInventory] = []

    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """SELECT distinct
                    potion.id, potion.sku, potion.name, potion.price, potion.red_ml, potion.green_ml, potion.blue_ml, potion.dark_ml, coalesce(sum(change), 0) as stock 
                   FROM
                    potion
                   LEFT JOIN potion_ledger ON potion_ledger.potion_id = potion.id
                   where potion.craft = true
                   GROUP BY potion.id
                   ORDER BY coalesce(sum(change), 0)"""
            )
        )

        for row in result:

            potion_inventory.append(
                PotionInventory(
                    recipe=PotionRecipe(
                        potion_id=row.id,
                        sku=row.sku,
                        name=row.name,
                        price=row.price,
                        potion_type=LiquidType.from_tuple(
                            (row.red_ml, row.green_ml, row.blue_ml, row.dark_ml)
                        ),
                    ),
                    stock=row.stock,
                )
            )

    return potion_inventory


def get_potion_recipes() -> list[PotionInventory]:
    potion_inventory: list[PotionInventory] = []

    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """SELECT distinct
                    potion.id, potion.sku, potion.name, potion.price, potion.red_ml, potion.green_ml, potion.blue_ml, potion.dark_ml, coalesce(sum(change), 0) as stock 
                   FROM
                    potion
                   LEFT JOIN potion_ledger ON potion_ledger.potion_id = potion.id
                   GROUP BY potion.id
                   ORDER BY coalesce(sum(change), 0)"""
            )
        )

        for row in result:

            potion_inventory.append(
                PotionInventory(
                    recipe=PotionRecipe(
                        potion_id=row.id,
                        sku=row.sku,
                        name=row.name,
                        price=row.price,
                        potion_type=LiquidType.from_tuple(
                            (row.red_ml, row.green_ml, row.blue_ml, row.dark_ml)
                        ),
                    ),
                    stock=row.stock,
                )
            )

    return potion_inventory


def get_max_recipe_craftable(
    recipe: PotionRecipe, liquid_in_inventory: LiquidType
) -> int:
    craftable_per_color: list[int] = []

    for color in colors:
        if getattr(recipe, color) != 0:
            craftable_per_color.append(
                getattr(liquid_in_inventory, color) // getattr(recipe, color)
            )

    return min(craftable_per_color)


def get_potion_from_type(potion_type: tuple[int, int, int, int]) -> PotionInventory:
    potions: list[PotionInventory] = get_craftable_potions()

    for potion in potions:
        if potion_type == (
            potion.recipe.potion_type.red_ml,
            potion.recipe.potion_type.green_ml,
            potion.recipe.potion_type.blue_ml,
            potion.recipe.potion_type.dark_ml,
        ):
            return potion

    raise RuntimeError(f"Potion type {potion_type} not found in table: potion")


def get_id_from_sku(potion_sku: str) -> int:
    potions: list[PotionInventory] = get_potion_recipes()

    for potion in potions:
        if potion_sku == potion.recipe.sku:
            return potion.recipe.potion_id

    raise RuntimeError(f"Potion type {potion_sku} not found in table: potion")
