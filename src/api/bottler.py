from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
from utils import potions_util, ledger

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

    def from_tuple(sku: str, potion: tuple[int, int, int, int]):
        return PotionRecipe(
            sku=sku,
            red_ml=potion[0],
            green_ml=potion[1],
            blue_ml=potion[2],
            dark_ml=potion[3],
        )


class PotionDelivered(BaseModel):
    potion_type: PotionRecipe
    quantity: int


class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int


def fix_data(data: PotionInventory) -> PotionDelivered:
    return PotionDelivered(
        potion_type=PotionRecipe.from_tuple(
            sku=potions_util.get_sku_from_type(data.potion_type),
            potion=data.potion_type,
        ),
        quantity=data.quantity,
    )


@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):

    # Increment amount of green_potions based on quantity from BottlePlan

    for potion in potions_delivered:
        potion = fix_data(potion)

        ledger.potion_delivered(potion)

    return "OK"


@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    # Creates a BottlePlan depending on how many multiples of 100ml of green I have and how much space I have left (assuming I get 50)

    plan = potions_util.create_bottle_plan()

    print(f"Bottle plan: {plan}")
    return plan


if __name__ == "__main__":
    print(get_bottle_plan())
