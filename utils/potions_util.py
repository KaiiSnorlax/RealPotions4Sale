from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from utils import ledger


class PotionType:
    red_ml: int
    green_ml: int
    blue_ml: int
    dark_ml: int

    def __init__(self, potion: tuple[int, int, int, int]):
        self.red_ml = potion[0]
        self.green_ml = potion[1]
        self.blue_ml = potion[2]
        self.dark_ml = potion[3]


class BottlePlan(BaseModel):
    potion_type: list[int]
    quantity: int


def get_potion_blueprints():
    potions = []

    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("SELECT red_ml, green_ml, blue_ml, dark_ml FROM potions")
        )
        for row in result:
            potions.append(PotionType((row[0], row[1], row[2], row[3])))
    return potions


def potion_plan():
    potion_blueprints = get_potion_blueprints()
    potion_plan = []

    for potion in potion_blueprints:

        if (
            potion.red_ml <= ledger.account_amount("red_ml")
            and potion.green_ml <= ledger.account_amount("green_ml")
            and potion.blue_ml <= ledger.account_amount("blue_ml")
            and potion.dark_ml <= ledger.account_amount("dark_ml")
        ):
            quantity = amount_possible(potion)
            for color in ["red_ml", "green_ml", "blue_ml", "dark_ml"]:
                if getattr(potion, color) != 0:
                    ledger.ml_entry(f"{color}", -(quantity * getattr(potion, color)))

            potion_plan.append(
                BottlePlan(
                    potion_type=[
                        potion.red_ml,
                        potion.green_ml,
                        potion.blue_ml,
                        potion.dark_ml,
                    ],
                    quantity=quantity,
                )
            )
    return potion_plan


def amount_possible(potion):
    quantities = []

    for color in ["red_ml", "green_ml", "blue_ml", "dark_ml"]:
        if getattr(potion, color) != 0:
            quantities.append(
                ledger.account_amount(f"{color}") // getattr(potion, color)
            )

    can_make = min(quantities)

    return can_make


def potion_delivered(potion, quantity: int):

    for color in ["red_ml", "green_ml", "blue_ml", "dark_ml"]:
        if getattr(potion, color) > 0:
            ledger.ml_entry(color, (-getattr(potion, color) * quantity))

    find_potion_sku = sqlalchemy.text(
        "SELECT sku FROM potions WHERE red_ml = :red_ml AND green_ml = :yellow_ml AND blue_ml = :blue_ml AND dark_ml = :dark_ml"
    ).bindparams(
        red_ml=getattr(potion, "red_ml"),
        yellow_ml=getattr(potion, "green_ml"),
        blue_ml=getattr(potion, "blue_ml"),
        dark_ml=getattr(potion, "dark_ml"),
    )

    with db.engine.begin() as connection:
        result = connection.execute(find_potion_sku).mappings().first()

    ledger.potion_entry(result["sku"], quantity)

    return result["sku"]
