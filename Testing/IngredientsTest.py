import csv

Ingredients = ["gin", "rum", "whiskey", "bourbon", "sweet vermouth"]

# with open('Ingredients.txt', 'w') as filehandle:
#     json.dump(Ingredients, filehandle)
#     filehandle.close()

# with open('Ingredients.txt', 'r') as filehandle:
#     Ingredient = json.load(filehandle)
#     filehandle.close()

print(Ingredients)

with open('Ingredients.txt', 'w', newline='') as myfile:
    wr = csv.writer(myfile)
    wr.writerow(Ingredients)
    myfile.close()

with open('Ingredients.txt', 'r') as myfile:
    r = csv.reader(myfile)
    Ingredients = list(r)
    Ingredients = [val for sublist in Ingredients for val in sublist]
    myfile.close()

print(Ingredients)