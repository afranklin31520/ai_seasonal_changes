import mysql.connector
from mysql import *
def insert_into_db(values:list[str]):
    values = tuple(values)
    connector = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="password",
        database = "ai seasonal changes"
    )
    my_cursor = connector.cursor()
    insert_QUERY = f"INSERT INTO verge VALUES (%s,%s,%s,%s,%s,%s,%s,%s)".format(values)
    my_cursor.execute(insert_QUERY,values)
    connector.commit()
    my_cursor.close()
    connector.close()