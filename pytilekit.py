import json
from pyloader.map import Map
from io import TextIOWrapper

def load(export_file:TextIOWrapper):
    data_dict = json.load(export_file)
    return Map(data_dict)