from fastapi import APIRouter, HTTPException, Query, Response
from http import HTTPStatus
from typing import List, Optional
from pydantic import NonNegativeFloat,NonNegativeInt,PositiveInt
from HW2.models.models import Item, ItemInCart,Cart
import json



router_cart = APIRouter(prefix="/cart")
router_item = APIRouter(prefix="/item")



carts = {}

items = {1: Item(id=1,name="test",price=150), 2:Item(id=2,name="test2",price=152, deleted =True)}


def generate_id_carts():
    return max(carts.keys(), default=0) + 1
def generate_id_item():
    return max(items.keys(), default=0) + 1


@router_cart.post("")
async def create_cart(response: Response):
        cart_id = generate_id_carts()
        carts[cart_id] =Cart(id = cart_id , items =[], price =0.0)
        response.headers["location"] = f"/carts/{cart_id}"
        response.status_code = HTTPStatus.CREATED

        return {"id":cart_id}


@router_cart.get("/{id}",status_code =HTTPStatus.OK)
async def get_cart(id:int):
    if id not in carts.keys():
        raise HTTPException(status_code = 404, detail = "cart_not_found")

    return carts[id]


@router_cart.get("",status_code =HTTPStatus.OK)
async def get_cart_by_params(offset:NonNegativeInt = 0, limit: PositiveInt = 10, min_price:NonNegativeFloat = None,
                             max_price: NonNegativeFloat = None,
                             min_quantity: NonNegativeInt = None,max_quantity :NonNegativeInt = None):

    filtered_carts = list(carts.values())

    if min_price is not None:
        filtered_carts = [cart for cart in filtered_carts if cart.price >= min_price]
    if max_price is not None:
        filtered_carts = [cart for cart in filtered_carts if cart.price <= max_price]
    if min_quantity is not None:
        filtered_carts = [cart for cart in filtered_carts if sum(item.quantity for item in cart.items) >= min_quantity]
    if max_quantity is not None:
        filtered_carts = [cart for cart in filtered_carts if sum(item.quantity for item in cart.items) <= max_quantity]
    filtered_carts= filtered_carts[offset:offset + limit]

    response = [{"id":x.id, "quantity":sum(item.quantity for item in x.items), "price": x.price} for x in filtered_carts ]
    # for i,j in enumerate(filtered_carts):
    #     filtered_carts[i]["quantity"] = quant[i]
    # ids = [int(x.id) for x in filtered_carts]
    #response = dict(zip(ids,filtered_carts))
    return response


@router_cart.post("/{cart_id}/add/{item_id}",status_code =HTTPStatus.OK)
def add_item_to_cart(cart_id: int, item_id: int):
    if cart_id not in carts.keys():
        raise HTTPException(status_code=404, detail="Cart not found")
    if item_id not in items.keys():
        raise HTTPException(status_code=404, detail="Item not found")

    cart = carts[cart_id]
    item = items[item_id]

    for cart_item in cart.items:
        if cart_item.id == item_id:
            cart_item.quantity += 1
            cart.price += item.price
            return {"message": "Item quantity increased"}

    cart.items.append(ItemInCart(id=item.id, name=item.name, quantity=1, available=not item.deleted))
    cart.price += item.price
    return {"message": "Item added to cart"}

@router_item.post("",status_code = HTTPStatus.CREATED )
async def create_item(item: dict):
    _id =generate_id_item()
    item = Item(id = _id, name = item["name"], price = item["price"])
    items[_id] = item
    return item


@router_item.get("/{item_id}",status_code = HTTPStatus.OK)
async def get_item(item_id:int):
    if items[item_id].deleted == True:
        raise HTTPException(status_code=404, detail ="Item doesnt exist")
    return items[item_id]

@router_item.get("",status_code = HTTPStatus.OK)
async def get_item_params(offset:NonNegativeInt = 0, limit: PositiveInt = 10, min_price:NonNegativeFloat = None,
                             max_price: NonNegativeFloat = None,
                             show_deleted:bool =None):
    filtered_items = list(items.values())

    if not show_deleted:
        filtered_items = [item for item in filtered_items if not item.deleted]
    if min_price is not None:
        filtered_items = [item for item in filtered_items if item.price >= min_price]
    if max_price is not None:
        filtered_items = [item for item in filtered_items if item.price <= max_price]

    return filtered_items[offset:offset + limit]

@router_item.put("/{item_id}",status_code = HTTPStatus.OK)
def update_item(item_id: int, item: dict):
    if "name" not in item.keys() or "price" not in item.keys():
        raise HTTPException(status_code=422, detail="not all params provided")
    new_item = Item(id=item_id,name=item["name"],price=item["price"])
    items[item_id] = new_item
    return new_item

@router_item.patch("/{item_id}",status_code = HTTPStatus.OK)
def partial_update_item(item_id: int, item: dict):

    stored_item = items[item_id]
    if stored_item.deleted == True:
        raise HTTPException(status_code=304, detail="Item not modified")
    if not set(item.keys()).issubset(set(stored_item.model_dump().keys())) or "deleted" in item.keys():
        raise HTTPException(status_code=422, detail="wrong field")
    updated_item=stored_item.model_copy(update=item)
    items[item_id] = updated_item
    return updated_item

@router_item.delete("/{item_id}")
def delete_item(item_id: int):
    if item_id not in items.keys():
        raise HTTPException(status_code=404, detail="Item not found")
    items[item_id].deleted = True
    return items[item_id]