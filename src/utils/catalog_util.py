from pydantic import BaseModel
import sqlalchemy
from src import database as db


class Catalog(BaseModel):
    sku: str
    name: str
    quantity: int
    price: int
    potion_type: tuple[int, int, int, int]


def get_catalog() -> list[Catalog]:
    potion_catalog: list[Catalog] = []

    # Gets all potions that a. I want to sell (catalog = true), and b. are stocked
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT distinct
                    potion.id, potion.sku, potion.name, potion.price, potion.red_ml, potion.green_ml, potion.blue_ml, potion.dark_ml, coalesce(sum(change), 0) as stock 
                FROM
                    potion
                LEFT JOIN potion_ledger ON potion_ledger.potion_id = potion.id
                WHERE
                    potion.catalog = true
                GROUP BY
                    potion.id
                HAVING
                    coalesce(sum(change), 0) != 0
                ORDER BY
                    coalesce(sum(change), 0)
                """
            )
        )
        for row in result:
            potion_catalog.append(
                Catalog(
                    sku=row[0],
                    name=row[1],
                    price=row[2],
                    potion_type=(row[3], row[4], row[5], row[6]),
                    quantity=row[7],
                )
            )

    return potion_catalog
