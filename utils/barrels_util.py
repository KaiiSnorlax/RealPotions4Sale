from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from utils import ledger


def get_barrel_type(barrel: list[int]):
    if barrel[0] == 1:
        return "red_ml"
    elif barrel[1] == 1:
        return "green_ml"
    elif barrel[2] == 1:
        return "blue_ml"
    else:
        return "dark_ml"


def barrel_delivered(barrel: list[int], ml: int, quantity: int, price: int):

    color = str(get_barrel_type(barrel))

    ledger.ml_entry(color, (ml * quantity))
    ledger.gold_entry(-(price * quantity))
