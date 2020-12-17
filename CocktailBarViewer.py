import sqlite3
import traceback
from enum import Enum

class Ingredient:
	def __init__(self, name):
		self.name = name

class Recipe_Ingredient:
	def __init__(self, ingredient, amount, unit, itype, notes):
		self.ingredient = ingredient
		self.amount = amount
		self.unit = unit
		units.add(unit)
		self.type = itype
		self.notes = notes

class Recipe:
	def __init__(self, title, category, flavors, glass, recipe_ingredients, instructions, information):
		self.title = title
		self.category = category.lower()
		categories.add(self.category)
		self.flavors = list(map(lambda x: x.lower(), flavors))
		flavors.update(self.flavors)
		self.glass = glass.lower()
		glasses.add(self.glass)
		self.recipe_ingredients = recipe_ingredients
		self.instructions = instructions
		self.information = information

class Method(Enum):
	QUIT = "q"
	NONE = ""

def main(cursor):
	print('============================================================')
	print("What do you want to do?")
	print("(Q)uit")

	selection = input('> ')[0].lower()

	try:
		return Method(selection)
	except ValueError as error:
		print("Invalid option")
		return Method.NONE

try:
	connection = sqlite3.connect("cocktailbar.db")
	cursor = connection.cursor()

	while(True):
		method = main(cursor)
		if method == Method.QUIT:
			print('============================================================')
			break
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