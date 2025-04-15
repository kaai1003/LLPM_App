#!/usr/bin/python3
"""line Class module"""

from models.basemodel import BaseModel

class Line(BaseModel):
    def __init__(self, *args, **kwargs):
        """Object init"""
        super().__init__(*args, **kwargs)
