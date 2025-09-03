from sqlalchemy import create_engine, text
from config import settings

DATABASE_URL = "oracle+oracledb://eccgoat:joaco0615@localhost:1521/xepdb1"

engine = create_engine(settings.database_url, echo=True)

with engine.connect() as conn:
    result = conn.execute(text("SELECT sysdate FROM dual"))
    print(result.fetchone())
