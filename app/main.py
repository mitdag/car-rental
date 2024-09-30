import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.auth import login, signup
from app.core.database import Base, engine
from app.routers import car, user, favorites, review, rental
from app.tests.test_sets import create_test_db

app = FastAPI()

app.include_router(login.router)
app.include_router(signup.router)
app.include_router(user.router)
app.include_router(car.router)
app.include_router(review.router)
app.include_router(rental.router)
app.include_router(create_test_db.router)
app.include_router(favorites.router)

Base.metadata.create_all(engine)

app.mount(
    "/static/templates/static",
    StaticFiles(directory="app/static/templates/static"),
    name="static",
)
# This code is here to run the app from pycharm
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
