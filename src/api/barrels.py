from fastapi import APIRouter, Depends
from src.api import auth
from src.utils import barrels_util, ledger

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)


def barrels_to_json(barrels_delivered: list[barrels_util.Barrel]) -> str:
    # Turn barrels_delivered into json format to use PostgreSQL json_populate_recordset **TO-DO: FIND LESS UGLY WAY OF DOING THIS**
    return (
        "["
        + ",".join(
            [
                f'{{"color": "{barrels_util.get_barrel_type(barrel)}", "quantity": {barrel.quantity}, "ml_per_barrel": {barrel.ml_per_barrel}, "price": {barrel.price}}}'
                for barrel in barrels_delivered
            ]
        )
        + "]"
    )


@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[barrels_util.Barrel], order_id: int):

    ledger.barrel_bought(barrels_to_json(barrels_delivered))

    print(f"Barrels Delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"


# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[barrels_util.Barrel]):

    barrels_to_buy = barrels_util.create_barrel_plan(wholesale_catalog)

    print(f"Barrel catalog: {wholesale_catalog}")
    print(f"Barrel plan: {barrels_to_buy}")
    return barrels_to_buy
