import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

ENGINE_URL = os.environ["INVENTORY_DATABASE_URL"]
engine = create_engine(ENGINE_URL, pool_pre_ping=True)
Session = sessionmaker(bind=engine)
