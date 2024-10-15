from fastapi import FastAPI

from HW4.demo_service.api import users, utils
from HW4.demo_service.api.utils import initialize
from prometheus_fastapi_instrumentator import Instrumentator

def create_app():
    app = FastAPI(
        title="Testing Demo Service",
        lifespan=initialize
    )



    app.add_exception_handler(ValueError, utils.value_error_handler)
    app.include_router( users.router)

    return app

app = create_app()

Instrumentator().instrument(app).expose(app)