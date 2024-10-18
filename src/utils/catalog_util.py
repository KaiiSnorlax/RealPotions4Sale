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
                    potion_id, potion_recipes.sku, potion_recipes.potion_name, potion_recipes.price, potion_recipes.red_ml, potion_recipes.green_ml, potion_recipes.blue_ml, potion_recipes.dark_ml, coalesce(sum(change), 0) as stock 
                FROM
                    potion_recipes
                LEFT JOIN potion_ledger ON potion_ledger.sku = potion_recipes.sku
                WHERE
                    potion_recipes.catalog = true
                GROUP BY
                    potion_recipes.sku
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
