from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import math

SQLALCHEMY_DATABASE_URL = "sqlite:///./car_rental.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Register Python's math.sin in the SQLite connection
def register_math_functions(db_connection, _):
    db_connection.create_function("sin", 1, math.sin)
    db_connection.create_function("cos", 1, math.cos)
    db_connection.create_function("acos", 1, math.acos)
    db_connection.create_function("radians", 1, math.radians)


# Bind the function to the connection
with engine.connect() as connection:
    # connection.connection.set_trace_callback(print)
    register_math_functions(connection.connection, None)
