from typing import Tuple
from fastapi import APIRouter
from pydantic import BaseModel
from utils import potions_util

router = APIRouter()


class Catalog(BaseModel):
    sku: str
    name: str
    quantity: int
    price: int
    potion_type: Tuple[int, int, int, int]


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """

    catalog = potions_util.get_current_catalog()

    return catalog
