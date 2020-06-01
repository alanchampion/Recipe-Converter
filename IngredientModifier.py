import tempfile
from subprocess import call
import os, sys
import codecs
from enum import Enum
import json
import csv
import re
import random

class Flavor(Enum):
    SAVORY = "savory"
    BITTER = "bitter"
    TART = "tart"
    SWEET = "sweet"
    STRONG = "strong"
    DRY = "dry"
    SPICY = "spicy"
    FRESH = "fresh"
    SMOKY = "smoky"
    CREAMY = "creamy"
    HERBAL = "herbal"
    HOT = "hot"

class 

class Bottle:
    def __init__(self, name, flavors):
        self.name = name
        self.flavors = flavors

    def __str__(self):
        print("%s")

    def to_json(self):
        dictionary = {}
        dictionary["name"] = self.name
        dictionary["flavors"] = self.flavors

    def write_to_file(self, folder):
        data = self.to_json()
        file = folder + '/' + self.name.replace(" ", "") + ".json"

        while os.path.exists(file):
            print("The file %s already exists. Do you want to (r)eplace the file or create (n)ew?" % file)
            selection = input("> ")
            if selection.lower() == 'r':
                os.remove(file)
            else:
                name = input('New name: ')
                file = folder + '/' + name.replace(" ", "") + ".json"
        with codecs.open(file, encoding='utf-8', mode='w') as outfile:
            json.dump(data, outfile)

if not os.path.exists("Ingredients"):
    os.makedirs("Ingredients")

