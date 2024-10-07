from typing import Tuple
from fastapi import APIRouter
from pydantic import BaseModel
from src.utils import potions_util

router = APIRouter()


class Catalog(BaseModel):
    sku: str
    name: str
    quantity: int
    price: int
    potion_type: Tuple[int, int, int, int]


@router.get("/catalog/", tags=["catalog"])
def get_catalog():

    catalog = potions_util.get_current_catalog()

    print(f"Get Catalog: {catalog}")

    return catalog
