import codecs
import json
import sqlite3
import os
import traceback
from collections import Counter

categories = set()
flavors = set()
ingredients = set()
glasses = set()
units = set()
types = set()

def add_ingredient_from_file(file_name, cursor):
    name = "none"
    dictionary_flavors = []

    with codecs.open(file_name, encoding='utf-8') as ingredient_file:
        data = json.load(ingredient_file)
        if 'name' in data:
            name = data['name']
        else:
            print("%s does not have a name." % ingredient_file.name)

        if 'flavors' in data:
            dictionary_flavors = Counter(data['flavors'])
        else:
            print("%s does not have flavors." % ingredient_file.name)
    
    if name != "none" and name not in ingredients:
        ingredients.add(name)
        cursor.execute("INSERT INTO ingredient (name) VALUES (?);", [name])
        ingredient_id = cursor.lastrowid

        for flavor, amount in dictionary_flavors.items():
            if flavor not in flavors:
                # print("Should add %s into database" % flavor)
                cursor.execute("INSERT INTO flavor (name) VALUES (?)", [flavor])
                flavors.add(flavor)
            cursor.execute("SELECT id FROM flavor WHERE name=?", [flavor])
            flavor_id = cursor.fetchone()[0]
            cursor.execute("""INSERT INTO ingredient_flavor (ingredient_id, flavor_id, amount) 
                VALUES ('%i', '%i', '%i')""" % (ingredient_id, flavor_id, amount))

def add_recipe_from_file(file_name, cursor):
    #title, category, flavors, glass, recipe_ingredients, instructions, information):
    title = "none"
    instructions = "none"
    information = "none"
    category = "none"
    glass = "none"
    rflavors = set()
    ingredients = None

    with codecs.open(file_name, encoding='utf-8') as recipe_file:
        data = json.load(recipe_file)
        if 'title' in data:
            title = data['title']
        else:
            print("%s does not have a title." % recipe_file.name)

        if 'pack' in data:
            category = data['pack']
        else:
            print("%s does not have a pack/category." % recipe_file.name)

        if 'glass' in data:
            glass = data['glass']
        else:
            print("%s does not have a glass." % recipe_file.name)

        if 'instructions' in data:
            instructions = data['instructions']
        else:
            print("%s does not have a instructions." % recipe_file.name)

        if 'information' in data:
            information = data['information']
        else:
            print("%s does not have a information." % recipe_file.name)

        if 'flavors' in data:
            rflavors = set(data['flavors'])
        else:
            print("%s does not have flavors." % recipe_file.name)

        if 'ingredients' in data:
            ingredients = data['ingredients']
        else:
            print("%s does not have ingredients." % recipe_file.name)
    
    if title != "none":
        if glass not in glasses:
            cursor.execute("INSERT INTO glass (name) VALUES (?);", [glass])
            glasses.add(glass)
        cursor.execute("SELECT id FROM glass WHERE name=?", [glass])
        glass_id = cursor.fetchone()[0]
        if category not in categories:
            cursor.execute("INSERT INTO category (name) VALUES (?);", [category])
            categories.add(category)
        cursor.execute("SELECT id FROM category WHERE name=?", [category])
        category_id = cursor.fetchone()[0]

        cursor.execute("INSERT INTO recipe (title, category, glass, instructions, information) VALUES (?,?,?,?,?);", 
            [title, category_id, glass_id, instructions, information])
        recipe_id = cursor.lastrowid

        for flavor in rflavors:
            if flavor not in flavors:
                # print("Should add %s into database" % flavor)
                cursor.execute("INSERT INTO flavor (name) VALUES (?)", [flavor])
                flavors.add(flavor)
            cursor.execute("SELECT id FROM flavor WHERE name=?", [flavor])
            flavor_id = cursor.fetchone()[0]
            cursor.execute("""INSERT INTO recipe_flavor (recipe_id, flavor_id) 
                VALUES (?,?)""", [recipe_id, flavor_id])

        if ingredients:
            for ingredient in ingredients:
                name = ""
                amount = 0
                unit = ""
                itype = ""
                notes = ""
                ingredient_id = -1
                unit_id = -1
                type_id = -1

                if 'ingredient' in ingredient:
                    name = ingredient['ingredient']

                    cursor.execute("SELECT id FROM ingredient WHERE name=?", [name])
                    ingredient_id = cursor.fetchone()[0]
                else:
                    print("%s does not have ingredient name for an ingredient" % (recipe_file.name))

                if 'amount' in ingredient:
                    amount = ingredient['amount']
                else:
                    print("%s does not have amount for ingredient %s." % (recipe_file.name, name))

                if 'measurement' in ingredient:
                    unit = ingredient['measurement']
                    
                    if unit not in units:
                        units.add(unit)
                        cursor.execute("INSERT INTO unit (name) VALUES (?)", [unit])
                    cursor.execute("SELECT id FROM unit WHERE name=?", [unit])
                    unit_id = cursor.fetchone()[0]
                else:
                    print("%s does not have measurement for ingredient %s." % (recipe_file.name, name))

                if 'type' in ingredient:
                    itype = ingredient['type']

                    if itype not in types:
                        types.add(itype)
                        cursor.execute("INSERT INTO type (name) VALUES (?)", [itype])
                    cursor.execute("SELECT id FROM type WHERE name=?", [itype])
                    type_id = cursor.fetchone()[0]
                else:
                    print("%s does not have itype for ingredient %s." % (recipe_file.name, name))

                if 'notes' in ingredient:
                    notes = ingredient['notes']
                    if notes == 'none':
                        notes = ""
                else:
                    pass#print("%s does not have notes for ingredient %s." % (recipe_file.name, name))

                if ingredient_id != -1 or unit_id != -1 or type_id != -1:
                    cursor.execute("""INSERT INTO recipe_ingredient (ingredient, amount, unit, type, notes) 
                        VALUES (?,?,?,?,?)""", [ingredient_id,amount,unit_id,type_id,notes])
                    recipe_ingredient_id = cursor.lastrowid

                    cursor.execute("""INSERT INTO recipe_recipe_ingredient (recipe_id, recipe_ingredient_id) 
                        VALUES (?,?)""", [recipe_id, recipe_ingredient_id])
                else:
                    print("Unable to add ingredient %s. ingredient_id = %i, unit_id = %i, type_id = %i" % (name, ingredient_id, unit_id, type_id))

