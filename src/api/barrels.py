from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
from src.utils import barrels_util

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


@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):

    for barrel in barrels_delivered:
        barrels_util.barrel_delivered(
            Barrel(
                sku=barrel.sku,
                ml_per_barrel=barrel.ml_per_barrel,
                potion_type=barrel.potion_type,
                price=barrel.price,
                quantity=barrel.quantity,
            )
        )

    print(f"Barrels Delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"


# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):

    barrels_to_buy = barrels_util.create_barrel_plan(wholesale_catalog)

    print(f"Barrel catalog: {wholesale_catalog}")
    print(f"Barrel plan: {barrels_to_buy}")
    return barrels_to_buy
