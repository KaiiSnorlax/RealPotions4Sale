import sqlalchemy
from src import database as db
from src.api.bottler import PotionDelivered, PotionRecipe
from src.api.barrels import Barrel
from utils import barrels_util, potions_util



colors = ["red_ml", "green_ml", "blue_ml", "dark_ml"]


def potion_sold(cart_id: int):

    get_transaction_info = sqlalchemy.text(
        "select customers.name, cart_items.sku, cart_items.quantity, potion_recipes.price from customer_visits join carts on customer_visits.visit_id = carts.visit_id join customers on customers.customer_id = customer_visits.customer_id join cart_items on carts.cart_id = cart_items.cart_id join potion_recipes on cart_items.sku = potion_recipes.sku;"
    )

    with db.engine.begin() as connection:
        transaction = connection.execute(get_transaction_info).mappings().all()

    for entry in range(len(transaction)):
        description = (
            f"Potion Sold: {transaction[entry]["name"]} purchased {transaction[entry]["sku"]} (x{transaction[entry]["quantity"]}) for {transaction[entry]["price"]} gold each."
        )  
        transaction_entry = sqlalchemy.text(
            "INSERT INTO transactions (description) VALUES (:description)"
        ).bindparams(description=description)

        with db.engine.begin() as connection:
            connection.execute(transaction_entry)

        gold_total = transaction[entry]["quantity"] * transaction[entry]["price"]
        gold_ledger_entry(gold_total)
        potion_ledger_entry(transaction[entry]["sku"], -transaction[entry]["quantity"])



def potion_delivered(potion: PotionDelivered):

    description = (
        f"Potion Delivered: {potion.potion_type.sku} (x{potion.quantity})")

    transaction_entry = sqlalchemy.text(
        "INSERT INTO transactions (description) VALUES (:description)"
    ).bindparams(description=description)

    with db.engine.begin() as connection:
        connection.execute(transaction_entry)

    potion_ledger_entry(potion.potion_type.sku, potion.quantity)

    for color in colors:
        if getattr(potion.potion_type, color) != 0:
            liquid_ledger_entry(color, -(getattr(potion.potion_type, color) * potion.quantity))


def potion_ledger_entry(sku: str, change: int):
    ledger_potion_entry = sqlalchemy.text(
        "INSERT INTO potion_ledger (transaction_id, sku, change) SELECT max(transaction_id), :sku, :change FROM transactions"
    ).bindparams(sku=sku, change=change)

    with db.engine.begin() as connection:
        connection.execute(ledger_potion_entry)


def barrel_bought(barrel: Barrel):
    color = barrels_util.get_barrel_type(barrel.potion_type)
    description = f"Barrel Purchased: Purchased {color} (x{barrel.quantity}) for {barrel.ml_per_barrel} each"

    transaction_entry = sqlalchemy.text(
        "INSERT INTO transactions (description) VALUES (:description)"
    ).bindparams(description=description)

    with db.engine.begin() as connection:
        connection.execute(transaction_entry)

    liquid_ledger_entry(color, (barrel.ml_per_barrel * barrel.quantity))
    gold_ledger_entry(-(barrel.price * barrel.quantity))


def gold_ledger_entry(change: int):

    ledger_gold_entry = sqlalchemy.text(
        "INSERT INTO gold_ledger (transaction_id, change) SELECT max(transaction_id), :change FROM transactions"
    ).bindparams(change=change)

    with db.engine.begin() as connection:
        connection.execute(ledger_gold_entry)


def liquid_ledger_entry(color: str, change: int):
    ledger_potion_entry = sqlalchemy.text(
        "INSERT INTO liquid_ledger (transaction_id, color, change) SELECT max(transaction_id), :color, :change FROM transactions"
    ).bindparams(color=color, change=change)

    with db.engine.begin() as connection:
        connection.execute(ledger_potion_entry)


def potion_capacity_ledger_entry(color: str, change: int):
    ledger_potion_entry = sqlalchemy.text(
        "INSERT INTO capacity_ledger (transaction_id, type, change) SELECT max(transaction_id), 'potion', 50 FROM transactions"
    )

    with db.engine.begin() as connection:
        connection.execute(ledger_potion_entry)


def liquid_capacity_ledger_entry(color: str, change: int):
    ledger_potion_entry = sqlalchemy.text(
        "INSERT INTO capacity_ledger (transaction_id, type, change) SELECT max(transaction_id), 'liquid', 10000 FROM transactions"
    )

    with db.engine.begin() as connection:
        connection.execute(ledger_potion_entry)





def liquid_ledger_sum(color: str) -> int:

    ledger = sqlalchemy.text(
        "SELECT sum(change) FROM liquid_ledger WHERE color = :color"
    ).bindparams(color=color)

    with db.engine.begin() as connection:
        result = connection.execute(ledger).mappings().first()

    return result["sum"]


def potion_ledger_sum(sku: str) -> int:

    ledger = sqlalchemy.text(
        "SELECT sum(change) FROM potion_ledger WHERE sku = :sku"
    ).bindparams(sku=sku)

    with db.engine.begin() as connection:
        result = connection.execute(ledger).mappings().first()

    return result["sum"]

def all_potions_sum() -> int:

    ledger = sqlalchemy.text(
        "SELECT sum(change) FROM potion_ledger"
    )

    with db.engine.begin() as connection:
        result = connection.execute(ledger).mappings().first()

    return result["sum"]
    

def gold_ledger_sum() -> int:

    ledger = sqlalchemy.text("SELECT sum(change) FROM gold_ledger")

    with db.engine.begin() as connection:
        result = connection.execute(ledger).mappings().first()

    return result["sum"]


def liquid_capacity_sum() -> int:

    ledger = sqlalchemy.text("SELECT sum(change) FROM capacity_ledger WHERE type = 'liquid'")

    with db.engine.begin() as connection:
        result = connection.execute(ledger).mappings().first()

    return result["sum"]

def potion_capacity_sum() -> int:

    ledger = sqlalchemy.text("SELECT sum(change) FROM capacity_ledger WHERE type = 'potion'")

    with db.engine.begin() as connection:
        result = connection.execute(ledger).mappings().first()

    return result["sum"]
