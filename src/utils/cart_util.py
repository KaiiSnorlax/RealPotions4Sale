import sqlalchemy
from src import database as db


def create_new_cart(
    customer_name: str, customer_class: str, customer_level: int
) -> int | None:

    # Creates a new cart
    cart = sqlalchemy.text(
        """INSERT INTO
            cart (visit_id)
           SELECT
            max(visit.id)
           FROM
            visit
            JOIN customer ON visit.customer_id = customer.id
           WHERE customer.name = :customer_name
            AND customer.class = :customer_class
            AND customer.level = :customer_level
           ON CONFLICT DO NOTHING
           RETURNING id"""
    ).bindparams(
        customer_name=customer_name,
        customer_class=customer_class,
        customer_level=customer_level,
    )

    with db.engine.begin() as connection:
        create_cart = connection.execute(cart).first()

    if create_cart is None:
        raise RuntimeError(
            f"Failed to create a cart for {customer_name, customer_class, customer_level}"
        )

    cart_id = create_cart[0]

    return cart_id


def add_item_to_cart(cart_id: int, potion_id: int, quantity: int):

    add_to_cart_query = sqlalchemy.text(
        """INSERT INTO
            cart_item (cart_id, potion_id, quantity)
           VALUES
            (:cart_id, :item_sku, :item_quantity)"""
    ).bindparams(item_sku=potion_id, item_quantity=quantity, cart_id=cart_id)

    with db.engine.begin() as connection:
        connection.execute(add_to_cart_query)

    return
