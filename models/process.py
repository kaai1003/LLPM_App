#!/usr/bin/python3
"""process Class module"""

from models.basemodel import BaseModel

class Process(BaseModel):
    def __init__(self, *args, **kwargs):
        """Object init"""
        super().__init__(*args, **kwargs)
