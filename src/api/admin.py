from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
<<<<<<< Updated upstream
=======
import sqlalchemy
from src import database as db
from utils import ledger
>>>>>>> Stashed changes

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)


@router.post("/reset")
def reset():
    """
    Reset the game state. Gold goes to 100, all potions are removed from
    inventory, and all barrels are removed from inventory. Carts are all reset.
    """
<<<<<<< Updated upstream
=======

    delete_ledger_entries = sqlalchemy.text("TRUNCATE table ledger")
    reset_ledger_sequence = sqlalchemy.text(
        "ALTER SEQUENCE ledger_entry_seq RESTART WITH 1"
    )
    add_default_gold = sqlalchemy.text(
        "INSERT INTO ledger (account, change) VALUES ('gold', 100)"
    )
    add_default_potion_capacity = sqlalchemy.text(
        "INSERT INTO ledger (account, change) VALUES ('potion_capacity', 50)"
    )
    add_default_ml_capacity = sqlalchemy.text(
        "INSERT INTO ledger (account, change) VALUES ('ml_capacity', 10000)"
    )
    add_potion_types = sqlalchemy.text(
        "INSERT INTO ledger (account, change) VALUES ('green_potion', 0), ('red_potion', 0)"
    )
    add_ml_types = sqlalchemy.text(
        "INSERT INTO ledger (account, change) VALUES ('red_ml', 0), ('green_ml', 0), ('blue_ml', 0), ('dark_ml', 0)"
    )

    with db.engine.begin() as connection:
        connection.execute(delete_ledger_entries)
        connection.execute(reset_ledger_sequence)
        connection.execute(add_default_gold)
        connection.execute(add_default_potion_capacity)
        connection.execute(add_default_ml_capacity)
        connection.execute(add_potion_types)
        connection.execute(add_ml_types)

    print("ledger reset")

>>>>>>> Stashed changes
    return "OK"
