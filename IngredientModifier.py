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
    def __new__(cls, value, label):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.label = label
        return obj
    BITTER = 0, "bitter"
    CREAMY = 1, "creamy"
    DRY = 2, "dry"
    FRESH = 3, "fresh"
    HERBAL = 4, "herbal"
    HOT = 5, "hot"
    SAVORY = 6, "savory"
    SMOKY = 7, "smoky"
    SPICY = 8, "spicy"
    STRONG = 9, "strong"
    SWEET = 10, "sweet"
    TART = 11, "tart"
    NONE = 12, "none"


class Bottle:
    def __init__(self, name, flavors):
        self.name = name
        self.flavors = flavors

    def __str__(self):
        print("%s")

    def to_json(self):
        dictionary = {}
        dictionary["name"] = self.name
        dictionary["flavors"] = []
        for flavor in self.flavors:
            dictionary["flavors"].append(flavor.label)
        return dictionary

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

Simple_Ingredients = []

if os.path.exists("Ingredients.csv"):
    with codecs.open('Ingredients.csv', encoding='utf-8', mode='r') as ingredients_file:
        r = csv.reader(ingredients_file)
        Simple_Ingredients = list(r)
        Simple_Ingredients = [val for sublist in Simple_Ingredients for val in sublist]
        ingredients_file.close()

for ingredient in Simple_Ingredients:
    if not os.path.exists("Ingredients/" + ingredient.replace(" ", "") + ".json"):
        print(f"~ {ingredient.capitalize()} ~")
        print("What flavors is this ingredient?")
        for flavor in Flavor:
            print(f"{flavor.value}) {flavor.label.capitalize()}")
        num_flavors = input("> ").split()

        flavors = []
        for flavor in num_flavors:
            flavors.append(Flavor(int(flavor)))

        bottle = Bottle(ingredient, flavors)
        bottle.write_to_file("Ingredients")

        print("")