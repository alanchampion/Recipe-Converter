import sqlite3
import traceback
import re
from enum import Enum

class Ingredient:
    def __init__(self, name):
        self.name = name

class Recipe_Ingredient:
    def __init__(self, name, amount, unit, itype, notes):
        self.name = name
        self.amount = amount
        self.unit = unit
        self.type = itype
        self.notes = notes

    def __str__(self):
        string = ""
        if self.type and self.type.lower() != "main":
            string += self.type + ": "
        if self.amount:
            string += self.amount + " "
        if self.unit:
            string += self.unit + " "
        if self.name:
            string += self.name + " "
        if self.notes:
            string += "(" + self.notes + ")"
        return string

class Recipe:
    def __init__(self, title, category, flavors, glass, recipe_ingredients, instructions, information):
        self.title = title
        self.category = category.lower()
        self.flavors = list(map(lambda x: x.lower(), flavors))
        self.glass = glass.lower()
        self.recipe_ingredients = recipe_ingredients
        self.instructions = instructions
        self.information = information

    def __str__(self):
        string = "--------------------\n"
        string += self.title + "\n"
        string += "Category: " + self.category + "\n"
        string += "Flavors: " + ", ".join(self.flavors) + "\n"
        if self.glass.lower() != "none":
            string += "Glass: " + self.glass.capitalize() + "\n\n"
        for ingredient in self.recipe_ingredients:
            string += str(ingredient) + "\n"
        string += "\n" + self.instructions + "\n\n"
        string += self.information + "\n"
        string += "--------------------"
        return string

class Method(Enum):
    QUIT = "q"
    SEARCH = "s"
    TITLE_SEARCH = "t"
    INGREDIENT_SEARCH = "i"
    NONE = ""

def string_found(string1, string2):
    if re.search(r"\b" + re.escape(string1) + r"\b", string2):
        return True
    return False

def string_front_found(string1, string2):
    if re.search(r"^" + re.escape(string1) + r"\b", string2):
        return True
    return False

def show_recipe_from_id(cursor, id):
    cursor.execute("""SELECT recipe.title, flavors.name, category.name, glass.name,
        ingredients.name, ingredients.amount, ingredients.unit, ingredients.type,
        ingredients.notes, recipe.instructions, recipe.information
        FROM (
            SELECT * FROM recipe WHERE recipe.rowid = ?
        ) AS recipe
        JOIN (
            SELECT recipe.rowid AS recipe_id, GROUP_CONCAT(flavor.name, ';') AS name FROM recipe
            JOIN recipe_flavor ON recipe.rowid = recipe_flavor.recipe_id
            JOIN flavor ON flavor.rowid = recipe_flavor.flavor_id
            WHERE recipe.rowid = ?
        ) AS flavors ON recipe.rowid = flavors.recipe_id
        JOIN glass ON recipe.glass = glass.rowid
        JOIN category ON recipe.category = category.rowid
        JOIN (
            SELECT recipe.rowid AS recipe_id, GROUP_CONCAT(ingredient.name, ';') AS name, GROUP_CONCAT(unit.name, ';') AS unit,
                GROUP_CONCAT(recipe_ingredient.amount, ';') AS amount, GROUP_CONCAT(type.name, ';') AS type,
                GROUP_CONCAT(recipe_ingredient.notes, ';') AS notes FROM recipe
            JOIN recipe_recipe_ingredient ON recipe_recipe_ingredient.recipe_id = recipe.rowid
            JOIN recipe_ingredient ON recipe_ingredient.rowid = recipe_recipe_ingredient.recipe_ingredient_id
            JOIN ingredient ON ingredient.rowid = recipe_ingredient.ingredient
            JOIN unit ON unit.rowid = recipe_ingredient.unit
            JOIN type ON type.rowid = recipe_ingredient.type
            WHERE recipe.rowid = ?
        ) AS ingredients ON recipe.rowid = ingredients.recipe_id;""", [id, id, id]);
    row = cursor.fetchone()

    title = row[0]
    flavors = row[1].split(';')
    category = row[2]
    glass = row[3]
    ingredient_names = row[4].split(';')
    ingredient_amounts = row[5].split(';')
    ingredient_units = row[6].split(';')
    ingredient_types = row[7].split(';')
    ingredient_notes = row[8].split(';')
    instructions = row[9]
    information = row[10]

    ingredients = []
    for i, name in enumerate(ingredient_names):
        ingredients.append(Recipe_Ingredient(name, ingredient_amounts[i], ingredient_units[i], ingredient_types[i], ingredient_notes[i]))
    recipe = Recipe(title, category, flavors, glass, ingredients, instructions, information)

    print(recipe)

