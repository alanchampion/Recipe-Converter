-- Get a specific recipe from id
SELECT recipe.title, flavors.name, category.name, glass.name,
ingredients.name, ingredients.amount, ingredients.unit, ingredients.type,
ingredients.notes, recipe.instructions, recipe.information
FROM recipe
JOIN (
    SELECT recipe.rowid AS recipe_id, GROUP_CONCAT(flavor.name, ';') AS name FROM recipe
    JOIN recipe_flavor ON recipe.rowid = recipe_flavor.recipe_id
    JOIN flavor ON flavor.rowid = recipe_flavor.flavor_id
    WHERE recipe.rowid = 280
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
    WHERE recipe.rowid = 280
) AS ingredients ON recipe.rowid = ingredients.recipe_id
WHERE recipe.rowid = 280;

-- Get a specific recipe from id
SELECT recipe_title.title, GROUP_CONCAT(DISTINCT(flavor.name), ';'), category.name, glass.name,
ingredients.name, GROUP_CONCAT(DISTINCT(recipe_ingredient.amount)), ingredients.unit, ingredients.type,
ingredients.notes, recipe.instructions, recipe.information
FROM (
    SELECT * FROM recipe WHERE recipe.rowid = 280
) AS recipe
JOIN recipe_title ON recipe_title.recipe_id = recipe.rowid
JOIN recipe_flavor ON recipe_flavor.recipe_id = recipe.rowid
JOIN flavor on flavor.rowid = recipe_flavor.flavor_id
JOIN glass ON recipe.glass = glass.rowid
JOIN category ON recipe.category = category.rowid
JOIN recipe_recipe_ingredient ON recipe_recipe_ingredient.recipe_id = recipe.rowid
JOIN recipe_ingredient ON recipe_ingredient.rowid = recipe_recipe_ingredient.recipe_ingredient_id
JOIN (
    SELECT recipe.rowid AS recipe_id, GROUP_CONCAT(ingredient.name, ';') AS name, GROUP_CONCAT(unit.name, ';') AS unit,
        GROUP_CONCAT(recipe_ingredient.amount, ';') AS amount, GROUP_CONCAT(type.name, ';') AS type,
        GROUP_CONCAT(recipe_ingredient.notes, ';') AS notes FROM recipe
    JOIN recipe_recipe_ingredient ON recipe_recipe_ingredient.recipe_id = recipe.rowid
    JOIN recipe_ingredient ON recipe_ingredient.rowid = recipe_recipe_ingredient.recipe_ingredient_id
    JOIN ingredient ON ingredient.rowid = recipe_ingredient.ingredient
    JOIN unit ON unit.rowid = recipe_ingredient.unit
    JOIN type ON type.rowid = recipe_ingredient.type
    WHERE recipe.rowid = 280
) AS ingredients ON recipe.rowid = ingredients.recipe_id

-- Get recipes from ingredients
SELECT DISTINCT recipe.rowid, recipe.title
FROM (
SELECT DISTINCT recipe.rowid, recipe.title FROM recipe_ingredient
JOIN recipe_recipe_ingredient ON recipe_recipe_ingredient.recipe_ingredient_id = recipe_ingredient.rowid
JOIN recipe ON recipe.rowid = recipe_recipe_ingredient.recipe_id
WHERE ingredient = 238) as recipe, 
(
SELECT DISTINCT recipe.rowid, recipe.title FROM recipe_ingredient
JOIN recipe_recipe_ingredient ON recipe_recipe_ingredient.recipe_ingredient_id = recipe_ingredient.rowid
JOIN recipe ON recipe.rowid = recipe_recipe_ingredient.recipe_id
WHERE ingredient = 187) as recipe1
WHERE recipe.rowid = recipe1.rowid;

-- Get recipes from ingredients, more precise
SELECT DISTINCT recipe.rowid, recipe.title
FROM recipe
JOIN (SELECT DISTINCT recipe_recipe_ingredient.recipe_id as recipe_id, COUNT(DISTINCT(ingredient.rowid)) as ingredient_count 
    FROM recipe_recipe_ingredient
    JOIN recipe_ingredient ON recipe_ingredient.rowid = recipe_recipe_ingredient.recipe_ingredient_id
    JOIN ingredient ON ingredient.rowid = recipe_ingredient.ingredient
    WHERE recipe_ingredient.ingredient = 187 OR recipe_ingredient.ingredient = 238
    GROUP BY recipe_recipe_ingredient.recipe_id HAVING COUNT(*) > 1
) as ingredients ON ingredients.recipe_id = recipe.rowid
WHERE ingredients.ingredient_count = 2;

SELECT DISTINCT recipe.rowid, recipe.title FROM recipe_ingredient
JOIN recipe_recipe_ingredient ON recipe_recipe_ingredient.recipe_ingredient_id = recipe_ingredient.rowid
JOIN recipe ON recipe.rowid = recipe_recipe_ingredient.recipe_id
WHERE ingredient = 187

SELECT recipe.rowid, recipe.title, flavors.name, category.name, glass.name,
ingredients.name, ingredients.amount, ingredients.unit, ingredients.type,
ingredients.notes, recipe.instructions, recipe.information
FROM recipe
JOIN (
    SELECT recipe.rowid AS recipe_id, GROUP_CONCAT(flavor.name, ';') AS name FROM recipe
    JOIN recipe_flavor ON recipe.rowid = recipe_flavor.recipe_id
    JOIN flavor ON flavor.rowid = recipe_flavor.flavor_id
    GROUP BY recipe.rowid
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
    GROUP BY recipe.rowid
) AS ingredients ON recipe.rowid = ingredients.recipe_id;

SELECT recipe.rowid, recipe.title, category.name, GROUP_CONCAT(flavor.name, ';'), 
glass.name, recipe.instructions, recipe.information
FROM recipe
JOIN recipe_flavor ON recipe.rowid = recipe_flavor.recipe_id
JOIN flavor ON flavor.rowid = recipe_flavor.flavor_id
JOIN glass ON recipe.glass = glass.rowid
JOIN category ON recipe.category = category.rowid
WHERE recipe.rowid = 280

SELECT recipe_recipe_ingredient.recipe_id, recipe_ingredient.amount, unit.name, 
ingredient.name, type.name, recipe_ingredient.notes FROM recipe_recipe_ingredient
JOIN recipe_ingredient ON recipe_ingredient.rowid = recipe_recipe_ingredient.recipe_ingredient_id
JOIN ingredient ON ingredient.rowid = recipe_ingredient.ingredient
JOIN unit ON unit.rowid = recipe_ingredient.unit
JOIN type ON type.rowid = recipe_ingredient.type
WHERE recipe_recipe_ingredient.recipe_id = 280;
