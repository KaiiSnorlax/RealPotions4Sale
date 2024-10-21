from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
from enum import Enum
from src.utils import customer_util, cart_util, ledger, potions_util

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

    return SearchResults(
        previous="",
        next="",
        results=[
            SearchResultsEntry(
                line_item_id=1,
                item_sku="1 oblivion potion",
                customer_name="Scaramouche",
                line_item_total=50,
                timestamp="2021-01-01T00:00:00Z",
            )
        ],
    )


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

    cart_id = cart_util.create_new_cart(
        customer.customer_name, customer.character_class, customer.level
    )

    print(
        f"Cart Created: {customer.customer_name} (level: {customer.level}, class: {customer.character_class}) created a cart with an id of {cart_id}"
    )

    return {"cart_id": cart_id}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):

    cart_util.add_item_to_cart(
        cart_id, potions_util.get_id_from_sku(item_sku), cart_item.quantity
    )

    print(
        f"Item Added to Cart: added {item_sku} (x{cart_item.quantity}) to cart {cart_id}"
    )
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
