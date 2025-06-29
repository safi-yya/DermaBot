import os
from pg8000.native import Connection
from dotenv import load_dotenv

load_dotenv()

username = os.environ["PG_USERNAME"]
password = os.environ["PG_PASSWORD"]
database = os.environ["PG_DATABASE"]

# Create your create_conn function to return a database connection object    #
def create_conn():
    conn = Connection(
        username,
        password = password,
        database = database                                       
    )
    return conn
    
# Create a close_db function that closes a passed database connection object 
def close_db(db):
    db.close()