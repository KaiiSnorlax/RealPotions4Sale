from enum import Enum

import sqlalchemy
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src import database as db
from src.api import auth
from src.utils import cart_util, customer_util, ledger, potions_util

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)


class SearchResultsEntry(BaseModel):
    line_item_id: int
    item_sku: str
    customer_name: str
    line_item_total: int
    timestamp: str


class SearchResults(BaseModel):
    previous: str
    next: str
    results: list[SearchResultsEntry]


class SearchSortOptions(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"


class SearchSortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: SearchSortOptions = SearchSortOptions.timestamp,
    sort_order: SearchSortOrder = SearchSortOrder.desc,
):
    search_results: list[SearchResultsEntry] = []

    customer_name = "%" + customer_name + "%"
    potion_sku = "%" + potion_sku + "%"

    if search_page == "" or int(search_page) == 1:
        page = 1
        prev_page = ""
    else:
        page = int(search_page)
        prev_page = str(page - 1)

    offset_val = (page - 1) * 5

    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                f"""
                SELECT customer.name AS customer_name, potion.sku AS item_sku, cart_item.id AS line_item_id, real_timestamp AS timestamp, gold_ledger.change AS line_item_total
                FROM customer
                JOIN visit ON visit.customer_id = customer.id
                JOIN cart ON cart.visit_id = visit.id
                JOIN cart_item ON cart_item.cart_id = cart.id
                JOIN potion ON potion.id = cart_item.potion_id
                JOIN checkout ON checkout.cart_item_id = cart_item.id 
                JOIN gold_ledger ON gold_ledger.transaction_id = checkout.transaction_id 
                WHERE customer.name ILIKE :customer_name AND potion.sku ILIKE :potion_sku
                ORDER BY {sort_col.value} {sort_order.value}
                LIMIT 6
                OFFSET :offset_val
                """
            ).bindparams(offset_val=offset_val, customer_name=customer_name, potion_sku=potion_sku)
        ).mappings()

        for row in result:
            search_results.append(
                SearchResultsEntry(
                    line_item_id=row.line_item_id,
                    item_sku=row.item_sku,
                    customer_name=row.customer_name,
                    line_item_total=row.line_item_total,
                    timestamp=row.timestamp.isoformat(),
                )
            )

        if len(search_results) <= 5:
            next_page = ""
        else:
            next_page = str(page + 1)
            search_results.pop(5)

        return SearchResults(previous=prev_page, next=next_page, results=search_results)


class Customer(BaseModel):
    customer_name: str
    character_class: str
    level: int


def customers_to_json(customers: list[Customer]) -> str:
    # Turn barrels_delivered into json format to use PostgreSQL json_populate_recordset **TO-DO: FIND LESS UGLY WAY OF DOING THIS**
    return (
        "["
        + ",".join(
            [
                f'{{"customer_name": "{customer.customer_name}", "character_class": "{customer.character_class}", "customer_level": {customer.level}}}'
                for customer in customers
            ]
        )
        + "]"
    )


@router.post("/visits/{visit_id}")
def post_visits(visit_id: int, customers: list[Customer]):

    # Which customers visited the shop today?

    customer_util.add_new_customer(customers_to_json(customers), visit_id)

    print(f"Customers Visited: {customers}")
    return "OK"


@router.post("/")
def create_cart(customer: Customer):

    cart_id = cart_util.create_new_cart(customer.customer_name, customer.character_class, customer.level)

    print(
        f"Cart Created: {customer.customer_name} (level: {customer.level}, class: {customer.character_class}) created a cart with an id of {cart_id}"
    )

    return {"cart_id": cart_id}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):

    cart_util.add_item_to_cart(cart_id, potions_util.get_id_from_sku(item_sku), cart_item.quantity)

    print(f"Item Added to Cart: added {item_sku} (x{cart_item.quantity}) to cart {cart_id}")
    return cart_item.quantity


class CartCheckout(BaseModel):
    payment: str


@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):

    # Decrements potion stock and increments gold depending on customers order.

    transaction_total: tuple[int, int] = ledger.potion_sold(cart_id)

    print(
        f"Cart Checkout: cart {cart_id} purchased {transaction_total[0]} potions totalling {transaction_total[1]} gold"
    )

    return {
        "total_potions_bought": transaction_total[0],
        "total_gold_paid": transaction_total[1],
    }
