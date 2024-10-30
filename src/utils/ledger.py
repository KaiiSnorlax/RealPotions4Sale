import sqlalchemy
from src import database as db


def potion_sold(cart_id: int) -> tuple[int, int]:
    # This transaction stores details of the cart owner / cart items and temporaily (for transaction) stores this information inside of line_item_details
    # For each potion sold (row in line_item_details) a transaction description is created and associated transaction_id is saved into temporary variable line_item_transaction_id
    # Using line_item_transaction_id potion ledger records the decrease in stock, while gold ledger records the increase in gold
    # Also using line_item_transaction_id, a row is inserted into checkout, which is a join table between cart_item and transaction (for ease of data analysis)

    cart_checkout = sqlalchemy.text(
        """
        DO $$
        DECLARE
            line_item_details RECORD;
            line_item_transaction_id INTEGER;
        BEGIN
        FOR line_item_details IN
            SELECT
                customer.name, customer.level, customer.class, 
                potion.name as potion_name, potion.price,
                cart_item.quantity, cart_item.potion_id, cart_item.id as cart_id
            FROM
                visit
                JOIN cart ON visit.id = cart.visit_id
                JOIN customer ON customer.id = visit.customer_id
                JOIN cart_item ON cart.id = cart_item.cart_id
                JOIN potion ON cart_item.potion_id = potion.id
            WHERE cart.id = :cart_id
        LOOP
            INSERT INTO transaction (description)
            VALUES (
            CONCAT(
                'Potion Sold: ', line_item_details.name, 
                ' (level ', line_item_details.level, ', class ', line_item_details.class, 
                ') purchased ', line_item_details.potion_name, 
                ' (x', line_item_details.quantity, 
                ') for ', line_item_details.price, ' gold each.')
            )
            RETURNING id INTO line_item_transaction_id;

            INSERT INTO potion_ledger (transaction_id, potion_id, change)
            VALUES (line_item_transaction_id, line_item_details.potion_id, -line_item_details.quantity);

            INSERT INTO gold_ledger (transaction_id, change)
            VALUES (line_item_transaction_id, (line_item_details.quantity * line_item_details.price));

            INSERT INTO checkout (transaction_id, cart_item_id)
            VALUES (line_item_transaction_id, line_item_details.cart_id);
        END LOOP;
        END $$;

        SELECT 
            SUM(cart_item.quantity) as total_bought, SUM(cart_item.quantity * potion.price) as total_price
        FROM
            cart_item
            JOIN potion ON potion.id = cart_item.potion_id
        WHERE cart_item.cart_id = :cart_id;
        """
    ).bindparams(cart_id=cart_id)

    with db.engine.begin() as connection:
        result = connection.execute(cart_checkout).mappings().first()

    if result is None:
        raise RuntimeError(f"error with cart {cart_id}")

    return (result["total_bought"], result["total_price"])


