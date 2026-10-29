from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

ENGINE_URL = "postgresql://inventory:Inv3ntory_P4ss@10.0.3.21:5432/inventory"
engine = create_engine(ENGINE_URL, pool_pre_ping=True)
Session = sessionmaker(bind=engine)
