import sqlalchemy
from src import database as db
from src.utils import ledger


def create_new_cart(customer_name: str, customer_class: str, customer_level: int) -> int | None:

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
           ON CONFLICT DO NOTHING
           RETURNING cart_id"""
    ).bindparams(
        customer_name=customer_name,
        customer_class=customer_class,
        customer_level=customer_level,
    )

    with db.engine.begin() as connection:
        create_cart = connection.execute(cart).first()

    if create_cart is None:
        raise RuntimeError(f"Failed to create a cart for {customer_name, customer_class, customer_level}")
    
    cart_id = create_cart[0]
    
    return cart_id


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


def cart_checkout(cart_id: int) -> int:
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

    return cart_total
