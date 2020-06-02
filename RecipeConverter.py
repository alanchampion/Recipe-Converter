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

Measurements = ["oz", ".oz", "oz.", "ounce", "ounces", "ml", ".ml", 
"ml.","tbsp", "tablespoon", "tablespoons", "tsp", "teaspoon", 
"teaspoons", "cup", "cups", "dash", "dashes", "drop", "drops", 
"pint",  "pints", "liter", "liters", "inch", "g", "gram", "grams", 
"twist", "peel", "wedge", "wedges", "wheel", "slice", 
"slices", "sprig", "leaf", "leaves", "pinch", "piece", "pod", 
"grated", "rinse", "bottle", "bottles", "barspoon", 
"barspoons", "piece", "pieces", "pound", "pounds", "lb", "lbs"]
Measurement_Convert = {
"oz": ["oz", ".oz", "oz.", "ounce", "ounces"],
"ml": ["ml", ".ml", "ml."],
"tbsp": ["tbsp", "tablespoon", "tablespoons"],
"tsp": ["tsp", "teaspoon", "teaspoons"],
"cup": ["cup", "cups"],
"dash": ["dash", "dashes"],
"drop": ["drop", "drops"],
"pint": ["pint", "pints"],
"liter": ["liter", "liters"],
"gram": ["gram", "grams", "g"],
"wedge": ["wedge", "wedges"],
"slice": ["slice", "slices"],
"leaf": ["leaf", "leaves"],
"bottle": ["bottle", "bottles"],
"barspoon": ["barspoon", "barspoons"],
"piece": ["pieces", "piece"],
"pound": ["pound", "pounds", "lb", "lbs"]
}
Filler_Words = ["of", "with", "fresh", "freshly", "1:1", "()", "/{/}", "[]"]
Garnish_Words = ["twist", "garnish", "peel", "wheel", "slice", "wedge", "sprig", "pod", "grated"]
Note_Words = ["top", "float", "rinse", "none"]

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

class Flavor(Enum):
    def __new__(cls, value, label):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.label = label
        return obj
    @classmethod
    def has_flavor(cls, value):
        return value.lower() in [flav.lower() for flav in cls._member_names_]
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

class Glass(Enum):
    ROCK = "rocks"
    COLLINS = "tom collins"
    COLLINS2 = "highball"
    COUPE = "coupe"
    TIKI1 = "tiki"
    TIKI2 = "tiki"
    PILSNER = "pilsner"
    PINT = "pint"
    MUG = "mug"
    IRISHCOFFEE = "irish coffee"
    CHAMPAGNE = "flute"
    COCKTAIL = "cocktail"
    NONE = "none"

class Bottle:
    def __init__(self, name, flavors):
        self.name = name.lower()
        self.flavors = flavors

    def __str__(self):
        return f"{self.name} {self.flavors}"

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
        for flavor in Flavor:
            print(f"{flavor.value}) {flavor.label.capitalize()}")
        num_flavors = input("> ").split()

        flavors = []
        for flavor in num_flavors:
            if not flavor.isdigit():
                return name
            flavors.append(Flavor(int(flavor)))

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
            print("The file %s already exists. Do you want to (r)eplace the file or create (n)ew?" % file)
            selection = input("> ")
            if selection.lower() == 'r':
                os.remove(file)
            else:
                name = input('New name: ')
                file = folder + '/' + name.replace(" ", "") + ".json"
        with codecs.open(file, encoding='utf-8', mode='w') as outfile:
            json.dump(data, outfile)

