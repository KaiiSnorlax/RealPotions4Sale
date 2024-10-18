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
                    sku=row[1],
                    name=row[2],
                    price=row[3],
                    potion_type=(row[4], row[5], row[6], row[7]),
                    quantity=row[8],
                )
            )

    return potion_catalog
