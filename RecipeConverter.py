#!/usr/bin/env python
import tempfile
from subprocess import call
import os, sys
import codecs
import traceback
import logging
from enum import Enum
import json
import csv
import re
import random
import difflib
import time
import datetime

Measurements = ["oz", ".oz", "oz.", "ounce", "ounces", "ml", ".ml", 
"ml.","tbsp", "tablespoon", "tablespoons", "tsp", "teaspoon", 
"teaspoons", "cup", "cups", "dash", "dashes", "drop", "drops", 
"quart", "quarts", "pint",  "pints", "liter", "liters", "inch", "g", "gram", "grams", 
"twist", "peel", "wedge", "wedges", "wheel", "slice", "spray", 
"slices", "ribbon", "ribbons", "sprig", "leaf", "leaves", "pinch", "piece", "pod", 
"grated", "rinse", "bottle", "bottles", "barspoon",
"barspoons", "piece", "pieces", "pound", "pounds", "lb", "lbs"]
Measurement_Convert = {
"oz": ["oz", ".oz", "oz.", "ounce", "ounces"],
"ml": ["ml", ".ml", "ml."],
"tbsp": ["tbs", "tbsp", "tablespoon", "tablespoons"],
"tsp": ["tsp", "teaspoon", "teaspoons"],
"cup": ["cup", "cups"],
"dash": ["dash", "dashes"],
"drop": ["drop", "drops"],
"quart": ["quart", "quarts"],
"pint": ["pint", "pints"],
"liter": ["liter", "liters"],
"gram": ["gram", "grams", "g"],
"wedge": ["wedge", "wedges"],
"slice": ["slice", "slices"],
"ribbon": ["ribbon", "ribbons"],
"leaf": ["leaf", "leaves"],
"bottle": ["bottle", "bottles"],
"barspoon": ["barspoon", "barspoons"],
"piece": ["pieces", "piece"],
"pound": ["pound", "pounds", "lb", "lbs"]
}
Filler_Words = ["of", "with", "fresh", "freshly", "1:1"]
Empty_Brackets = ["()", "/{/}", "[]"]
Garnish_Words = ["twist", "garnish", "peel", "wheel", "slice", "wedge", "sprig", "pod", "grated"]
Note_Words = ["top", "float", "rinse", "none"]
Flavors = ["bitter", "creamy", "dry", "fresh", "herbal", "hot", "savory", "smoky", "spicy", "strong", "sweet", "tart"]

os.system("")
logging.basicConfig(format='\033[31m%(message)s\033[0m')
logger = logging.getLogger('Logger')

# Group of Different functions for different styles
class Style:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

class Type:
    MAIN = "main"
    GARNISH = "garnish"
    OPTIONAL = "optional"

def get_type(str_type):
    if str_type == str(Type.MAIN):
        return Type.MAIN
    if str_type == str(Type.GARNISH):
        return Type.GARNISH
    if str_optional == str(Type.OPTIONAL):
        return Type.OPTIONAL

class Pack(Enum):
    NONALCOHOLIC = ("Nonalcoholic", 0)
    GROUP = ("Group", 1)
    NIGHTCAP = ("Nightcap", 2)
    DESSERT = ("Dessert", 3)
    BRUNCH = ("Brunch", 4)
    TIKI = ("Tiki", 5)
    DINNER = ("Dinner", 6)
    MYDRINKS = ("My Drinks", 7)

    def __init__(self, pack, importance):
        self.pack = pack
        self.importance = importance

def get_pack(pack):
    if pack == Pack.NONALCOHOLIC.pack:
        return Pack.NONALCOHOLIC
    if pack == Pack.GROUP.pack:
        return Pack.GROUP
    if pack == Pack.NIGHTCAP.pack:
        return Pack.NIGHTCAP
    if pack == Pack.DESSERT.pack:
        return Pack.DESSERT
    if pack == Pack.BRUNCH.pack:
        return Pack.BRUNCH
    if pack == Pack.TIKI.pack:
        return Pack.TIKI
    if pack == Pack.DINNER.pack:
        return Pack.DINNER
    if pack == Pack.MYDRINKS.pack:
        return Pack.MYDRINKS

class Glass(Enum):
    ROCK = "rocks"
    COLLINS = "collins"
    COLLINS2 = "highball"
    COUPE = "coupe"
    NANDN = "nick and nora"
    TIKI1 = "tiki"
    TIKI2 = "tiki"
    PILSNER = "pilsner"
    PINT = "pint"
    MUG = "mug"
    IRISHCOFFEE = "irish coffee"
    CHAMPAGNE = "flute"
    COCKTAIL = "cocktail"
    NONE = "none"

