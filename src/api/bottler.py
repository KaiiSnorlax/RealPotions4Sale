from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
from src.utils import potions_util, ledger

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)


class PotionRecipe(BaseModel):
    sku: str

    red_ml: int
    green_ml: int
    blue_ml: int
    dark_ml: int

    @staticmethod
    def from_tuple(sku: str, potion: tuple[int, int, int, int]):
        return PotionRecipe(
            sku=sku,
            red_ml=potion[0],
            green_ml=potion[1],
            blue_ml=potion[2],
            dark_ml=potion[3],
        )


class PotionDelivered(BaseModel):
    potion_type: tuple[int, int, int, int]
    quantity: int


def bottles_to_json(potions_delivered: list[PotionDelivered]) -> str:
    # Turn potions_delivered into json format to use PostgreSQL json_populate_recordset **TO-DO: FIND LESS UGLY WAY OF DOING THIS**
    return (
        "["
        + ",".join(
            [
                f'{{"potion_id": {potions_util.get_potion_from_type(potion.potion_type).recipe.potion_id}, "sku": "{potions_util.get_potion_from_type(potion.potion_type).recipe.sku}", "quantity": {potion.quantity}, "red_ml_cost": {potion.potion_type[0]}, "green_ml_cost": {potion.potion_type[1]}, "blue_ml_cost": {potion.potion_type[2]}, "dark_ml_cost": {potion.potion_type[3]}}}'
                for potion in potions_delivered
            ]
        )
        + "]"
    )


@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionDelivered], order_id: int):

    ledger.potion_delivered(bottles_to_json(potions_delivered))

    return "OK"


@router.post("/plan")
def get_bottle_plan():

    plan = potions_util.get_potion_plan()

    print(f"Get Bottle Plan: {plan}")
    return plan


if __name__ == "__main__":
    print(get_bottle_plan())
