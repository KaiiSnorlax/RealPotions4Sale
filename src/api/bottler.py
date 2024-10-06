from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
<<<<<<< Updated upstream
import sqlalchemy
from src import database as db
=======
from utils import potions_util, ledger
>>>>>>> Stashed changes

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)


<<<<<<< Updated upstream
class BottlePlan(BaseModel):
    potion_type: list[int]
=======
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
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
        update_global_inventory = sqlalchemy.text(
            "UPDATE global_inventory SET num_green_potions = num_green_potions + :quantity, num_green_ml = num_green_ml - (100 * :quantity)"
        ).bindparams(quantity=potion.quantity)

        with db.engine.begin() as connection:
            connection.execute(update_global_inventory)

    print(f"potions delievered: {potions_delivered} order_id: {order_id}")
=======
        print(potion)
        potion = fix_data(potion)

        ledger.potion_delivered(potion)
>>>>>>> Stashed changes

    return "OK"


@router.post("/plan")
def get_bottle_plan():

    # Creates a BottlePlan depending on how many multiples of 100ml of green I have and how much space I have left (assuming I get 50)

    with db.engine.begin() as connection:
        inventory = (
            connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
            .mappings()
            .first()
        )

    free_space = 50 - inventory["num_green_potions"]
    possible_potions = inventory["num_green_ml"] // 100

    potions_to_bottle = []

    if (free_space == 0) or (possible_potions == 0):
        print(f"Bottle plan: {potions_to_bottle}")
        return potions_to_bottle

    elif possible_potions >= free_space:
        potions_to_bottle.append(
            BottlePlan(
                potion_type=[0, 100, 0, 0],
                quantity=possible_potions - (possible_potions - free_space),
            )
        )

    else:
        potions_to_bottle.append(
            BottlePlan(potion_type=[0, 100, 0, 0], quantity=possible_potions)
        )

    print(f"Bottle plan: {potions_to_bottle}")
    return potions_to_bottle


if __name__ == "__main__":
    print(get_bottle_plan())