def get_glass(glass):
    if glass == Glass.ROCK.value:
        return Glass.ROCK
    if glass == Glass.COLLINS.value:
        return Glass.COLLINS
    if glass == Glass.COLLINS2.value:
        return Glass.COLLINS2
    if glass == Glass.COUPE.value:
        return Glass.COUPE
    if glass == Glass.NANDN.value:
        return Glass.NANDN
    if glass == Glass.TIKI1.value:
        return Glass.TIKI1
    if glass == Glass.TIKI2.value:
        return Glass.TIKI2
    if glass == Glass.PILSNER.value:
        return Glass.PILSNER
    if glass == Glass.PINT.value:
        return Glass.PINT
    if glass == Glass.MUG.value:
        return Glass.MUG
    if glass == Glass.IRISHCOFFEE.value:
        return Glass.IRISHCOFFEE
    if glass == Glass.CHAMPAGNE.value:
        return Glass.CHAMPAGNE
    if glass == Glass.COCKTAIL.value:
        return Glass.COCKTAIL
    return Glass.NONE

class Bottle:
    def __init__(self, name, flavors):
        self.name = name.lower()
        self.flavors = flavors

    def __str__(self):
        return f"{self.name} {self.flavors}"

    def to_json(self):
        dictionary = {}
        dictionary["name"] = self.name
        dictionary["flavors"] = self.flavors
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

class Bar:
    def __init__(self, bottles):
        self.bottles = bottles
    def __str__(self):
        string = "==============================- Bar -==============================\n"
        for bottle in self.bottles:
            string += str(bottle) + "\n"
        string += "==============================- Bar -==============================\n"
        return string
    def __getitem__(self, index):
        return self.bottles[index]
    def __contains__(self, item):
        return item.lower() in [bottle.name.lower() for bottle in self.bottles]
    def add_ingredient(self, name):
        if name in self:
            print(f"{name} is already in this bar. Do you want to override it?")
            override = input("> ")
            if override.lower() != "y":
                print(f"Not overriding ingredient {name}")
                return name
        
        matches = difflib.get_close_matches(name.lower(), self.get_names())
        if len(matches) > 0:
            print(f"There are ingredients similar to {name}. Would you like to use one of these?")
            for index, match in enumerate(matches):
                print(f"{index}) {self.get_bottle(match)}")
            index = input("> ")
            if index.isdigit() and int(index) < len(matches):
                return matches[int(index)]

        print(f"What flavors are in {name}? Type c to cancel.")
        for index, flavor in enumerate(Flavors):
            print(f"{index}) {flavor.capitalize()}")
        num_flavors = input("> ").split()

        flavors = []
        for index in num_flavors:
            if not index.isdigit():
                return name
            flavors.append(Flavors[int(index)])

        bottle = Bottle(name, flavors)
        try:
            bottle.write_to_file("Ingredients")
            self.bottles.append(bottle)
        except:
            print("Error saving ingredient.")

        print("")
        return name
    def get_names(self):
        return [bottle.name.lower() for bottle in self.bottles]
    def get_bottle(self, name):
        for bottle in self.bottles:
            if bottle.name == name.lower():
                return bottle
        return None

class RecipeBox:
    def __init__(self, location):
        self.recipes = []
        self.location = location

        if not os.path.exists(self.location):
            os.makedirs(self.location)

    def __str__(self):
        string = "%i Recipes Found" % len(self.recipes)
        string += "================================================================================\n"
        for recipe in self.recipes:
            string += recipe
            string += "\n"
        string += "================================================================================\n"
        return string

    def append(self, recipe):
        recipe.write_to_file(self.location)
        print(color_text(recipe, Style.CYAN))
        self.recipes.append(recipe)

class Ingredient:
    def __init__(self, amount, measurement, name, ingredient_type=Type.MAIN, notes="none"):
        self.name = name
        self.amount = amount
        self.measurement = measurement.lower()
        self.ingredient_type = ingredient_type
        self.notes = notes
        self.validate()

    def __str__(self):
        self.validate()
        string = ""

        if self.amount == "":
            string += "%s\n%s\n%s" % (self.measurement_text, self.name_text, self.ingredient_type)
        elif self.measurement == "":
            string += "%s\n%s\n%s" % (self.amount_text, self.name_text, self.ingredient_type)
        else:
            string += "%s\n%s\n%s\n%s" % (self.amount_text, self.measurement_text, self.name_text, self.ingredient_type)

        if(self.notes != "none"):
            string += "\n[%s]" % self.notes

        return string

    def validate(self):
        self.amount_valid = True
        self.name_valid = True
        self.measurement_valid = True
        self.amount_text = self.amount
        self.name_text = self.name
        self.measurement_text = self.measurement

        fixed_measurement = check_measurement(self.measurement)
        if fixed_measurement:
            measurement = fixed_measurement

        if not(check_number(self.amount) or self.amount == ""):
            self.amount_valid = False
            self.amount_text = color_text(self.amount, Style.RED)
        else:
            self.amount_text = color_text(self.amount, Style.GREEN)

        if self.name.lower() not in CurrentBar and self.name:
            self.name_valid = False
            self.name_text = color_text(self.name, Style.RED)
        elif not self.name:
            self.name_valid = False
            self.name_text = color_text("NONE", Style.RED)
        else:
            self.name_text = color_text(self.name, Style.GREEN)

        if self.measurement not in Measurements and self.measurement != "":
            self.measurement_valid = False
            self.measurement_text = color_text(self.measurement, Style.RED)
        else:
            self.measurement_text = color_text(self.measurement, Style.GREEN)

        return self.amount_valid and self.name_valid and self.measurement_valid

    def to_json(self):
        dictionary = {}
        dictionary["amount"] = self.amount
        dictionary["measurement"] = self.measurement
        dictionary["ingredient"] = self.name
        dictionary["type"] = self.ingredient_type
        dictionary["notes"] = self.notes
        return dictionary

    def print(self):
        string = ""

        if self.amount:
            string += "%s " % self.amount
        if self.measurement:
            string += "%s " % self.measurement
        string += "%s" % self.name

        if self.ingredient_type != Type.MAIN:
            string += " (%s)" % self.ingredient_type
        if self.notes != "none":
            string += " [%s]" % self.notes

        return string

    def print_with_errors(self):
        self.validate()
        string = ""

        if self.amount:
            string += f"{self.amount_text} "
        if self.measurement:
            string += f"{self.measurement_text} "

        string += f"{self.name_text}"

        if self.ingredient_type != Type.MAIN:
            string += " (%s)" % self.ingredient_type
        if self.notes != "none":
            string += " [%s]" % self.notes

        return string

