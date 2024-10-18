import sqlalchemy
from src import database as db
from src.api import info


def add_new_customer(
    customer_name: str, customer_class: str, customer_level: int
) -> None:

    # Adds a new customer if the combination of name, class and level are unique
    customer_entry = sqlalchemy.text(
        """INSERT INTO
            customer (name, class, level)
           VALUES
            (:customer_name, :customer_class, :customer_level)
           ON CONFLICT DO NOTHING"""
    ).bindparams(
        customer_name=customer_name,
        customer_class=customer_class,
        customer_level=customer_level,
    )

    # Adds a new visit for each customer
    visit_entry = sqlalchemy.text(
        """INSERT INTO
            visit (customer_id, hour, day)
           SELECT
            customer.id, :hour, :day
           FROM
            customer
           WHERE customer.name = :customer_name
           AND customer.class = :customer_class
           AND customer.level = :customer_level"""
    ).bindparams(
        customer_name=customer_name,
        customer_class=customer_class,
        customer_level=customer_level,
        hour=info.time.hour,
        day=info.time.day,
    )

    with db.engine.begin() as connection:
        connection.execute(customer_entry)
        connection.execute(visit_entry)
