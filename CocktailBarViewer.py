import sqlite3

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

try:
	connection = sqlite3.connect("cocktailbar.db")
	cursor = connection.cursor()
	