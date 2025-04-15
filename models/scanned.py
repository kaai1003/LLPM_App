#!/usr/bin/python3
"""scanned fx Class module"""

from models.basemodel import BaseModel

class Scanned(BaseModel):
    def __init__(self, *args, **kwargs):
        """Object init"""
        super().__init__(*args, **kwargs)
