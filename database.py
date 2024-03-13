import sqlite3
import logging

from config import DB_NAME

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="log_file.txt",
    filemode="w",
)


def connect_db():
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    logging.info("The database has been created")
    cur.close()


def execute_query(sql_query, data=None, db_path=f'{DB_NAME}'):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    if data:
        cursor.execute(sql_query, data)
    else:
        cursor.execute(sql_query)

    connection.commit()
    connection.close()


def execute_selection_query(sql_query, data=None, db_path=f'{DB_NAME}'):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    if data:
        rows = cursor.execute(sql_query, data)
    else:
        rows = cursor.execute(sql_query)
    for row in rows:
        row
    connection.close()
    return row


def create_table():
    sql_query = '''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        subject TEXT,
        level TEXT,
        task TEXT,
        answer TEXT
        ); 
    '''
    execute_query(sql_query)


def insert_data(chat_id, subject):
    sql_query = 'INSERT INTO users(user_id, subject) VALUES(?, ?);'
    data = (chat_id, subject, )
    execute_query(sql_query, data)
    logging.info("A new user has been added to the database")


def update_data(chat_id, column, value):

    sql_query = f"UPDATE users SET {column} = ? WHERE user_id = ?;"
    data = (value, chat_id,)
    execute_query(sql_query, data)

    logging.info("The data in the database has been updated")


def select_data(chat_id):
    sql_query = "SELECT * FROM users WHERE user_id = ?;"
    data = (chat_id, )
    execute_selection_query(sql_query, data)
    logging.info("Data was requested from the database")


def delete_data(chat_id):
    sql_query = "DELETE FROM users WHERE user_id = ?;"
    data = (chat_id, )
    execute_query(sql_query, data)
    logging.info(f"The user's data for these id "
                 f"{chat_id} in the database has been deleted")


def prepare_db():
    connect_db()
    create_table()
