from fastapi import FastAPI, Request, exceptions
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from src.api import carts, catalog, bottler, barrels, admin, info, inventory
import json
import logging
from starlette.middleware.cors import CORSMiddleware

description = """
Central Coast Cauldrons is the premier ecommerce site for all your alchemical desires.
"""


class BadRequest:
    message: list[str] = []
    data: None = None


app = FastAPI(
    title="Central Coast Cauldrons",
    description=description,
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Lucas Pierce",
        "email": "lupierce@calpoly.edu",
    },
)

origins = ["https://potion-exchange.vercel.app"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(inventory.router)
app.include_router(carts.router)
app.include_router(catalog.router)
app.include_router(bottler.router)
app.include_router(barrels.router)
app.include_router(admin.router)
app.include_router(info.router)


@app.exception_handler(exceptions.RequestValidationError)  # type: ignore
@app.exception_handler(ValidationError)  # type: ignore
async def validation_exception_handler(
    request: Request, exc: exceptions.RequestValidationError | ValidationError
):
    logging.error(f"The client sent invalid data!: {exc}")
    exc_json = json.loads(exc.json())
    response = BadRequest()
    for error in exc_json:
        response.message.append(f"{error['loc']}: {error['msg']}")

    return JSONResponse(response, status_code=422)


@app.get("/")
async def root():
    return {"message": "Welcome to the Central Coast Cauldrons."}
