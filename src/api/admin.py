from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from utils import ledger

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

    delete_carts = sqlalchemy.text("TRUNCATE table carts CASCADE")
    reset_cart_sequence = sqlalchemy.text(
        "ALTER SEQUENCE carts_cart_id_seq RESTART WITH 1"
    )

    delete_cart_items = sqlalchemy.text("TRUNCATE table cart_items CASCADE")

    delete_customer_visits = sqlalchemy.text("TRUNCATE table customer_visits CASCADE")
    reset_customer_visits_sequence = sqlalchemy.text(
        "ALTER SEQUENCE customer_visits_visit_id_seq RESTART WITH 1"
    )

    delete_customers = sqlalchemy.text("TRUNCATE table customers CASCADE")
    reset_customers_sequence = sqlalchemy.text(
        "ALTER SEQUENCE customers_id_seq RESTART WITH 1"
    )

    with db.engine.begin() as connection:
        connection.execute(delete_ledger_entries)
        connection.execute(reset_ledger_sequence)
        connection.execute(add_default_gold)
        connection.execute(add_default_potion_capacity)
        connection.execute(add_default_ml_capacity)
        connection.execute(add_potion_types)
        connection.execute(add_ml_types)
        connection.execute(delete_cart_items)
        connection.execute(delete_carts)
        connection.execute(reset_cart_sequence)
        connection.execute(delete_customer_visits)
        connection.execute(reset_customer_visits_sequence)
        connection.execute(delete_customers)
        connection.execute(reset_customers_sequence)

    print("ledger, carts, and customers reset")

    return "OK"
