from fastapi import FastAPI

from app.middlewares.error_log import ErrorLoggingMiddleware
from app.routers import category, products, auth, permission, users, review

app = FastAPI(swagger_ui_parameters={"persistAuthorization": True})
# app.add_middleware(ErrorLoggingMiddleware)


@app.get("/")
async def welcome() -> dict:
    return {"message": "My e-commerce app"}


app.include_router(category.router)
app.include_router(products.router)
app.include_router(auth.router)
app.include_router(permission.router)
app.include_router(users.router)
app.include_router(review.router)
# app.include_router(errors.router)
