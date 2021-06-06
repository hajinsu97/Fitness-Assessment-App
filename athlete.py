from common import *


class Athlete:
    def __init__(self, name: str, results):
        self.name = name
        self.results_list = [results]

    def add_results(self, new_results):
        self.results_list.append(new_results)
