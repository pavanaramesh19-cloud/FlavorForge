"""
FlavorForge - Recipe Suggestor
Backend: Flask + Python
Data: CSV file (recipes.csv)

HOW IT WORKS
------------
1. User enters ingredients they have (comma-separated) in the browser.
2. Frontend (script.js) sends those ingredients to this backend via POST /suggest
3. This file loads recipes.csv, compares the user's ingredients to each
   recipe's ingredient list, and scores recipes by how many ingredients match.
4. The best-matching recipes are sent back as JSON and shown on the page.
"""

from flask import Flask, render_template, request, jsonify
import csv
import os

# templates/ and static/ live one level up from this file (in the project
# root, as siblings of backend/), so we point Flask at them explicitly.
BASE_DIR = os.path.dirname(__file__)
TEMPLATE_DIR = os.path.join(BASE_DIR, "..", "templates")
STATIC_DIR = os.path.join(BASE_DIR, "..", "static")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

# Path to the CSV file that stores all recipes
CSV_PATH = os.path.join(BASE_DIR, "recipes.csv")


def load_recipes():
    """Read recipes.csv into a list of dictionaries."""
    recipes = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Turn "carrot,broccoli,bell pepper" into ["carrot","broccoli","bell pepper"]
            row["ingredients_list"] = [
                ing.strip().lower() for ing in row["ingredients"].split(",")
            ]
            recipes.append(row)
    return recipes


def score_recipe(user_ingredients, recipe_ingredients):
    """
    Very simple matching score:
    (number of matching ingredients) / (total ingredients the recipe needs)
    Returns a value between 0 and 1 -- higher means a better match.
    """
    if not recipe_ingredients:
        return 0
    matches = set(user_ingredients) & set(recipe_ingredients)
    return len(matches) / len(recipe_ingredients)


@app.route("/")
def home():
    """Render the main page."""
    return render_template("index.html")


@app.route("/suggest", methods=["POST"])
def suggest():
    """
    Receives JSON like: { "ingredients": "egg, onion, tomato" }
    Returns the top matching recipes as JSON.
    """
    data = request.get_json()
    raw_ingredients = data.get("ingredients", "")

    # Clean up user input: "Egg, Onion , tomato" -> ["egg", "onion", "tomato"]
    user_ingredients = [
        item.strip().lower() for item in raw_ingredients.split(",") if item.strip()
    ]

    if not user_ingredients:
        return jsonify({"results": []})

    recipes = load_recipes()

    scored = []
    for recipe in recipes:
        score = score_recipe(user_ingredients, recipe["ingredients_list"])
        if score > 0:  # only keep recipes with at least one matching ingredient
            matched = sorted(set(user_ingredients) & set(recipe["ingredients_list"]))
            missing = sorted(set(recipe["ingredients_list"]) - set(user_ingredients))
            scored.append({
                "name": recipe["name"],
                "cuisine": recipe["cuisine"],
                "diet": recipe["diet"],
                "time_minutes": recipe["time_minutes"],
                "instructions": recipe["instructions"],
                "match_percent": round(score * 100),
                "matched_ingredients": matched,
                "missing_ingredients": missing,
            })

    # Sort recipes so the best matches appear first
    scored.sort(key=lambda r: r["match_percent"], reverse=True)

    return jsonify({"results": scored[:8]})  # send back top 8 matches


if __name__ == "__main__":
    # debug=True auto-reloads the server when you save changes (useful while building)
    app.run(debug=True)
