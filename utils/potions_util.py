from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from utils import ledger
from typing import Tuple

colors = ["r", "g", "b", "d"]


class LiquidInventory(BaseModel):

    r: int
    g: int
    b: int
    d: int

    def from_tuple(potion: tuple[int, int, int, int]):
        return LiquidInventory(r=potion[0], g=potion[1], b=potion[2], d=potion[3])


class PotionRecipe(BaseModel):
    sku: str

    r: int
    g: int
    b: int
    d: int

    def from_tuple(sku: str, potion: tuple[int, int, int, int]):
        return PotionRecipe(sku=sku, r=potion[0], g=potion[1], b=potion[2], d=potion[3])


class BottlePlan(BaseModel):
    potion_type: PotionRecipe
    quantity: int

    def from_tuple(sku: str, potion: PotionRecipe, quantity: int):
        return BottlePlan(
            PotionRecipe(sku=sku, r=potion[0], g=potion[1], b=potion[2], d=potion[3]),
            quantity,
        )


def create_bottle_plan():
    recipes = get_potion_recipe()
    bottle_plan = []

    liquid_in_inventory = get_liquid_amount()

    for recipe in recipes:
        if (
            liquid_in_inventory.r >= recipe.r
            and liquid_in_inventory.g >= recipe.g
            and liquid_in_inventory.b >= recipe.b
            and liquid_in_inventory.d >= recipe.d
        ):
            max_craftable = get_max_recipe_craftable(recipe, liquid_in_inventory)
            for color in colors:
                setattr(
                    liquid_in_inventory,
                    color,
                    getattr(liquid_in_inventory, color)
                    - (max_craftable * getattr(recipe, color)),
                )

            bottle_plan.append(BottlePlan(potion_type=recipe, quantity=max_craftable))

    return bottle_plan


def get_potion_recipe():
    recipes = []

    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                "SELECT sku, red_ml, green_ml, blue_ml, dark_ml FROM potion_recipes"
            )
        )
        for row in result:
            recipes.append(
                PotionRecipe.from_tuple(
                    sku=row[0], potion=(row[1], row[2], row[3], row[4])
                )
            )

    return recipes


def get_liquid_amount():

    liquid_in_inventory = LiquidInventory.from_tuple(
        (
            ledger.account_amount("red_ml"),
            ledger.account_amount("green_ml"),
            ledger.account_amount("blue_ml"),
            ledger.account_amount("dark_ml"),
        )
    )

    return liquid_in_inventory


def get_max_recipe_craftable(
    recipe: PotionRecipe, liquid_in_inventory: LiquidInventory
):
    craftable_per_color = []
    for color in colors:
        if getattr(recipe, color) != 0:
            craftable_per_color.append(
                getattr(liquid_in_inventory, color) // getattr(recipe, color)
            )

    return min(craftable_per_color)
