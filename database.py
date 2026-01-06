import os
from sqlalchemy import create_engine,text
from dotenv import load_dotenv
load_dotenv()
MYSQL_USER =os.getenv("MYSQL_USER")
MYSQL_PASSWORD =os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT =os.getenv("MYSQL_PORT")
MYSQL_DB = os.getenv("MYSQL_DB")

DATABASE_URL = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
    f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
)

try:
    engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   # avoids stale connections
    pool_recycle=3600     # optional but good
)
    print("db connection established")
    
except Exception as  e:
    print("CONNECION FAILED",e)

