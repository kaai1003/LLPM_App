#!/usr/bin/python3
"""Galia Class module"""

from models.basemodel import BaseModel
from models.engine.db_manager import get_connection

class Picking(BaseModel):
    """Galia Object Definition"""
    def __init__(self, *args, **kwargs):
        """Object init"""
        super().__init__(*args, **kwargs)

    def save_picking(self, data):
        """Save Galia"""
        conn = get_connection()
        if conn is None:
            print("Connection failed")
            return None
        try:
            cursor = conn.cursor()
            colums = ', '.join(data.keys())
            values = ', '.join(['%s'] * len(data))
            query = "INSERT INTO galia ({}) VALUES ({}) RETURNING id;".format(colums, values)
            cursor.execute(query, tuple(data.values()))
            conn.commit()
            galia_id = cursor.fetchone()[0]
            return galia_id
        except Exception as e:
            print(e)
            return None
        finally:
            cursor.close()
            conn.close()

    def retrieve_picking(self, nr_batch):
        """Retrieve Galia"""
        conn = get_connection()
        if conn is None:
            print("Connection failed")
            return None
        try:
            cursor = conn.cursor()
            query = "SELECT * FROM galia WHERE nr_galia = %s;"
            cursor.execute(query, (nr_batch,))
            galia = cursor.fetchone()
            return galia
        except Exception as e:
            print(e)
            return None
        finally:
            cursor.close()
            conn.close()
