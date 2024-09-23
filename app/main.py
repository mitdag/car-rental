
from fastapi import FastAPI
import uvicorn

from app import core
from app.api import user
from app.auth import signup
from app.core.database import Base
from app.core.database import engine

app = FastAPI()

app.include_router(user.router)
app.include_router(signup.router)

Base.metadata.create_all(engine)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


#from app.schemas.address import AddressBase

    # a = AddressBase(
    #     street_name="Merellaan",
    #     number="102",
    #     postal_code="2289EB",
    #     city="Rijswijk",
    #     state="ZH",
    #     country="The Netherlands"
    # )
    #
    # print(a)
