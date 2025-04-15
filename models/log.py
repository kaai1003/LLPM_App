#!/usr/bin/python3
"""log Class module"""

from models.basemodel import BaseModel

class Log(BaseModel):
    def __init__(self, *args, **kwargs):
        """Object init"""
        super().__init__(*args, **kwargs)
