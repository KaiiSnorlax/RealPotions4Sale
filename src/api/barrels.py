from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)


class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int


class BarrelOrder(BaseModel):
    sku: str
    quantity: int


@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    """ """
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"


# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """

    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                "UPDATE global_inventory SET gold = gold - "
                + str(wholesale_catalog[0].price)
                + ", num_green_ml = num_green_ml + "
                + str(wholesale_catalog[0].ml_per_barrel)
                + " WHERE num_green_potions < 10 AND gold >= "
                + str(wholesale_catalog[0].price)
                + ""
            )
        )
        return BarrelOrder(
            sku=wholesale_catalog[0].sku,
            quantity=wholesale_catalog[0].quantity,
        )

    # return BarrelOrder(
    #     sku=wholesale_catalog[0].sku,
    #     quantity=wholesale_catalog[0].quantity,
    # )
