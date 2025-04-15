#!/usr/bin/python3
"""Database connection module"""

import csv
import json
import os
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor


def get_connection(db_conn):
    try:
        conn = psycopg2.connect(**db_conn)
        return conn
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

def save_obj(table, data):
        """Save obj"""
        db_conn_str = os.environ.get("DB_CONN", "{}")
        DB_CONFIG = json.loads(db_conn_str)
        conn = get_connection(DB_CONFIG)
        if conn is None:
            print("Connection failed")
            return None
        try:
            cursor = conn.cursor()
            colums = ', '.join(data.keys())
            values = ', '.join(['%s'] * len(data))
            query = "INSERT INTO {} ({}) VALUES ({}) RETURNING id;".format(table, colums, values)
            cursor.execute(query, tuple(data.values()))
            conn.commit()
            obj_id = cursor.fetchone()[0]
            return obj_id
        except Exception as e:
            print(e)
            return None
        finally:
            cursor.close()
            conn.close()

def get_obj(table, col, value):
    """Get obj"""
    db_conn_str = os.environ.get("DB_CONN", "{}")
    DB_CONFIG = json.loads(db_conn_str)
    conn = get_connection(DB_CONFIG)
    if conn is None:
        print("Connection failed")
        return None
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        query = sql.SQL("SELECT * FROM {} WHERE {} = %s;").format(sql.Identifier(table),
                                                                  sql.Identifier(col))
        cursor.execute(query, (value,))
        obj = cursor.fetchone()
        return dict(obj) if obj else None
    except Exception as e:
        print(e)
        return None
    finally:
        cursor.close()
        conn.close()

def get_list_obj(table, col, value):
    """Get obj"""
    db_conn_str = os.environ.get("DB_CONN", "{}")
    DB_CONFIG = json.loads(db_conn_str)
    conn = get_connection(DB_CONFIG)
    if conn is None:
        print("Connection failed")
        return None
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        query = sql.SQL("SELECT * FROM {} WHERE {} = %s;").format(sql.Identifier(table),
                                                                  sql.Identifier(col))
        cursor.execute(query, (value,))
        list_obj = cursor.fetchall()
        return [dict(obj) for obj in list_obj] if list_obj else None
    except Exception as e:
        print(e)
        return None
    finally:
        cursor.close()
        conn.close()

def update_obj(table, data, obj_id):
    """Update obj"""
    db_conn_str = os.environ.get("DB_CONN", "{}")
    DB_CONFIG = json.loads(db_conn_str)
    conn = get_connection(DB_CONFIG)
    if conn is None:
        print("Connection failed")
        return None
    try:
        cursor = conn.cursor()
        set_values = ', '.join([f"{key} = %s" for key in data.keys()])
        query = "UPDATE {} SET {} WHERE id = %s;".format(table, set_values)
        cursor.execute(query, tuple(data.values()) + (obj_id,))
        conn.commit()
        return True
    except Exception as e:
        print(e)
        return False
    finally:
        cursor.close()
        conn.close()

def get_all(table):
    """Get all"""
    db_conn_str = os.environ.get("DB_CONN", "{}")
    DB_CONFIG = json.loads(db_conn_str)
    conn = get_connection(DB_CONFIG)
    if conn is None:
        print("Connection failed")
        return None
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        query = sql.SQL("SELECT * FROM {};").format(sql.Identifier(table))
        cursor.execute(query)
        obj = cursor.fetchall()
        list_obj = []
        for item in obj:
            list_obj.append(dict(item))
        return list_obj
    except Exception as e:
        print(e)
        return None
    finally:
        cursor.close()
        conn.close()

def delete_obj(table, obj_id):
    """Delete obj"""
    db_conn_str = os.environ.get("DB_CONN", "{}")
    DB_CONFIG = json.loads(db_conn_str)
    conn = get_connection(DB_CONFIG)
    if conn is None:
        print("Connection failed")
        return None
    try:
        cursor = conn.cursor()
        query = "DELETE FROM {} WHERE id = %s;".format(table)
        cursor.execute(query, (obj_id,))
        conn.commit()
        return True
    except Exception as e:
        print(e)
        return False
    finally:
        cursor.close()
        conn.close()

def load_csv(csv_file):
    """Load CSV file as a list of dictionaries."""
    with open(csv_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)  # Reads CSV as dictionary
        return [dict(row) for row in reader]

def set_db_conn(db_conn):
    """Set DB connection as env variable"""
    # set db_conn dictionnary as windows env variable
    os.environ["DB_CONN"] = json.dumps(db_conn)