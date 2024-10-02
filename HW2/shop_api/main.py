from fastapi import FastAPI
from HW2.routers.queries import router_item,router_cart
app = FastAPI(title="Shop API")
app.include_router(router_cart)
app.include_router(router_item)