class Recipe:
    def __init__(self, title, ingredients, instructions, information, labels, pack, glass, flavors=[]):
        self.title = title

        valid = True
        for ingredient in ingredients:
            if not ingredient.validate():
                valid = False
                break
        if valid:
            self.ingredients = ingredients
        else:
            self.ingredients = process_ingredients(ingredients)

        self.instructions = instructions
        self.information = information
        self.labels = labels
        self.flavors = flavors
        self.pack = pack
        self.glass = glass

    def __str__(self):
        string = "--------------------\n"
        string += self.title + "\n"
        string += "Pack: " + self.pack.pack + "\n"
        string += "Flavors: " + ", ".join(self.flavors) + "\n"
        string += "Old Labels: " + ", ".join(self.labels) + "\n"
        if self.glass != Glass.NONE:
            string += "Glass: " + self.glass.value.capitalize() + "\n\n"
        for ingredient in self.ingredients:
            string += ingredient.print() + "\n"
        string += "\n" + self.instructions + "\n\n"
        string += self.information + "\n"
        string += "--------------------"
        return string

    def to_json(self):
        dictionary = {}
        dictionary["title"] = self.title
        dictionary["pack"] = self.pack.pack
        dictionary["flavors"] = self.flavors
        dictionary["labels"] = self.labels
        dictionary["glass"] = simplify_glass(self.glass)
        dictionary["ingredients"] = []
        for ingredient in self.ingredients:
            dictionary["ingredients"].append(ingredient.to_json())
        dictionary["instructions"] = self.instructions
        dictionary["information"] = self.information

        return dictionary

    def write_to_file(self, folder):
        data = self.to_json()
        file = folder + '/' + self.title.replace(" ", "") + ".json"

        while os.path.exists(file):
            print("The file %s already exists. Do you want to (c)ompare the files, (r)eplace the file, or create (n)ew?" % file)
            selection = input("> ")
            if selection.lower() == 'r':
                os.remove(file)
            elif selection.lower() == 'n':
                name = input('New name: ')
                file = folder + '/' + name.replace(" ", "") + ".json"
            else:
                old_recipe = create_from_file(file)
                print_side_by_side(file, self.title)
                print_side_by_side(old_recipe, self)
        with codecs.open(file, encoding='utf-8', mode='w') as outfile:
            json.dump(data, outfile)

def create_from_file(file_name):
    new_recipe = Recipe("", [], "", "", [], "", "", [])

    with codecs.open(file_name, encoding='utf-8') as json_file:
        data = json.load(json_file)
        
        if 'title' in data:
            new_recipe.title = data['title']
        if 'pack' in data:
            pack = data['pack']
            new_recipe.pack = get_pack(pack)
        if 'flavors' in data:
            new_recipe.flavors = data['flavors']
        if 'labels' in data:
            new_recipe.labels = data['labels']
        if 'glass' in data:
            glass = data['glass']
            new_recipe.glass = get_glass(glass)
        else:
            new_recipe.glass = Glass.NONE
        if 'instructions' in data:
            new_recipe.instructions = data['instructions']
        if 'information' in data:
            new_recipe.information = data['information']
        if 'ingredients' in data:
            for ingredient in data['ingredients']:
                amount = ""
                measurement = ""
                name = ""
                ingredient_type = ""
                notes = ""

                if 'amount' in ingredient:
                    amount = ingredient['amount']
                if 'measurement' in ingredient:
                    measurement = ingredient['measurement']
                if 'ingredient' in ingredient:
                    name = ingredient['ingredient']
                if 'type' in ingredient:
                    ingredient_type = ingredient['type']
                    ingredient_type = get_type(ingredient_type)
                if 'notes' in ingredient:
                    notes = ingredient['notes']
                add_ingredient = Ingredient(amount, measurement, name, ingredient_type, notes)
                new_recipe.ingredients.append(add_ingredient)
        json_file.close()
    return new_recipe

def color_text(text, style):
    return "%s%s%s" % (style, text, Style.RESET)

