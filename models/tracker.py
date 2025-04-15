#!/usr/bin/python3
"""tracker fx Class module"""

from models.basemodel import BaseModel

class Tracker(BaseModel):
    def __init__(self, *args, **kwargs):
        """Object init"""
        super().__init__(*args, **kwargs)
