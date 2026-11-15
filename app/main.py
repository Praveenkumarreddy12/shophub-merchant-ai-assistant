
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI


from connection import initialize_database
from urls import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    print("ShopHub database initialized.")
    yield


app = FastAPI(
    title="ShopHub Store API",
    description="Multi-tenant e-commerce mock API",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)


@app.get("/")
def home():
    return {
        "message": "Welcome to ShopHub Store API",
        "status": "running"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
    print("Done")