def print_side_by_side(left, right, size=75, space=4):
    a = str(left).strip()
    b = str(right).strip()
    a_size = size
    b_size = size

    while a or b:
        a_find = a.find("\n")
        b_find = b.find("\n")

        if a_find < a_size and a_find != -1:
            a_size = a_find
        if b_find < b_size and b_find != -1:
            b_size = b_find
        print(a[:a_size].ljust(size) + " " * space + b[:b_size])
        a = a[a_size:].strip()
        b = b[b_size:].strip()
        a_size = size
        b_size = size

def convert_timedelta(duration):
    days, seconds = duration.days, duration.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 60)
    return days, hours, minutes, seconds

def check_number(text):
    try:
        a = float(text)
    except ValueError:
        return False
    else:
        return True

def format_number(text):
    if check_number(text):
        if text.isdigit():
            return int(text)
        else:
            return float(text)
    return text

def simplify_glass(glass):
    if glass == Glass.PINT:
        return Glass.PILSNER.value
    return glass.value

def check_measurement(measurement):
    for key, value in Measurement_Convert.items():
        if measurement.lower() in value:
            measurement = key
            return measurement
    return None

def remove_measurement(ingredient):
    ingredient = ingredient.strip()
    if not(ingredient.startswith('or ') or ingredient.startswith('-or- ') 
        or ('(' in ingredient and ')' in ingredient)
        or ('[' in ingredient and ']' in ingredient)):
        return ingredient

    if '(' in ingredient or ')' in ingredient:
        ingredient = re.sub(r" ?\([^)]+\)", "", ingredient).strip()
    if '[' in ingredient or ']' in ingredient:
        ingredient = re.sub(r" ?\[[^]]+\]", "", ingredient).strip()
    if ingredient.startswith('or ') or ingredient.startswith('-or- '):
        ingredient = divide_ingredient(ingredient).name

    return ingredient

def divide_ingredient(ingredient_text, set_type=False):
    ingredient_text = ingredient_text.lower()
    ingredient_type = Type.MAIN
    notes = "none"

    if "mint sprig" in ingredient_text:
        ingredient_text = ingredient_text.replace("mint sprig", "sprig mint")

    if set_type:
        for word in Garnish_Words:
            if word in ingredient_text:
                ingredient_type = Type.GARNISH
                break
        if Type.GARNISH in ingredient_text:
            ingredient_text = ingredient_text.replace("garnish", "")
        for note in Note_Words:
            if note in ingredient_text:
                notes = note
        if notes == "none":
            if '[' in ingredient_text and ']' in ingredient_text:
                notes = ingredient_text[ingredient_text.find("[")+1:ingredient_text.find("]")]
        if Type.OPTIONAL in ingredient_text:
            ingredient_type = Type.OPTIONAL
            ingredient_text = ingredient_text.replace("optional", "")
    else:
        if Type.GARNISH in ingredient_text:
            ingredient_type = Type.GARNISH
            ingredient_text = ingredient_text.replace("garnish", "")
        for note in Note_Words:
            if note in ingredient_text:
                notes = note
        if notes == "none":
            if '[' in ingredient_text and ']' in ingredient_text:
                notes = ingredient_text[ingredient_text.find("[")+1:ingredient_text.find("]")]
        if Type.OPTIONAL in ingredient_text:
            ingredient_type = Type.OPTIONAL
            ingredient_text = ingredient_text.replace("optional", "")
    temp = ingredient_text.split(" ")
    temp = [i.lower() for i in temp if i not in Empty_Brackets]
    if set_type:
        temp = [i.lower() for i in temp if i not in Filler_Words]
    divided_ingredient = []
    for item in temp:
        divided_ingredient.extend(re.findall(r"[0-9.]+|[^0-9]+", item))
    
    if len(divided_ingredient) == 2 and divided_ingredient[-1] in Garnish_Words:
        return Ingredient(1, divided_ingredient[1], divided_ingredient[0], ingredient_type)
    
    if len(divided_ingredient) > 3 and divided_ingredient[0].isdigit() and divided_ingredient[1] == "/" and divided_ingredient[2].isdigit():
        divided_ingredient = [str(int(divided_ingredient[0])/int(divided_ingredient[2]))] + temp[3:]

    need_number = True
    number_index = -1
    need_measurement = True
    measurement_index = -1
    need_ingredient = False
    ingredient_index = -1
    for number, item in enumerate(divided_ingredient):
        if need_number and check_number(item):
            number_index = number
            need_number = False
            need_measurement = True
        if need_measurement and item.lower() in Measurements:
            measurement_index = number
            need_measurement = False
            need_ingredient = True
        if need_ingredient and item.lower() not in Measurements:
            ingredient_index = number
            need_ingredient = False
        if item.lower() in [note.lower() for note in Note_Words]:
            notes = item.lower()

    if notes != "none" and notes in divided_ingredient:
        divided_ingredient.remove(notes)

    number = " ".join(divided_ingredient[:number_index+1])
    measurement = " ".join(divided_ingredient[number_index+1:measurement_index+1])
    fixed_measurement = check_measurement(measurement)
    
    if fixed_measurement:
        measurement = fixed_measurement
    if need_measurement:
        ingredient = " ".join(divided_ingredient[number_index+1:])
    else:
        ingredient = " ".join(divided_ingredient[ingredient_index:])
    ingredient = remove_measurement(ingredient)

    if notes.lower() == "top" and not number:
        number = "2"
        measurement = "oz"

    number = format_number(number)

    if ingredient in Measurements:
        garnish_word = ingredient
        ingredient = measurement.replace(" " + ingredient, "").strip()
        measurement = garnish_word

    return Ingredient(number, measurement, ingredient, ingredient_type, notes)

