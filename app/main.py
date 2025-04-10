from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette import status
from starlette.middleware.gzip import GZipMiddleware

from app.routers import category, products, auth, permission, users, review, celery


load_dotenv()

app = FastAPI(swagger_ui_parameters={"persistAuthorization": True})

origins = [
    "http://127.0.0.1:8000",
    "http://localhost:3000",
    "https://example.com",
    "null"
]
allowed_hosts = ["example.com", "*.example.com", "127.0.0.1"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)
app.add_middleware(GZipMiddleware, minimum_size=500)


@app.get("/health_check", status_code=status.HTTP_200_OK)
async def welcome() -> dict:
    return {"message": "My e-commerce app"}


app.include_router(category.router)
app.include_router(products.router)
app.include_router(auth.router)
app.include_router(permission.router)
app.include_router(users.router)
app.include_router(review.router)
app.include_router(celery.router)
 