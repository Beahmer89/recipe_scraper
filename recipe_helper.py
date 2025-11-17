import recipe_scraper
import fake_db


def regenerate_recipe(recipe_id):
    recipe = fake_db.get_recipe_by_id(recipe_id)
    html = recipe_scraper.get_recipe(recipe["url"][0])
    recipe_data = recipe_scraper.create_recipe_page(html, recipe["url"][0])
    fake_db.update_recipe_by_id(recipe_id=recipe_id, recipe_html=recipe_data["recipe"])