def delete_ingredients(divided_ingredients):
    print("Which ingredient(s) to delete?")
    sections = list(map(int, re.split(', |,| ', input('> '))))
    sections.sort(reverse=True)
    
    for section in sections:
        divided_ingredients.pop(section)

    return divided_ingredients

def change_ingredient_type(ingredient):
    print("What type do you want it to change to? (M)ain, (G)arnish, (O)ptional")
    selection = input("> ")
    if selection.lower() == "m":
        ingredient.ingredient_type = Type.MAIN
    elif selection.lower() == "g":
        ingredient.ingredient_type = Type.GARNISH
    elif selection.lower() == "o":
        ingredient.ingredient_type = Type.OPTIONAL
    else:
        print("Not a valid type")
    
    return ingredient

def modify_ingredient(ingredient):
    if not ingredient.validate():
        matches = difflib.get_close_matches(ingredient.name.lower(), CurrentBar.get_names())
        if len(matches) > 0:
            print(f"There are ingredients similar to {ingredient.name}. Would you like to use one of these? 'N' for no.")
            for index, match in enumerate(matches):
                print(f"{index}) {CurrentBar.get_bottle(match)}")
            index = input("> ")
            if index.isdigit() and int(index) < len(matches):
                ingredient.name = matches[int(index)]
                return divide_ingredient(ingredient.print())

    modified_ingredient = edit_text(ingredient.print())
    return divide_ingredient(modified_ingredient)

def process_ingredients(ingredients):
    while True:
        print('============================================================')
        for number, text in enumerate(ingredients):
            print('-----%i-----' % number)
            print("%s" % text)
            print('-----%i-----\n' % number)
        print('============================================================')
        print('\nValues in red do not conform to correct values.')
        print("Type number to modify that ingredient.")
        print("(D)elete ingredients")
        print("(A)dd ingredient")
        print("Change ingredient (T)ype")
        print("(S)ave new ingredient to possible ingredients")
        print("(P)rint current bar")
        print("(F)inish")
        print("(Q)uit and save with errors")
        selection = input('> ')

        try:
            if selection.lower() == "q" or selection.lower() == "quit":
                return ingredients
            elif selection.lower() == "d":
                delete_ingredients(ingredients)
            elif selection.lower() == "a":
                ingredient = edit_text("")
                ingredients.append(divide_ingredient(ingredient, True))
            elif selection.lower() == "t":
                print("Which ingredient do you want to change type of?")
                selection = input("> ")
                index = int(selection)
                if(index >= len(ingredients)):
                    print("Selection must be valid ingredient number.")
                ingredients[index] = change_ingredient_type(ingredients[index])
            elif selection.lower() == "s":
                print("Which ingredient do you want to save?")
                selection = input("> ")
                if selection.isdigit():
                    index = int(selection)
                    if(index >= len(ingredients)):
                        print("Selection must be valid ingredient number.")
                    ingredients[index].name = CurrentBar.add_ingredient(ingredients[index].name.lower())
            elif selection.lower() == "p":
                print(CurrentBar)
            elif selection.isnumeric():
                index = int(selection)
                if(index >= len(ingredients)):
                    print("Selection must be valid ingredient number.")
                ingredients[index] = modify_ingredient(ingredients[index])
            else:
                valid = True
                for ingredient in ingredients:
                    if not ingredient.validate():
                        valid = False
                        break
                if not valid:
                    print("Not all ingredients are valid. Type 'q' to force quit anyway.")
                else:
                    return ingredients
        except Exception as e:
            logger.error("Error trying to process request.")
            logger.error(e)


def edit_text(data):
    EDITOR = os.environ.get('EDITOR', 'vim')

    with tempfile.NamedTemporaryFile(suffix=".tmp", dir=os.getcwd()) as tmp:
        tmp.write(data.encode('utf-8'))
        tmp.flush()
        call([EDITOR, "-n", tmp.name])

        # For some reason, this does not remember changes made to file. 
        # tmp.seek(0)
        # data = tmp.read().decode('utf-8').strip()
        file = open(tmp.name, "r")
        data = file.read().strip()
        tmp.close()
    print(data)

    return data

