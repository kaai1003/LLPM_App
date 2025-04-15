#!/usr/bin/python3
"""Job Class module"""

from models.basemodel import BaseModel

class Job(BaseModel):
    def __init__(self, *args, **kwargs):
        """Object init"""
        super().__init__(*args, **kwargs)