def search_all(cursor):
    print("Not implemented")

def print_recipes_from_rowid_title(cursor, rowid_title):
    result_ids = []

    if len(rowid_title) == 0:
        print("No results found")
        return
    if len(rowid_title) == 1:
        show_recipe_from_id(cursor, rowid_title[0][0])
        return

    for index, row in enumerate(rowid_title):
        print("(%i) %s" % (index, row[1]))
        result_ids.append(row)

    print("Which recipe(s) do you want to show results? Insert 'c' for cancel")
    search = input("> ")
    print()

    if search[0].lower() == 'c':
        return

    numbers = list(map(int, re.findall(r'\d+', search)))
    if len(numbers) == 0:
        print("Not a valid selection")
        return
    else:
        for index in numbers:
            if index >= len(result_ids) or index < 0:
                print("%i was not a valid selection" % index)
            else:
                show_recipe_from_id(cursor, result_ids[index][0])

def title_search(cursor):
    print("What recipe title do you want to search for?")
    search = input("> ")
    print()

    front_results = []
    middle_results = []
    back_results = []
    results = []
    all_rows = cursor.execute("""SELECT rowid, title FROM recipe""")
    for row in all_rows:
        if search.lower() == row[1].lower():
            front_results.append(row)
        elif string_front_found(search.lower(), row[1].lower()):
            middle_results.append(row)
        elif string_found(search.lower(), row[1].lower()):
            back_results.append(row)

    row_sort = lambda row : row[1]
    front_results.sort(key=row_sort)
    middle_results.sort(key=row_sort)
    back_results.sort(key=row_sort)
    results.extend(front_results)
    results.extend(middle_results)
    results.extend(back_results)

    print_recipes_from_rowid_title(cursor, results)

def get_recipes_from_ingredient_ids(cursor, ingredient_ids):
    if len(ingredient_ids) == 0:
        print("No ingredients specified")
        return
    elif len(ingredient_ids) == 1:
        all_rows = cursor.execute("""SELECT DISTINCT recipe.rowid, recipe.title FROM recipe_ingredient
            JOIN recipe_recipe_ingredient ON recipe_recipe_ingredient.recipe_ingredient_id = recipe_ingredient.rowid
            JOIN recipe ON recipe.rowid = recipe_recipe_ingredient.recipe_id
            WHERE ingredient = ?""", ingredient_ids)
        results = []
        for row in all_rows:
            results.append(row)
        print_recipes_from_rowid_title(cursor, results)
        return
    else:
        where_statement = "recipe_ingredient.ingredient = ? OR " * len(ingredient_ids)
        where_statement = where_statement[:-3]
        ingredient_ids.append(len(ingredient_ids))
        query = """SELECT DISTINCT recipe.rowid, recipe.title
            FROM recipe
            JOIN (SELECT DISTINCT recipe_recipe_ingredient.recipe_id as recipe_id, COUNT(DISTINCT(ingredient.rowid)) as ingredient_count
                FROM recipe_recipe_ingredient
                JOIN recipe_ingredient ON recipe_ingredient.rowid = recipe_recipe_ingredient.recipe_ingredient_id
                JOIN ingredient ON ingredient.rowid = recipe_ingredient.ingredient WHERE """ + where_statement + """
                GROUP BY recipe_recipe_ingredient.recipe_id HAVING COUNT(*) > 1
            ) as ingredients ON ingredients.recipe_id = recipe.rowid
            WHERE ingredients.ingredient_count = ?;"""

        all_rows = cursor.execute(query, ingredient_ids)
        results = []
        for row in all_rows:
            results.append(row)
        print_recipes_from_rowid_title(cursor, results)