def find_notes(text):
    notes = []
    split_text = re.split(r"\n", text)
    ingredient = ""
    measurement = ""
    amount = ""
    need_ingredient = True
    need_measurement = True
    need_amount = True

    for line in split_text:
        for note in Note_Words:
            if note in line.lower():
                line = line.replace(".", "")
                split_line = line.split()
                for i in CurrentBar:
                    if i.name in line.lower():
                        ingredient = i.name
                for word in split_line:
                    if word.lower() in CurrentBar and need_ingredient:
                        ingredient = word.lower()
                        need_ingredient = False
                    if word.lower() in Measurements and need_measurement:
                        measurement = word.lower()
                        need_measurement = False
                    if check_number(word) and need_amount:
                        amount = word
                        need_amount = False
                if ingredient:
                    ingredient = Ingredient(amount, measurement, ingredient, Type.MAIN, note)
                    notes.append(ingredient)
                    ingredient = ""
    return notes

def find_garnishes(text):
    garnishes = []
    split_text = re.split(r"\n|\. ", text)
    ingredient = ""
    measurement = ""
    amount = ""

    for line in split_text:
        if "garnish" in line.lower():
            line = line.replace(".", "")
            split_line = line.split()
            for word in split_line:
                if word.lower() in CurrentBar:
                    ingredient = word.lower()
                if word.lower() in Measurements:
                    measurement = word.lower()
                if check_number(word):
                    amount = word
            if ingredient:
                ingredient = Ingredient(amount, measurement, ingredient, Type.GARNISH)
                garnishes.append(ingredient)
    return garnishes

def combine_sections(divided_text):
    print("Which sections to combine?")
    sections = list(map(int, re.split(', |,| ', input('> '))))
    if len(sections) < 2:
        print("Requires at least 2 sections to combine.")
        return divided_text
    
    to_combine = []
    for section in sections:
        to_combine.append(divided_text[section])
    for text in to_combine:
        divided_text.remove(text)

    new_text = "\n".join(to_combine)
    divided_text.append(new_text)

    return divided_text

def delete_sections(divided_text):
    print("Which section(s) to delete?")
    sections = list(map(int, re.split(', |,| ', input('> '))))
    sections.sort(reverse=True)
    
    for section in sections:
        divided_text.pop(int(section))

    return divided_text

def swap_sections(divided_text):
    print("Which 2 sections to swap?")
    sections = list(map(int, re.split(', |,| ', input('> '))))
    if len(sections) != 2:
        print("Requires 2 sections to swap.")
        return divided_text
    
    divided_text[sections[0]], divided_text[sections[1]] = divided_text[sections[1]], divided_text[sections[0]]

    return divided_text

def move_section(divided_text):
    print("Which section to move?")
    section = int(input('> '))

    print("Which location to put section %i?" % section)
    index = int(input('> '))

    while index != section:
        if index < section:
            divided_text[section], divided_text[section-1] = divided_text[section-1], divided_text[section]
            section = section - 1
        else:
            divided_text[section], divided_text[section+1] = divided_text[section+1], divided_text[section]
            section = section + 1

    return divided_text

def add_section(divided_text):
    text = edit_text("")
    if text:
        divided_text.append(text)
    return divided_text

def change_pack(current_pack):
    print("What pack do you want to change to?")
    for number,pack in enumerate(Pack):
        print("%i) %s" % (number, pack.pack.capitalize()))
    selection = int(input("> "))

    if(selection >= len(Pack)):
        print("Choose a valid pack.")
        return current_pack
    for number, pack in enumerate(Pack):
        if number == selection:
            return pack

def change_glass(current_glass):
    print("What glass do you want to change to?")
    for number,glass in enumerate(Glass):
        print("%i) %s" % (number, glass.value.capitalize()))
    selection = int(input("> "))

    if(selection >= len(Glass)):
        print("Choose a valid glass.")
        return current_glass
    for number, glass in enumerate(Glass):
        if number == selection:
            return glass

def find_pack(labels, text_content):
    labels = [label.lower() for label in labels]
    possible_packs = []

    if "breakfast" in labels or "lunch" in labels:
        possible_packs.append(Pack.BRUNCH)

    for pack in Pack:
        if pack.pack.lower() in labels:
            possible_packs.append(pack)
    if possible_packs:
        possible_packs.sort(key=lambda item: item.importance)
        return possible_packs[0]

    divided_text = text_content.split()
    for pack in Pack:
        if pack.pack.lower() in divided_text:
            possible_packs.append(pack)
    if possible_packs:
        possible_packs.sort(key=lambda item: item.importance)
        return possible_packs[0]

    return Pack.MYDRINKS

def find_glass(labels, text_content):
    new_glass = Glass.NONE

    if "Tiki" in labels:
        new_glass = random.choice([Glass.TIKI1, Glass.TIKI2])

    for glass in Glass:
        if glass.value.lower() in text_content.lower():
            return glass

    return new_glass

def create_recipe_from_section(title, labels, divided_text):
    print("Which section(s) to use for the new recipe?")
    sections = list(map(int, re.split(', |,| ', input('> '))))

    new_recipe = ""
    for section in sections:
        new_recipe = new_recipe+divided_text[section]+"\n\n"

    new_recipe = new_recipe[:-2]

    print("What is the new recipes title?")
    new_title = input('> ')

    print("Use the current recipes labels? (y/n)")
    use_old_labels = input('> ')
    if use_old_labels.lower() != 'y':
        labels = re.split(', |,| ', edit_text(",".join(labels)))

    recipe = process_text_content(new_title, labels, new_recipe)
    Recipes.append(recipe)

    return divided_text

