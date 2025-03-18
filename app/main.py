from fastapi import FastAPI

from app.middlewares.error_log import ErrorLoggingMiddleware
from app.routers import category, products, errors


app = FastAPI()
# app.add_middleware(ErrorLoggingMiddleware)


@app.get("/")
async def welcome() -> dict:
    return {"message": "My e-commerce app"}


app.include_router(category.router)
app.include_router(products.router)
# app.include_router(errors.router)
