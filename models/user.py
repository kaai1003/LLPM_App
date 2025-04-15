#!/usr/bin/python3
"""users Class module"""

from models.basemodel import BaseModel

class User(BaseModel):
    def __init__(self, *args, **kwargs):
        """Object init"""
        super().__init__(*args, **kwargs)
