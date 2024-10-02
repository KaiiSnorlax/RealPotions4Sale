from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db


def ml_entry(color: str, change: int):

    ledger_ml_entry = sqlalchemy.text(
        "INSERT INTO ledger (account, change) VALUES (:color, :change)"
    ).bindparams(color=color, change=change)

    with db.engine.begin() as connection:
        connection.execute(ledger_ml_entry)

    return


def potion_entry(potion_sku: str, change: int):
    ledger_potion_entry = sqlalchemy.text(
        "INSERT INTO ledger (account, change) VALUES (:sku, :change)"
    ).bindparams(sku=potion_sku, change=change)

    with db.engine.begin() as connection:
        connection.execute(ledger_potion_entry)

    return


def gold_entry(change: int):

    ledger_gold_entry = sqlalchemy.text(
        "INSERT INTO ledger (account, change) VALUES ('gold', :change)"
    ).bindparams(change=change)

    with db.engine.begin() as connection:
        connection.execute(ledger_gold_entry)


def ml_capacity_entry(change: int):

    ledger_ml_capacity_entry = sqlalchemy.text(
        "INSERT INTO ledger (account, change) VALUES ('ml_capacity', :change)"
    ).bindparams(change=change)

    with db.engine.begin() as connection:
        connection.execute(ledger_ml_capacity_entry)


def potion_capacity_entry(change: int):

    ledger_potion_capacity_entry = sqlalchemy.text(
        "INSERT INTO ledger (account, change) VALUES ('potion_capacity', :change)"
    ).bindparams(change=change)

    with db.engine.begin() as connection:
        connection.execute(ledger_potion_capacity_entry)


def account_amount(account: str) -> int:

    ledger = sqlalchemy.text(
        "SELECT sum(change) FROM ledger WHERE account = :account"
    ).bindparams(account=account)

    with db.engine.begin() as connection:
        result = connection.execute(ledger).mappings().first()

    return result["sum"]
