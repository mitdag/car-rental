import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination
from prometheus_fastapi_instrumentator import Instrumentator

from app.auth import login, logout, signup
from app.core.database import Base, engine
from app.routers import admin_user_tools, car, favorites, rental, review, user
from app.tests.test_sets import create_test_db

app = FastAPI()

Instrumentator().instrument(app).expose(app)

add_pagination(app)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)

app.include_router(signup.router)
app.include_router(login.router)
app.include_router(logout.router)
app.include_router(user.router)
app.include_router(car.router)
app.include_router(rental.router)
app.include_router(review.router)
app.include_router(create_test_db.router)
app.include_router(favorites.router)
app.include_router(admin_user_tools.router)

Base.metadata.create_all(engine)


# This code is here to run the app from pycharm
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
