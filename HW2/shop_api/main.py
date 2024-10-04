from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator


from HW2.routers.queries import router_item,router_cart
from HW2.routers.chat.chat import chat_router


app = FastAPI(title="Shop API")

#Instrumentator().instrument(app).expose(app)


app.include_router(router_cart)
app.include_router(router_item)
app.include_router(chat_router)