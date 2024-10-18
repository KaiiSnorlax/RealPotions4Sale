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
    # inventory, and all barrels are removed from inventory. cart are all reset.

    delete_potion_ledger_entries = sqlalchemy.text(
        "TRUNCATE table potion_ledger CASCADE"
    )
    reset_potion_ledger_sequence = sqlalchemy.text(
        "ALTER SEQUENCE potion_ledger_id_seq RESTART WITH 1"
    )

    delete_gold_ledger_entries = sqlalchemy.text("TRUNCATE table gold_ledger CASCADE")
    reset_gold_ledger_sequence = sqlalchemy.text(
        "ALTER SEQUENCE gold_ledger_id_seq RESTART WITH 1"
    )

    delete_liquid_ledger_entries = sqlalchemy.text(
        "TRUNCATE table liquid_ledger CASCADE"
    )
    reset_liquid_ledger_sequence = sqlalchemy.text(
        "ALTER SEQUENCE liquid_ledger_id_seq RESTART WITH 1"
    )

    delete_capacity_ledger_entries = sqlalchemy.text(
        "TRUNCATE table capacity_ledger CASCADE"
    )
    reset_capacity_ledger_sequence = sqlalchemy.text(
        "ALTER SEQUENCE capacity_ledger_id_seq RESTART WITH 1"
    )

    delete_transaction = sqlalchemy.text("TRUNCATE table transaction CASCADE")
    reset_ledger_sequence = sqlalchemy.text(
        "ALTER SEQUENCE transaction_id_seq RESTART WITH 1"
    )

    add_starting_transaction = sqlalchemy.text(
        "INSERT INTO transaction (description) VALUES ('Shop Reset: starting gold 100'), ('Shop Reset: starting liquid capacity 10000'), ('Shop Reset: starting potion capacity 50')"
    )

    add_starting_gold = sqlalchemy.text(
        "INSERT INTO gold_ledger (transaction_id, change) VALUES (1, 100)"
    )

    add_starting_capacity = sqlalchemy.text(
        "INSERT INTO capacity_ledger (transaction_id, type, change) VALUES (2, 'liquid', 10000), (3, 'potion', 50)"
    )

    with db.engine.begin() as connection:
        connection.execute(delete_transaction)
        connection.execute(delete_potion_ledger_entries)
        connection.execute(reset_potion_ledger_sequence)
        connection.execute(delete_gold_ledger_entries)
        connection.execute(reset_gold_ledger_sequence)
        connection.execute(delete_liquid_ledger_entries)
        connection.execute(reset_liquid_ledger_sequence)
        connection.execute(reset_ledger_sequence)
        connection.execute(delete_capacity_ledger_entries)
        connection.execute(reset_capacity_ledger_sequence)
        connection.execute(add_starting_transaction)
        connection.execute(add_starting_gold)
        connection.execute(add_starting_capacity)

    delete_cart = sqlalchemy.text("TRUNCATE table cart CASCADE")
    reset_cart_sequence = sqlalchemy.text("ALTER SEQUENCE cart_id_seq RESTART WITH 1")

    delete_cart_item = sqlalchemy.text("TRUNCATE table cart_item CASCADE")

    delete_customer_visits = sqlalchemy.text("TRUNCATE table visit CASCADE")
    reset_customer_visits_sequence = sqlalchemy.text(
        "ALTER SEQUENCE visit_id_seq RESTART WITH 1"
    )

    delete_customers = sqlalchemy.text("TRUNCATE table customer CASCADE")
    reset_customers_sequence = sqlalchemy.text(
        "ALTER SEQUENCE customer_id_seq RESTART WITH 1"
    )

    delete_checkout = sqlalchemy.text("TRUNCATE table checkout CASCADE")

    with db.engine.begin() as connection:
        connection.execute(delete_cart_item)
        connection.execute(delete_cart)
        connection.execute(reset_cart_sequence)
        connection.execute(delete_customer_visits)
        connection.execute(reset_customer_visits_sequence)
        connection.execute(delete_customers)
        connection.execute(reset_customers_sequence)
        connection.execute(delete_checkout)

    print("Reset: ledgers, cart, and customers reset")

    return "OK"
