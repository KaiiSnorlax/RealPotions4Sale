import sqlalchemy
from src import database as db
from src.utils import ledger


def create_new_cart(customer_name: str, customer_class: str, customer_level: int):

    cart = sqlalchemy.text(
        """INSERT INTO
            carts (visit_id)
           SELECT
            max(customer_visits.visit_id)
           FROM
            customer_visits
            JOIN customers ON customer_visits.customer_id = customers.customer_id
           WHERE customers.name = :customer_name
            AND customers.class = :customer_class
            AND customers.level = :customer_level
           ON CONFLICT DO NOTHING"""
    ).bindparams(
        customer_name=customer_name,
        customer_class=customer_class,
        customer_level=customer_level,
    )

    with db.engine.begin() as connection:
        connection.execute(cart)


def get_cart_id(customer_name: str, customer_class: str, customer_level: int):

    cart_id_query = sqlalchemy.text(
        """SELECT
            max(cart_id)
           FROM
            customer_visits
            JOIN carts ON customer_visits.visit_id = carts.visit_id
            JOIN customers ON customers.customer_id = customer_visits.customer_id
           WHERE customers.name = :customer_name
            AND customers.class = :customer_class
            AND customers.level = :customer_level"""
    ).bindparams(
        customer_name=customer_name,
        customer_class=customer_class,
        customer_level=customer_level,
    )

    with db.engine.begin() as connection:
        cart_id = connection.execute(cart_id_query).first()

    if cart_id is None:
        raise RuntimeError(
            f"({customer_name}, {customer_class}, {customer_level}) has not made a cart in table: carts"
        )

    return cart_id[0]


def add_item_to_cart(cart_id: int, item_sku: str, quantity: int):

    add_to_cart_query = sqlalchemy.text(
        """INSERT INTO
            cart_items (cart_id, sku, quantity)
           VALUES
            (:cart_id, :item_sku, :item_quantity)"""
    ).bindparams(item_sku=item_sku, item_quantity=quantity, cart_id=cart_id)

    with db.engine.begin() as connection:
        connection.execute(add_to_cart_query)

    return


def cart_checkout(cart_id: int):
    cart_total = 0
    cart_items = sqlalchemy.text(
        """SELECT
            cart_items.sku, quantity, price
           FROM
            cart_items
            JOIN potions ON cart_items.sku = potions.sku
           WHERE cart_id = :cart_id"""
    ).bindparams(cart_id=cart_id)

    with db.engine.begin() as connection:
        potions_sold = connection.execute(cart_items).mappings().all()

        for potion in potions_sold:
            ledger.potion_ledger_entry(potion["sku"], -potion["quantity"])
            ledger.gold_ledger_entry((potion["price"] * potion["quantity"]))

    print(cart_total)