def find_flavors(ingredients):
    all_flavors = []
    flavor1 = "none"
    flavor2 = "none"

    for ingredient in ingredients:
        bottle = CurrentBar.get_bottle(ingredient.name)
        all_flavors.extend(bottle.flavors)
    all_flavors = list(filter(lambda flavor: flavor.lower() != "none", all_flavors))
    if len(all_flavors) > 0:
        flavor1 = max(set(all_flavors), key = all_flavors.count)
        all_flavors = list(filter(lambda flavor: flavor.lower() != flavor1, all_flavors))
    if len(all_flavors) > 0:
        flavor2 = max(set(all_flavors), key = all_flavors.count)

    return flavor1, flavor2

def edit_flavors(flavors):
    print("Current flavors are %s." % ", ".join(map(lambda flavor: flavor.capitalize(), flavors)))
    print("What flavors do you want?")
    for index, flavor in enumerate(Flavors):
        print(f"{index}) {flavor.capitalize()}")
    new_flavors_index = input("> ").split()

    if len(new_flavors_index) != 2:
        logger.error("Can only accept 2 flavors")
        return flavors

    if new_flavors_index[0].isdigit() and new_flavors_index[1].isdigit():
        flavor1_index = int(new_flavors_index[0])
        flavor2_index = int(new_flavors_index[1])
        if flavor1_index < len(Flavors) and flavor2_index < len(Flavors):
            return Flavors[flavor1_index], Flavors[flavor2_index]

    logger.error("There was an error setting new flavors.")
    return flavors

def process_text_content(title, labels, text_content):
    divided_text = text_content.split('\n\n')
    if len(divided_text) > 4 and divided_text[3] == "---":
        print(color_text('Found two recipes for "%s". Want to split them? (y/n)' % title, Style.BLUE))
        split = input('> ')
        if split.lower() == 'y' or split.lower() == 'yes':
            recipe = process_text_content(title, labels, "\n\n".join(divided_text[4:]))
            Recipes.append(recipe)

            divided_text = divided_text[0:3]
    first_correct = True
    contains_garnish = False
    found_notes = False
    ingredients_valid = False
    need_flavors = True
    ingredients = []
    flavors = []

    pack = find_pack(labels, text_content)
    glass = find_glass(labels, text_content)

    while True:
        if first_correct and len(divided_text) == 3:
            ingredients = []
            for ingredient in divided_text[0].split("\n"):
                ingredient = divide_ingredient(ingredient, first_correct)
                ingredients.append(ingredient)
                if ingredient.ingredient_type == Type.GARNISH:
                    contains_garnish = True
                if ingredient.notes != "none":
                    found_notes = True
            if not found_notes:
                notes = find_notes(divided_text[1])
                for note in notes:
                    ingredients.append(note)
                    divided_text[0] += "\n"
                    divided_text[0] += note.print()
                found_notes = True
            if not contains_garnish:
                garnishes = find_garnishes(divided_text[1])
                for garnish in garnishes:
                    ingredients.append(garnish)
                    divided_text[0] += "\n"
                    divided_text[0] += garnish.print()
                contains_garnish = True
            first_correct = False

        if len(divided_text) == 3:
            ingredients_valid = True
            for ingredient in ingredients:
                if not ingredient.validate():
                    ingredients_valid = False
            if need_flavors and ingredients_valid:
                    flavors = find_flavors(ingredients)

        print('=============================- %s -=============================' % title)
        print("Pack: %s" % pack.pack)
        print("Flavors: %s" % ", ".join(map(lambda flavor: flavor.capitalize(), flavors)))
        print("Old Labels: %s" % ", ".join(labels))
        print("Glass: %s\n" % glass.value.capitalize())
        if len(divided_text) == 3:
            print(Style.GREEN + '-----0 Ingredients 0-----')

            for ingredient in ingredients:
                print(ingredient.print_with_errors())

            print(Style.GREEN + '-----0 Ingredients 0-----\n')
            print('-----1 Instructions 1-----')
            print(divided_text[1])
            print('-----1 Instructions 1-----\n')
            print('-----2 Information 2-----')
            print(divided_text[2])
            print('-----2 Information 2-----\n' + Style.RESET)
        else:
            for number, text in enumerate(divided_text):
                print('-----%i-----' % number)
                print("%s" % text)
                print('-----%i-----\n' % number)
        print('=============================- %s -=============================' % title)
        print('\nRequires sections for ingredients, instructions, and source/information in that order.')
        print('What to do with this text for recipe "' + title + '"?')
        print('Type number to modify that section')
        print('(C)ombine sections')
        print('(D)elete sections')
        print('S(W)ap sections')
        print('(M)ove section')
        print('(A)dd section')
        print('Create (N)ew recipe from sections')
        print('Modify (T)itle')
        print('Modify (P)ack')
        print('Modify (F)lavors')
        print('Modify (I)ngredients')
        print('Modify (G)lass')
        print('(S)ave and fix any red ingredients')
        print('(Q)uit without saving current recipe')
        selection = input('> ')

        if selection.lower() == "q":
            exit()

        try:
            if selection.lower() == "c":
                divided_text = combine_sections(divided_text)
            elif selection.lower() == "d":
                divided_text = delete_sections(divided_text)
            elif selection.lower() == "w":
                divided_text = swap_sections(divided_text)
                first_correct = True
                contains_garnish = False
            elif selection.lower() == "m":
                divided_text = move_section(divided_text)
                first_correct = True
                contains_garnish = False
            elif selection.lower() == "a":
                divided_text = add_section(divided_text)
            elif selection.lower() == "n":
                divided_text = create_recipe_from_section(title, labels, divided_text)
            elif selection.lower() == "t":
                title = edit_text(title)
            elif selection.lower() == "p":
                pack = change_pack(pack)
            elif selection.lower() == "f":
                need_flavors = False
                flavors = edit_flavors(flavors)
            elif selection.lower() == "i":
                if(len(divided_text) != 3):
                    print("Must only contain 3 sections: ingredients, instructions, and source/information")
                else:
                    ingredients = process_ingredients(ingredients)
                    divided_text[0] = "\n".join(list(map(lambda ingredient: ingredient.print(), ingredients)))
            elif selection.lower() == "g":
                glass = change_glass(glass)
            elif selection.lower() == "s":
                if len(divided_text) != 3:
                    print("Not finished creating sections for ingredients, instructions, and source/information")
                else:
                    if not ingredients_valid:
                        ingredients = process_ingredients(ingredients)
                        divided_text[0] = "\n".join(list(map(lambda ingredient: ingredient.print(), ingredients)))
                    else:
                        return Recipe(title, ingredients, divided_text[1], divided_text[2], labels, pack, glass, flavors)
            elif selection.isnumeric():
                index = int(selection)
                if(index >= len(divided_text)):
                    print("Selection must be valid section.")
                divided_text[index] = edit_text(divided_text[index])
                if index == 0:
                    first_correct = True
            else:
                print("Invalid command")
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logger.error("Error trying to process request.")
            logger.error(e)
            logger.error("".join(traceback.format_tb(exc_traceback)))

