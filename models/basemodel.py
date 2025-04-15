#!/usr/bin/python3
"""Base Model module"""

from uuid import uuid4
from datetime import datetime
from models.engine.db_manager import save_obj
from models.engine.db_manager import update_obj
from models.engine.db_manager import delete_obj

import models

time_format = "%Y-%m-%dT%H:%M:%S"

tables = {"User": "users",
          "Reference": "reference",
          "Project": "projects",
          "Line": "lines",
          "Process": "process",
          "Job": "production_jobs",
          "Harness": "harness_details",
          "Tracker": "harness_tracker",
          "Galia": "galia",
          "Scanned": "scanned_fx",
          "Log": "logs"
          }

class BaseModel:
    """BaseModel Definition"""
    
    def __init__(self, *args, **kwargs):
        """class initialisation"""
        if kwargs:
            for key, value in kwargs.items():
                if key != "__class__":
                    setattr(self, key, value)
            if kwargs.get("created_at", None):
                self.created_at = kwargs["created_at"]
            else:
                self.created_at = datetime.now()
            if kwargs.get("updated_at", None):
                self.updated_at = kwargs["updated_at"]
            else:
                self.updated_at = datetime.now()
            if kwargs.get("id", None) is None:
                self.id = str(uuid4())
        else:
            self.id = str(uuid4())
            self.created_at = datetime.now()
            self.updated_at = self.created_at

    def __str__(self):
        """String representation of the BaseModel class"""
        return "[{:s}] ({:s}) {}".format(self.__class__.__name__, self.id,
                                         self.__dict__)

    def to_dict(self):
        """returns a dictionary containing all keys/values of the instance"""
        new_dict = self.__dict__.copy()
        if "created_at" in new_dict:
            new_dict["created_at"] = new_dict["created_at"].strftime(time_format)
        if "updated_at" in new_dict:
            new_dict["updated_at"] = new_dict["updated_at"].strftime(time_format)
        return new_dict

    def save(self):
        """save object to postgres databse"""
        self.updated_at = datetime.now()
        obj_name = self.__class__.__name__
        table = tables[obj_name]
        obj_dict = self.to_dict()
        return save_obj(table, obj_dict)

    def update(self):
        """update object in postgres databse"""
        self.updated_at = datetime.now()
        obj_name = self.__class__.__name__
        table = tables[obj_name]
        obj_dict = self.to_dict()
        obj_id = obj_dict["id"]
        return update_obj(table, obj_dict, obj_id)

    def delete(self):
        """delete object from postgres databse"""
        obj_name = self.__class__.__name__
        table = tables[obj_name]
        obj_id = self.id
        return delete_obj(table, obj_id)