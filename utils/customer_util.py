from pydantic import BaseModel
import sqlalchemy
from src import database as db
from src.api import info


class Customer(BaseModel):
    customer_name: str
    character_class: str
    level: int


def add_new_customer(customer: Customer):

    customer_entry = sqlalchemy.text(
        "INSERT INTO customers (name, class, level) VALUES (:customer_name, :customer_class, :customer_level) ON CONFLICT DO NOTHING"
    ).bindparams(
        customer_name=customer.customer_name,
        customer_class=customer.character_class,
        customer_level=customer.level,
    )

    visit_entry = sqlalchemy.text(
        "INSERT INTO customer_visits (customer_id, hour, day) SELECT customer_id, :hour, :day FROM customers WHERE customers.name = :customer_name AND customers.class = :customer_class AND customers.level = :customer_level;"
    ).bindparams(
        customer_name=customer.customer_name,
        customer_class=customer.character_class,
        customer_level=customer.level,
        hour=info.time.hour,
        day=info.time.day,
    )

    with db.engine.begin() as connection:
        connection.execute(customer_entry)
        connection.execute(visit_entry)
