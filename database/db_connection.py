import mysql.connector
from mysql.connector import Error
from config.config import DB_CONFIG


def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Database connection failed: {e}")
        raise


def execute_query(query, params=None, fetch=False):
    conn   = None
    cursor = None
    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())

        if fetch:
            return cursor.fetchall()

        conn.commit()
        return cursor.rowcount

    except Error as e:
        print(f"Query error: {e}")
        raise

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def execute_many(query, data_list):
    # Used when saving multiple predictions at once
    conn   = None
    cursor = None
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.executemany(query, data_list)
        conn.commit()
        return cursor.rowcount

    except Error as e:
        print(f"Bulk insert error: {e}")
        raise

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close