def read_in_file(file_name):
    title = ""
    text_content = ""
    labels = []

    with codecs.open(file_name, encoding='utf-8') as json_file:
        data = json.load(json_file)
        
        if 'labels' in data:
            for label in data['labels']:
                labels.append(label['name'])
            if 'Drinks' in labels and data['color'] in ["BROWN", "RED"]:
                if 'title' in data:
                    title = data['title']
                if 'textContent' in data:
                    text_content = data['textContent']
                    text_content = text_content.replace(u'\u00e7', 'c').replace(u'\u00e8', 'e')
                recipe = process_text_content(title, labels, text_content)
                json_file.close()
                return recipe
        json_file.close()
    return None

def read_in_ingredient(file_name):
    name = ""
    flavors = []

    with codecs.open(file_name, encoding='utf-8') as json_file:
        data = json.load(json_file)
        
        if 'flavors' in data:
            for flavor in data['flavors']:
                if flavor in Flavors:
                    flavors.append(flavor)
        if 'name' in data:
            name = data['name']
        json_file.close()
    if name:
        return Bottle(name, flavors)
    return None

Recipes = RecipeBox("Recipes")
ingredients = []

if not os.path.exists("Finished"):
    os.makedirs("Finished")

if os.path.exists("Ingredients"):
    ingredient_files = [pos_json for pos_json in os.listdir(os.getcwd()+"/Ingredients") if pos_json.endswith('.json')]
    for file_name in ingredient_files:
        try:
            bottle = read_in_ingredient("Ingredients/" + file_name)
            if bottle is not None:
                ingredients.append(bottle)
        except:
            print(f"Error reading in {file_name}")
else:
    os.makedirs("Ingredients")

CurrentBar = Bar(ingredients)

json_files = [pos_json for pos_json in os.listdir(os.getcwd()) if pos_json.endswith('.json')]

times = []
avg_time = 0
est_time = 0
num_files = len(json_files)

for file_name in json_files:
    start_time = time.time()
    try:
        recipe = read_in_file(file_name)
        if recipe is not None:
            Recipes.append(recipe)
        os.replace(file_name, "Finished/" + file_name)
        
        end_time = time.time()
        num_files = num_files-1
        print("%s took %.3f seconds" % (recipe.title, end_time-start_time))
        times.append(end_time-start_time)
        avg_time = sum(times)/len(times)
        print("Average time: %.3f seconds" % (avg_time))
        print("%i files left" % num_files)
        est_time = datetime.timedelta(seconds=(avg_time * num_files))
        print("Estimated time to complete: %i days, %i hours, %i minutes, %i seconds" % convert_timedelta(est_time))

        selection = input("Press enter to go to start next recipe")
        if selection.lower() == "q":
            exit()
    except SystemExit as e:
        print("Shutting down program")
        sys.exit()
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logger.error('Error trying to read in a recipe from file "%s"' % file_name)
        logger.error(e)
        logger.error("".join(traceback.format_tb(exc_traceback)))

print(Recipes)