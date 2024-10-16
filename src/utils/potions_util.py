from pydantic import BaseModel
import sqlalchemy
from src import database as db
from src.utils.barrels_util import LiquidType
from src.utils import barrels_util, ledger


colors = ["red_ml", "green_ml", "blue_ml", "dark_ml"]


class PotionRecipe(BaseModel):
    sku: str
    name: str
    price: int

    potion_type: LiquidType

    @staticmethod
    def from_tuple(sku: str, name: str, price: int, potion: tuple[int, int, int, int]):
        return PotionRecipe(
            sku=sku, name=name, price=price, potion_type=LiquidType.from_tuple(potion)
        )


class PotionInventory(BaseModel):
    recipe: PotionRecipe
    stock: int


class BottlePlan(BaseModel):
    potion_type: tuple[int, int, int, int]
    quantity: int


def get_potion_plan() -> list[BottlePlan]:
    potions = get_potion_inventory()
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


def get_potion_inventory() -> list[PotionInventory]:
    potion_inventory: list[PotionInventory] = []

    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """SELECT distinct
                    potion_recipes.sku, potion_recipes.potion_name, potion_recipes.price, potion_recipes.red_ml, potion_recipes.green_ml, potion_recipes.blue_ml, potion_recipes.dark_ml, coalesce(sum(change), 0) as stock 
                   FROM
                    potion_recipes
                   LEFT JOIN potion_ledger ON potion_ledger.sku = potion_recipes.sku
                   where potion_recipes.craft = true
                   GROUP BY potion_recipes.sku
                   ORDER BY coalesce(sum(change), 0)"""
            )
        )
        for row in result:
            potion_inventory.append(
                PotionInventory(
                    recipe=PotionRecipe.from_tuple(
                        sku=row[0],
                        name=row[1],
                        price=row[2],
                        potion=(row[3], row[4], row[5], row[6]),
                    ),
                    stock=row[7],
                ),
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


def get_sku_from_type(potion_type: tuple[int, int, int, int]) -> str:
    potions: list[PotionInventory] = get_potion_inventory()

    for potion in potions:
        if potion_type == (
            potion.recipe.potion_type.red_ml,
            potion.recipe.potion_type.green_ml,
            potion.recipe.potion_type.blue_ml,
            potion.recipe.potion_type.dark_ml,
        ):
            return potion.recipe.sku

    raise RuntimeError(f"Potion type {potion_type} not found in table: potion_recipes")
