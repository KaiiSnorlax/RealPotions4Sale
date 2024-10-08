from pydantic import BaseModel
import sqlalchemy
from src import database as db
from src.utils.barrels_util import LiquidInventory
from src.api.catalog import Catalog
from src.utils import barrels_util, ledger


colors = ["red_ml", "green_ml", "blue_ml", "dark_ml"]


class PotionRecipe(BaseModel):
    sku: str
    name: str
    price: int

    red_ml: int
    green_ml: int
    blue_ml: int
    dark_ml: int

    @staticmethod
    def from_tuple(sku: str, name: str, price: int, potion: tuple[int, int, int, int]):
        return PotionRecipe(
            sku=sku,
            name=name,
            price=price,
            red_ml=potion[0],
            green_ml=potion[1],
            blue_ml=potion[2],
            dark_ml=potion[3],
        )


class BottlePlan(BaseModel):
    potion_type: list[int]
    quantity: int


def create_bottle_plan() -> list[BottlePlan]:
    recipes = get_potion_recipes()
    bottle_plan: list[BottlePlan] = []

    free_space = ledger.potion_capacity_sum() - ledger.all_potions_sum()

    liquid_in_inventory = barrels_util.get_liquid_amount()

    for recipe in recipes:
        if free_space == 0:
            return bottle_plan
        if (
            liquid_in_inventory.red_ml >= recipe.red_ml
            and liquid_in_inventory.green_ml >= recipe.green_ml
            and liquid_in_inventory.blue_ml >= recipe.blue_ml
            and liquid_in_inventory.dark_ml >= recipe.dark_ml
        ):
            max_craftable = get_max_recipe_craftable(recipe, liquid_in_inventory)
            if max_craftable > free_space:
                can_make = free_space
                free_space = 0
            else:
                can_make = max_craftable
                free_space -= can_make

            bottle_plan.append(
                BottlePlan(
                    potion_type=[
                        recipe.red_ml,
                        recipe.green_ml,
                        recipe.blue_ml,
                        recipe.dark_ml,
                    ],
                    quantity=can_make,
                )
            )

    return bottle_plan


def get_potion_recipes() -> list[PotionRecipe]:
    recipes: list[PotionRecipe] = []

    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """SELECT
                    sku, potion_name, price, red_ml, green_ml, blue_ml, dark_ml
                   FROM
                    potion_recipes"""
            )
        )
        for row in result:
            recipes.append(
                PotionRecipe.from_tuple(
                    sku=row[0],
                    name=row[1],
                    price=row[2],
                    potion=(row[3], row[4], row[5], row[6]),
                )
            )

    return recipes


def get_max_recipe_craftable(
    recipe: PotionRecipe, liquid_in_inventory: LiquidInventory
) -> int:
    craftable_per_color: list[int] = []

    for color in colors:
        if getattr(recipe, color) != 0:
            craftable_per_color.append(
                getattr(liquid_in_inventory, color) // getattr(recipe, color)
            )

    return min(craftable_per_color)


def get_sku_from_type(potion_type: tuple[int, int, int, int]) -> str:
    recipes: list[PotionRecipe] = get_potion_recipes()

    for recipe in recipes:
        if potion_type == (
            recipe.red_ml,
            recipe.green_ml,
            recipe.blue_ml,
            recipe.dark_ml,
        ):
            return recipe.sku

    raise RuntimeError(f"Potion type {potion_type} not found in table: potion_recipes")


def get_current_catalog() -> list[Catalog]:
    recipes: list[PotionRecipe] = get_potion_recipes()
    catalog: list[Catalog] = []
    spots: int = 6

    for recipe in recipes:
        if ledger.potion_ledger_sum(recipe.sku) > 0 and spots > 0:
            catalog.append(
                Catalog(
                    sku=recipe.sku,
                    name=recipe.name,
                    quantity=ledger.potion_ledger_sum(recipe.sku),
                    price=recipe.price,
                    potion_type=(
                        recipe.red_ml,
                        recipe.green_ml,
                        recipe.blue_ml,
                        recipe.dark_ml,
                    ),
                )
            )
            spots -= 1

    return catalog
