import uvicorn
from fastapi import FastAPI

from app import core
from app.auth import signup
from app.core.database import Base, engine
from app.routers import car, user

app = FastAPI()

app.include_router(user.router)
app.include_router(signup.router)
app.include_router(car.router)

Base.metadata.create_all(engine)

# This code is here to run the app from pycharm
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
