from common import *
from datetime import datetime


class Student:
    def __init__(self, name: str, data):
        self.name = name
        self.data_list = [data]

    def insert_data(self, new_data):
        self.data_list.append(new_data)
