from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum
import sqlalchemy
from src import database as db
from src.api import info

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)


class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"


class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"


@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku,
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """

    return {
        "previous": "",
        "next": "",
        "results": [
            {
                "line_item_id": 1,
                "item_sku": "1 oblivion potion",
                "customer_name": "Scaramouche",
                "line_item_total": 50,
                "timestamp": "2021-01-01T00:00:00Z",
            }
        ],
    }


class Customer(BaseModel):
    customer_name: str
    character_class: str
    level: int


@router.post("/visits/{visit_id}")
def post_visits(visit_id: int, customers: list[Customer]):
    """
    Add new customers who visited to database
    Add new and returning customers vistit information to database for data analysis
    """

    for traveler in customers:
        with db.engine.begin() as connection:
            add_new_customer = sqlalchemy.text(
                "INSERT INTO customers (name, class, level) VALUES (:customer_name, :character_class, :level) ON CONFLICT DO NOTHING"
            ).bindparams(
                customer_name=traveler.customer_name,
                character_class=traveler.character_class,
                level=traveler.level,
            )
            connection.execute(add_new_customer)

            get_customer_id = sqlalchemy.text(
                "SELECT (customer_id) FROM customers WHERE (name = :customer_name)"
            ).bindparams(customer_name=traveler.customer_name)

            unique_visit = connection.execute(get_customer_id).mappings().all()

            for visit in unique_visit:

                add_new_visit = sqlalchemy.text(
                    "INSERT INTO customer_visits (visit_id, customer_id, hour_visited, day_visited) VALUES (:id, :visit, :hour, :day)"
                ).bindparams(
                    id=visit_id,
                    visit=visit["customer_id"],
                    hour=info.time.hour,
                    day=info.time.day,
                )

                connection.execute(add_new_visit)

    print(customers)

    return "OK"


@router.post("/")
def create_cart(new_cart: Customer):
    """ """
    return {"cart_id": 1}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    return CartItem(quantity=1)


class CartCheckout(BaseModel):
    payment: str


@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):

    # Decrements potion stock and increments gold depending on customers order.
    # For now, only take into account when one potion bought.

    update_global_inventory = sqlalchemy.text(
        "UPDATE global_inventory SET num_green_potions = num_green_potions - 1, gold = gold + 50 WHERE num_green_potions > 0"
    )

    with db.engine.begin() as connection:
        connection.execute(update_global_inventory)

    return {"total_potions_bought": 1, "total_gold_paid": 50}
