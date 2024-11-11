from fastapi import APIRouter

from src.utils import catalog_util

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():

    catalog = catalog_util.get_catalog()

    print(f"Get Catalog: {catalog}")

    return catalog
