from fastapi import APIRouter, Depends
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)


@router.post("/reset")
def reset():

    # Reset the game state. Gold goes to 100, all potions are removed from
    # inventory, and all barrels are removed from inventory. Carts are all reset.

    delete_potion_ledger_entries = sqlalchemy.text(
        "TRUNCATE table potion_ledger CASCADE"
    )

    delete_gold_ledger_entries = sqlalchemy.text("TRUNCATE table gold_ledger CASCADE")
    delete_liquid_ledger_entries = sqlalchemy.text(
        "TRUNCATE table liquid_ledger CASCADE"
    )

    delete_transactions = sqlalchemy.text("TRUNCATE table transactions CASCADE")
    reset_ledger_sequence = sqlalchemy.text(
        "ALTER SEQUENCE transactions_transaction_id_seq RESTART WITH 1"
    )

    add_starting_transactions = sqlalchemy.text(
        "INSERT INTO transactions (description) VALUES ('Shop Reset: starting gold 100'), ('Shop Reset: starting liquid capacity 10000'), ('Shop Reset: starting potion capacity 50')"
    )

    add_starting_gold = sqlalchemy.text(
        "INSERT INTO gold_ledger (transaction_id, change) VALUES (1, 100)"
    )

    add_starting_capacity = sqlalchemy.text(
        "INSERT INTO capacity_ledger (transaction_id, type, change) VALUES (2, 'liquid', 10000), (3, 'potion', 50)"
    )

    with db.engine.begin() as connection:
        connection.execute(delete_transactions)
        connection.execute(delete_potion_ledger_entries)
        connection.execute(delete_gold_ledger_entries)
        connection.execute(delete_liquid_ledger_entries)
        connection.execute(reset_ledger_sequence)
        connection.execute(add_starting_transactions)
        connection.execute(add_starting_gold)
        connection.execute(add_starting_capacity)

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
        "ALTER SEQUENCE customers_customer_id_seq RESTART WITH 1"
    )

    with db.engine.begin() as connection:
        connection.execute(delete_cart_items)
        connection.execute(delete_carts)
        connection.execute(reset_cart_sequence)
        connection.execute(delete_customer_visits)
        connection.execute(reset_customer_visits_sequence)
        connection.execute(delete_customers)
        connection.execute(reset_customers_sequence)

    print("Reset: ledgers, carts, and customers reset")

    return "OK"
