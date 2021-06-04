class Student:
    def __init__(self, name: str):
        self.name = name
        self.data = []

    def add_data(self, data):
        self.data.append(data)