try:
    connection = sqlite3.connect("cocktailbar.db")
    cursor = connection.cursor()

    #Ingredients 
    cursor.execute('''DROP TABLE IF EXISTS ingredient''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS ingredient (
        id INTEGER PRIMARY KEY, 
        name TEXT)''')
    connection.commit()

    cursor.execute('''DROP TABLE IF EXISTS ingredient_substitution''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS ingredient_substitution (
        ingredient_id INTEGER NOT NULL,
        substitution_id INTEGER NOT NULL,
        alias BOOLEAN NOT NULL DEFAULT 0,
        PRIMARY KEY (ingredient_id, substitution_id))''')

    cursor.execute('''DROP TABLE IF EXISTS flavor''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS flavor (id INTEGER PRIMARY KEY, name TEXT)''')
    connection.commit()

    cursor.execute('''DROP TABLE IF EXISTS ingredient_flavor''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS ingredient_flavor (
        ingredient_id INTEGER,
        flavor_id INTEGER,
        amount INTEGER,
        FOREIGN KEY (ingredient_id) REFERENCES ingredient(id), 
        FOREIGN KEY (flavor_id) REFERENCES flavor(id), 
        PRIMARY KEY (ingredient_id, flavor_id))''')
    connection.commit()

    # Recipes
    cursor.execute('''DROP TABLE IF EXISTS glass''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS glass (
        id INTEGER PRIMARY KEY, 
        name TEXT)''')
    connection.commit()

    cursor.execute('''DROP TABLE IF EXISTS category''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS category (
        id INTEGER PRIMARY KEY, 
        name TEXT)''')
    connection.commit()

    cursor.execute('''DROP TABLE IF EXISTS recipe''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS recipe (
        id INTEGER PRIMARY KEY, 
        title TEXT, 
        category INTEGER,
        glass INTEGER,
        instructions TEXT,
        information TEXT,
        FOREIGN KEY (glass) REFERENCES glass(id),
        FOREIGN KEY (category) REFERENCES category(id)
        )''')
    connection.commit()

    cursor.execute('''DROP TABLE IF EXISTS recipe_flavor''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS recipe_flavor (
        recipe_id INTEGER,
        flavor_id INTEGER,
        FOREIGN KEY (recipe_id) REFERENCES ingredient(id), 
        FOREIGN KEY (flavor_id) REFERENCES flavor(id), 
        PRIMARY KEY (recipe_id, flavor_id))''')
    connection.commit()

    #recipe_ingredient
    cursor.execute('''DROP TABLE IF EXISTS unit''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS unit (
        id INTEGER PRIMARY KEY, 
        name TEXT)''')
    connection.commit()

    cursor.execute('''DROP TABLE IF EXISTS type''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS type (
        id INTEGER PRIMARY KEY, 
        name TEXT)''')
    connection.commit()

    cursor.execute('''DROP TABLE IF EXISTS recipe_ingredient''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS recipe_ingredient (
        id INTEGER PRIMARY KEY, 
        ingredient INTEGER, 
        amount NUMBER,
        unit INTEGER,
        type INTEGER,
        notes TEXT,
        FOREIGN KEY (ingredient) REFERENCES ingredient(id),
        FOREIGN KEY (unit) REFERENCES unit(id),
        FOREIGN KEY (type) REFERENCES type(id)
        )''')
    connection.commit()

    cursor.execute('''DROP TABLE IF EXISTS recipe_recipe_ingredient''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS recipe_recipe_ingredient (
        recipe_id INTEGER,
        recipe_ingredient_id INTEGER,
        FOREIGN KEY (recipe_id) REFERENCES ingredient(id), 
        FOREIGN KEY (recipe_ingredient_id) REFERENCES recipe_ingredient(id), 
        PRIMARY KEY (recipe_id, recipe_ingredient_id))''')
    connection.commit()

    json_files = [pos_json for pos_json in os.listdir(os.getcwd()+"/Ingredients") if pos_json.endswith('.json')]
    for ingredient_file in json_files:
        add_ingredient_from_file("Ingredients/" + ingredient_file, cursor)
    connection.commit()

    json_files = [pos_json for pos_json in os.listdir(os.getcwd()+"/Recipes") if pos_json.endswith('.json')]
    for recipe_file in json_files:
        add_recipe_from_file("Recipes/" + recipe_file, cursor)
    connection.commit()

    connection.commit()
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