def color_text(text, style):
    return "%s%s%s" % (style, text, Style.RESET)

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
        number = "1"
        measurement = "oz"

    number = format_number(number)
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

    with tempfile.NamedTemporaryFile(suffix=".tmp", dir=os.getcwd(), delete=False) as tmp:
        tmp.write(data.encode('utf-8'))
        tmp.flush()
        call([EDITOR, "-n", tmp.name])

        tmp.seek(0)
        data = tmp.read().decode('utf-8').strip()
        tmp.close()
        os.unlink(tmp.name)

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
                        ingredient = i
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
    new_glass = Glass.ROCK

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
    ingredients = []

    pack = find_pack(labels, text_content)
    glass = find_glass(labels, text_content)

    while True:
        print('=============================- %s -=============================' % title)
        print("Pack: %s" % pack.pack)
        print("Old Labels: %s" % ", ".join(labels))
        print("Glass: %s\n" % glass.value.capitalize())
        if(len(divided_text) == 3):
            print(Style.GREEN + '-----0 Ingredients 0-----')

            if first_correct:
                ingredients = []
                for ingredient in divided_text[0].split("\n"):
                    ingredient = divide_ingredient(ingredient, first_correct)
                    ingredients.append(ingredient)
                    if ingredient.ingredient_type == Type.GARNISH:
                        contains_garnish = True
                    if ingredient.notes != "none":
                        found_notes = True
                    print(ingredient.print_with_errors())
                if not found_notes:
                    notes = find_notes(divided_text[1])
                    for note in notes:
                        print(note.print_with_errors())
                        ingredients.append(note)
                        divided_text[0] += "\n"
                        divided_text[0] += note.print()
                    found_notes = True
                if not contains_garnish:
                    garnishes = find_garnishes(divided_text[1])
                    for garnish in garnishes:
                        print(garnish.print_with_errors())
                        ingredients.append(garnish)
                        divided_text[0] += "\n"
                        divided_text[0] += garnish.print()
                    contains_garnish = True
            else:
                for ingredient in ingredients:
                    print(ingredient.print_with_errors())

            first_correct = False
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
        print('(S)wap sections')
        print('(M)ove section')
        print('(A)dd section')
        print('Create (N)ew recipe from sections')
        print('Modify (T)itle')
        print('Modify (P)ack')
        print('Modify (I)ngredients')
        print('Modify (G)lass')
        print('(F)inish and fix any red ingredients')
        print('(Q)uit without saving current recipe')
        selection = input('> ')

        if selection.lower() == "q":
            exit()

        try:
            if selection.lower() == "c":
                divided_text = combine_sections(divided_text)
            elif selection.lower() == "d":
                divided_text = delete_sections(divided_text)
            elif selection.lower() == "s":
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
            elif selection.lower() == "i":
                if(len(divided_text) != 3):
                    print("Must only contain 3 sections: ingredients, instructions, and source/information")
                else:
                    ingredients = process_ingredients(ingredients)
                    divided_text[0] = "\n".join(list(map(lambda ingredient: ingredient.print(), ingredients)))
            elif selection.lower() == "g":
                glass = change_glass(glass)
            elif selection.lower() == "f":
                if len(divided_text) != 3:
                    print("Not finished creating sections for ingredients, instructions, and source/information")
                else:
                    valid = True
                    for ingredient in ingredients:
                        if not ingredient.validate():
                            valid = False
                            break
                    if not valid:
                        ingredients = process_ingredients(ingredients)
                        divided_text[0] = "\n".join(list(map(lambda ingredient: ingredient.print(), ingredients)))
                    return Recipe(title, ingredients, divided_text[1], divided_text[2], labels, pack, glass)
            elif selection.isnumeric():
                index = int(selection)
                if(index >= len(divided_text)):
                    print("Selection must be valid section.")
                divided_text[index] = edit_text(divided_text[index])
                if index == 0:
                    first_correct = True
            else:
                print("Invalid command")
        except:
            logger.error("Error trying to process request.")

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
                if Flavor.has_flavor(flavor):
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
for file_name in json_files:
    try:
        recipe = read_in_file(file_name)
        if recipe is not None:
            Recipes.append(recipe)
        os.replace(file_name, "Finished/" + file_name)
    except SystemExit as e:
        print("Shutting down program")
        sys.exit()
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logger.error('Error trying to read in a recipe from file "%s"' % file_name)
        logger.error(e)
        logger.error("".join(traceback.format_tb(exc_traceback)))

print(Recipes)