def ingredient_search(cursor):
    recipes = []

    print("What ingredient do you want to search for?")
    search = input("> ")
    print()

    front_results = []
    middle_results = []
    back_results = []
    results = []
    result_ids = []
    all_rows = cursor.execute("""SELECT rowid, name FROM ingredient""")
    for row in all_rows:
        if search.lower() == row[1].lower():
            front_results.append(row)
        elif string_front_found(search.lower(), row[1].lower()):
            middle_results.append(row)
        elif string_found(search.lower(), row[1].lower()):
            back_results.append(row)

    row_sort = lambda row : row[1]
    front_results.sort(key=row_sort)
    middle_results.sort(key=row_sort)
    back_results.sort(key=row_sort)
    results.extend(front_results)
    results.extend(middle_results)
    results.extend(back_results)

    if len(results) == 0:
        print("No results found")
        return
    if len(results) == 1:
        recipes = get_recipes_from_ingredient_ids(cursor, [results[0][0]])
        return

    for index, row in enumerate(results):
        print("(%i) %s" % (index, row[1]))
        result_ids.append(row)

    print("Which ingredient do you want to search on? Insert 'c' for cancel")
    search = input("> ")
    print()

    if search[0].lower() == 'c':
        return

    numbers = list(map(int, re.findall(r'\d+', search)))
    if len(numbers) == 0:
        print("Not a valid selection")
        return
    else:
        temp = []
        for index in numbers:
            if index >= len(result_ids) or index < 0:
                print("%i was not a valid selection. Ignoring" % index)
            else:
                temp.append(results[index][0])
        if len(temp) == 0:
            print("No valid ingredients selected")
            return
        get_recipes_from_ingredient_ids(cursor, temp)

def main():
    print("What do you want to do?")
    print("(S)earch")
    print("(T)itle Search")
    print("(I)ngredient Search")
    print("(Q)uit")
    selection = input('> ').lower()

    try:
        return Method(selection)
    except ValueError as error:
        print("Invalid option")
        return Method.NONE

try:
    connection = sqlite3.connect("cocktailbar.db")
    cursor = connection.cursor()

    while(True):
        print('============================================================')
        method = main()
        print()
        if method == Method.QUIT:
            print('============================================================')
            break
        elif method == Method.SEARCH:
            search_all(cursor)
        elif method == Method.TITLE_SEARCH:
            title_search(cursor)
        elif method == Method.INGREDIENT_SEARCH:
            ingredient_search(cursor)
        elif method == Method.NONE:
            pass
        else:
            print("How did you get here?")
        print('============================================================')
        print()

    cursor.close()
except sqlite3.Error as error:
    print("Error while connecting to sqlite: ", error)
    traceback.print_exc()
finally:
    if (connection):
        connection.close()
        print("The SQLite connection is closed")

# Get the ingredients
# SELECT ingredient.name, flavor.name, ingredient_flavor.amount FROM ingredient
#   JOIN ingredient_flavor ON ingredient.id = ingredient_flavor.ingredient_id
#   JOIN flavor ON flavor.id = ingredient_flavor.flavor_id;

# Get the recipes without ingredients
# SELECT recipe.title, GROUP_CONCAT(flavor.name) as flavors, category.name, glass.name, recipe.instructions, recipe.information
#   FROM recipe
#   JOIN recipe_flavor ON recipe.id = recipe_flavor.recipe_id
#   JOIN flavor ON flavor.id = recipe_flavor.flavor_id
#   JOIN glass ON recipe.glass = glass.id
#   JOIN category ON recipe.category = category.id
#   WHERE recipe.title = 'Old Fashioned';

