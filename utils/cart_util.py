from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from utils import ledger


def create_new_cart(customer_name):
    get_visit_id = sqlalchemy.text(
        "SELECT MAX(visit_id) FROM customers JOIN customer_visits ON customers.customer_id = customer_visits.customer_id WHERE (customers.customer_name = :customer_name)"
    ).bindparams(customer_name=customer_name)

    get_cart_id = sqlalchemy.text(
        "SELECT max(cart_id) FROM customer_visits JOIN carts ON customer_visits.visit_id = carts.visit_id JOIN customers ON customers.customer_id = customer_visits.customer_id WHERE customer_name = :customer_name"
    ).bindparams(customer_name=customer_name)

    with db.engine.begin() as connection:
        visit_id = connection.execute(get_visit_id).mappings().first()
        connection.execute(
            sqlalchemy.text(
                "INSERT INTO carts (visit_id) VALUES (:current_visit)"
            ).bindparams(current_visit=visit_id["max"])
        )
        visit_id = connection.execute(get_cart_id).mappings().first()
        connection.execute(get_cart_id).mappings().first()

    return visit_id["max"]


def add_item_to_cart(cart_id, item_sku, item_quantity):
    """"""
    add_to_cart = sqlalchemy.text(
        "INSERT INTO cart_items (cart_id, sku, quantity) VALUES (:cart_id, :item_sku, :item_quantity)"
    ).bindparams(item_sku=item_sku, item_quantity=item_quantity, cart_id=cart_id)
    with db.engine.begin() as connection:
        connection.execute(add_to_cart)

    return


def cart_checkout(cart_id):
    cart_total = 0
    cart_items = sqlalchemy.text(
        "SELECT cart_items.sku, quantity, price FROM cart_items JOIN potions ON cart_items.sku = potions.sku WHERE cart_id = :cart_id"
    ).bindparams(cart_id=cart_id)

    with db.engine.begin() as connection:
        potions_sold = connection.execute(cart_items).mappings().all()

        for potion in potions_sold:
            ledger.potion_entry(potion["sku"], -potion["quantity"])
            ledger.gold_entry((potion["price"] * potion["quantity"]))

    print(cart_total)