def potion_delivered(json_string: str):
    # This transaction takes in a json array and converts it into a set of records, each representing a delivered potion. (Do this since details of our order are not in database)
    # For each potion delivered (row in order_details) a transaction description is created and associated transaction_id is saved into temporary variable potion_transaction_id
    # Using potion_transaction_id potion ledger records the increase in stock
    # Also using potion_transaction_id liquid ledger records the decrease in stock (IF statements there to avoid useless entries where there is 0 change)

    potions_delivered = sqlalchemy.text(
        """
        DO $potions_delivered$
        DECLARE
            order_details RECORD;
            potion_transaction_id INTEGER;
        BEGIN
        FOR order_details IN
        select * from json_populate_recordset(null::record,:json_string)
        AS
        (
        sku text,
        potion_id integer,
        quantity integer,
        red_ml_cost integer,
        green_ml_cost integer,
        blue_ml_cost integer,
        dark_ml_cost integer
        )
        LOOP
            INSERT INTO transaction (description)
            VALUES (
            CONCAT(
            'Potion Delivered: ', order_details.sku, ' (x', order_details.quantity, ')')
            )
            RETURNING id INTO potion_transaction_id;

            INSERT INTO potion_ledger (transaction_id, potion_id, change)
            VALUES (potion_transaction_id, order_details.potion_id, order_details.quantity);

            IF order_details.red_ml_cost * order_details.quantity <> 0 THEN
                INSERT INTO liquid_ledger (transaction_id, color, change)
                VALUES (potion_transaction_id, 'red_ml', -(order_details.red_ml_cost * order_details.quantity));
            END IF;

            IF order_details.green_ml_cost * order_details.quantity <> 0 THEN
                INSERT INTO liquid_ledger (transaction_id, color, change)
                VALUES (potion_transaction_id, 'green_ml', -(order_details.green_ml_cost * order_details.quantity));
            END IF;

            IF order_details.blue_ml_cost * order_details.quantity <> 0 THEN
                INSERT INTO liquid_ledger (transaction_id, color, change)
                VALUES (potion_transaction_id, 'blue_ml', -(order_details.blue_ml_cost * order_details.quantity));
            END IF;

            IF order_details.dark_ml_cost * order_details.quantity <> 0 THEN
                INSERT INTO liquid_ledger (transaction_id, color, change)
                VALUES (potion_transaction_id, 'dark_ml', -(order_details.dark_ml_cost * order_details.quantity));
            END IF;
        END LOOP;
        END $potions_delivered$;
        """
    ).bindparams(json_string=json_string)

    with db.engine.begin() as connection:
        connection.execute(potions_delivered)


def potion_ledger_entry(sku: str, change: int):
    ledger_potion_entry = sqlalchemy.text(
        """INSERT INTO
            potion_ledger (transaction_id, sku, change)
           SELECT
            max(transaction_id), :sku, :change
           FROM
            transaction"""
    ).bindparams(sku=sku, change=change)

    with db.engine.begin() as connection:
        connection.execute(ledger_potion_entry)


def barrel_bought(json_string: str):
    # This transaction takes in a json array and converts it into a set of records, each representing a delivered barrel. (Do this since details of our order are not in database)
    # For each barrel delivered (row in order_details) a transaction description is created and associated transaction_id is saved into temporary variable potion_transaction_id
    # Using barrel_transaction_id liquid ledger records the increase in stock, while gold ledger records the decrease in gold

    barrels_bought = sqlalchemy.text(
        """
        DO $barrels_delivered$
        DECLARE
            order_details RECORD;
            barrel_transaction_id INTEGER;
        BEGIN
        FOR order_details IN
        select * from json_populate_recordset(null::record,:json_string)
        AS
        (
        color text,
        quantity integer,
        ml_per_barrel integer,
        price integer
        )
        LOOP
            INSERT INTO transaction (description)
            VALUES (
            CONCAT(
            'Barrel Purchased: ', order_details.color, ' (x ', order_details.quantity, '); containing ', order_details.ml_per_barrel, 'ml; costing ', order_details.price, ' gold each.')
            )
            RETURNING id INTO barrel_transaction_id;

            INSERT INTO liquid_ledger (transaction_id, change, color)
            VALUES (barrel_transaction_id, order_details.ml_per_barrel, order_details.color);

            INSERT INTO gold_ledger (transaction_id, change)
            VALUES (barrel_transaction_id, -(order_details.quantity * order_details.price));

        END LOOP;
        END $barrels_delivered$;
        """
    ).bindparams(json_string=json_string)

    with db.engine.begin() as connection:
        connection.execute(barrels_bought)


