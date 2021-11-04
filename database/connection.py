from playhouse.db_url import connect
from config import DB_URL


database_connection = connect(DB_URL)