# Get the full recipe, ingredients concatinated
# SELECT recipe.title, GROUP_CONCAT(DISTINCT flavors.name), category.name, glass.name,
#    GROUP_CONCAT(DISTINCT ingredients.ingredient), recipe.instructions, recipe.information
#    FROM (
#        SELECT * FROM recipe WHERE recipe.title = 'Old Fashioned'
#    ) AS recipe
#    JOIN (
#        SELECT recipe.id as recipe_id, flavor.name as name FROM recipe
#        JOIN recipe_flavor ON recipe.id = recipe_flavor.recipe_id
#        JOIN flavor ON flavor.id = recipe_flavor.flavor_id
#    ) AS flavors ON recipe.id = flavors.recipe_id
#    JOIN glass ON recipe.glass = glass.id
#    JOIN category ON recipe.category = category.id
#    JOIN (
#        SELECT recipe.id as recipe_id, type.name || ': ' || recipe_ingredient.amount ||
#        ' ' || unit.name || ' ' || ingredient.name || ' (' || recipe_ingredient.notes || ')' as ingredient FROM recipe
#        JOIN recipe_recipe_ingredient ON recipe_recipe_ingredient.recipe_id = recipe.id
#        JOIN recipe_ingredient on recipe_ingredient.id = recipe_recipe_ingredient.recipe_ingredient_id
#        JOIN ingredient on ingredient.id = recipe_ingredient.ingredient
#        JOIN unit on unit.id = recipe_ingredient.unit
#        JOIN type on type.id = recipe_ingredient.type
#        WHERE recipe.title = 'Old Fashioned'
#    ) AS ingredients ON recipe.id = ingredients.recipe_id

# Get the full recipe, ingredients seperate
# SELECT recipe.title, flavors.name, category.name, glass.name,
#     ingredients.name, ingredients.amount, ingredients.unit, ingredients.type,
#     ingredients.notes, recipe.instructions, recipe.information
#     FROM (
#         SELECT * FROM recipe WHERE recipe.title = 'Old Fashioned'
#     ) AS recipe
#     JOIN (
#         SELECT recipe.id as recipe_id, GROUP_CONCAT(flavor.name) as name FROM recipe
#         JOIN recipe_flavor ON recipe.id = recipe_flavor.recipe_id
#         JOIN flavor ON flavor.id = recipe_flavor.flavor_id
#         WHERE recipe.title = 'Old Fashioned'
#     ) AS flavors ON recipe.id = flavors.recipe_id
#     JOIN glass ON recipe.glass = glass.id
#     JOIN category ON recipe.category = category.id
#     JOIN (
#         SELECT recipe.id as recipe_id, GROUP_CONCAT(ingredient.name, ';') as name, GROUP_CONCAT(unit.name, ';') as unit,
#             GROUP_CONCAT(recipe_ingredient.amount, ';') as amount, GROUP_CONCAT(type.name, ';') as type,
#             GROUP_CONCAT(recipe_ingredient.notes, ';') as notes FROM recipe
#         JOIN recipe_recipe_ingredient ON recipe_recipe_ingredient.recipe_id = recipe.id
#         JOIN recipe_ingredient on recipe_ingredient.id = recipe_recipe_ingredient.recipe_ingredient_id
#         JOIN ingredient on ingredient.id = recipe_ingredient.ingredient
#         JOIN unit on unit.id = recipe_ingredient.unit
#         JOIN type on type.id = recipe_ingredient.type
#         WHERE recipe.title = 'Old Fashioned'
#     ) AS ingredients ON recipe.id = ingredients.recipe_id

# Get recipe's that include a specific ingredient
# SELECT recipe.id, recipe.title FROM ingredient
#     JOIN recipe_ingredient ON recipe_ingredient.ingredient = ingredient.id
#     JOIN recipe_recipe_ingredient ON recipe_recipe_ingredient.recipe_ingredient_id = recipe_ingredient.id
#     JOIN recipe ON recipe.id = recipe_recipe_ingredient.recipe_id
#     WHERE ingredient.name = 'bourbon';
