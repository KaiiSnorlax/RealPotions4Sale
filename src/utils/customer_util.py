import sqlalchemy
from src import database as db
from src.api import info


def add_new_customer(json_string: str, visit_id: int) -> None:

    # Adds a new customer if the combination of name, class and level are unique
    # Adds a new visit for said customer if visit_id is unique
    customer_entry = sqlalchemy.text(
        """
        DO $insert_customers$
        DECLARE
            customer_visit_details RECORD;
            current_customer_id INTEGER;
        BEGIN
        FOR customer_visit_details IN
        select * from json_populate_recordset(null::record,:json_string)
        AS
        (
        customer_name text,
        character_class text,
        customer_level integer
        )
        LOOP
            INSERT INTO customer (name, class, level)
            VALUES (customer_visit_details.customer_name, customer_visit_details.character_class, customer_visit_details.customer_level)
            ON CONFLICT (name, class, level) DO NOTHING;

            SELECT id
            INTO current_customer_id
            FROM customer
            WHERE name=customer_visit_details.customer_name and class=customer_visit_details.character_class and level=customer_visit_details.customer_level;

            INSERT INTO visit (customer_id, hour, day, external_visit_id)
            VALUES (current_customer_id, :hour, :day, :visit_id)
            ON CONFLICT DO NOTHING;
        END LOOP;
        END $insert_customers$;
        """
    ).bindparams(
        json_string=json_string,
        visit_id=visit_id,
        hour=info.time.hour,
        day=info.time.day,
    )

    with db.engine.begin() as connection:
        connection.execute(customer_entry)