def capacity_upgrade(liquid_upgrade: int, potion_upgrade: int):
    liquid_upgrade_transaction = sqlalchemy.text(
        """
        INSERT INTO transaction (description)
        VALUES ('Liquid Capacity Upgrade: + :l_upgrade ml space')
        RETURNING id
        """
    ).bindparams(l_upgrade=liquid_upgrade * 10000)

    potion_upgrade_transaction = sqlalchemy.text(
        """
        INSERT INTO transaction (description)
        VALUES ('Potion Capacity Upgrade: + :p_upgrade potion slots')
        RETURNING id
        """
    ).bindparams(p_upgrade=potion_upgrade * 50)

    liquid_upgrade_entry = sqlalchemy.text(
        """
        INSERT INTO capacity_ledger (transaction_id, type, change)
        VALUES (:t_id, 'liquid', :capacity_change);

        INSERT INTO gold_ledger (transaction_id, change)
        VALUES (:t_id, :gold_change);
        """
    )

    potion_upgrade_entry = sqlalchemy.text(
        """
        INSERT INTO capacity_ledger (transaction_id, type, change)
        VALUES (:t_id, 'potion', :capacity_change);

        INSERT INTO gold_ledger (transaction_id, change)
        VALUES (:t_id, :gold_change);
        """
    )

    if liquid_upgrade > 0:
        with db.engine.begin() as connection:
            transaction_id = connection.execute(liquid_upgrade_transaction).scalar_one()
            connection.execute(
                liquid_upgrade_entry.bindparams(
                    t_id=transaction_id, capacity_change=liquid_upgrade * 10000, gold_change=-liquid_upgrade * 1000
                )
            )

    if potion_upgrade > 0:
        with db.engine.begin() as connection:
            transaction_id = connection.execute(potion_upgrade_transaction).scalar_one()
            connection.execute(
                potion_upgrade_entry.bindparams(
                    t_id=transaction_id, capacity_change=potion_upgrade * 50, gold_change=-potion_upgrade * 1000
                )
            )
    return


def liquid_ledger_sum(color: str) -> int:

    ledger = sqlalchemy.text(
        """SELECT
            COALESCE(sum(change), 0)
           FROM
            liquid_ledger
           WHERE
            color = :color"""
    ).bindparams(color=color)

    with db.engine.begin() as connection:
        result = connection.execute(ledger).first()

    if result is None:
        raise RuntimeError(f"Failed to sum {color} in table: liquid_ledger")

    return result[0]


def potion_ledger_sum(sku: str) -> int:

    ledger = sqlalchemy.text(
        """SELECT
            COALESCE(sum(change), 0)
           FROM
            potion_ledger
           WHERE
            sku = :sku"""
    ).bindparams(sku=sku)

    with db.engine.begin() as connection:
        result = connection.execute(ledger).first()

    if result is None:
        raise RuntimeError(f"Failed to sum {sku} in table: potion_ledger")

    return result[0]


def all_potions_sum() -> int:

    ledger = sqlalchemy.text(
        """SELECT
            COALESCE(sum(change), 0)
           FROM
            potion_ledger"""
    )

    with db.engine.begin() as connection:
        result = connection.execute(ledger).first()

    if result is None:
        raise RuntimeError("Failed to sum all types of potions in table: potion_ledger")

    return result[0]


def all_liquid_sum() -> int:

    ledger = sqlalchemy.text(
        """SELECT
            COALESCE(sum(change), 0)
           FROM
            liquid_ledger"""
    )

    with db.engine.begin() as connection:
        result = connection.execute(ledger).first()

    if result is None:
        raise RuntimeError("Failed to sum all types of liquid in table: liquid_ledger")

    return result[0]


def gold_ledger_sum() -> int:

    ledger = sqlalchemy.text(
        """SELECT
            COALESCE(sum(change), 0)
           FROM
            gold_ledger"""
    )

    with db.engine.begin() as connection:
        result = connection.execute(ledger).first()

    if result is None:
        raise RuntimeError("Failed to sum gold in table: gold_ledger")

    return result[0]


def liquid_capacity_sum() -> int:

    ledger = sqlalchemy.text(
        """SELECT
            COALESCE(sum(change), 0)
           FROM
            capacity_ledger
           WHERE
            type = 'liquid'"""
    )

    with db.engine.begin() as connection:
        result = connection.execute(ledger).first()

    if result is None:
        raise RuntimeError("Failed to sum gold in table: gold_ledger")

    return result[0]


def potion_capacity_sum() -> int:

    ledger = sqlalchemy.text(
        """SELECT
            COALESCE(sum(change), 0)
           FROM
            capacity_ledger
           WHERE
            type = 'potion'"""
    )

    with db.engine.begin() as connection:
        result = connection.execute(ledger).first()

    if result is None:
        raise RuntimeError("Failed to sum potion capacity in table: capacity_ledger")

    return result[0]
