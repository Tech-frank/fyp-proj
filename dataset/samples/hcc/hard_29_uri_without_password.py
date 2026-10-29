from sqlalchemy import create_engine

DATABASE_URL = "postgresql://reporting@db.internal:5432/reports"
engine = create_engine(DATABASE_URL, connect_args={"sslmode": "require"})
