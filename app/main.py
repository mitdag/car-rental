import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.auth import signup, login
from app.core.database import Base
from app.core.database import engine
from app.routers import car
from app.routers import user

app = FastAPI()

app.include_router(login.router)
app.include_router(signup.router)
app.include_router(user.router)
app.include_router(car.router)

Base.metadata.create_all(engine)

app.mount(
    "/static/templates/static",
    StaticFiles(directory="app/static/templates/static"),
    name="static"
)
# This code is here to run the app from pycharm
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
