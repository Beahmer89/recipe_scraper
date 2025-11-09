import streamlit

import fake_db
import recipe_scraper

streamlit.title("Recipe Scraper")

url = streamlit.text_input("Enter recipe URL:")

if streamlit.button("Generate Recipe"):
    if not url:
        streamlit.error("Enter a URL Please")
        streamlit.stop()

    with streamlit.spinner("Grabbing Recipe...."):
        html = recipe_scraper.get_recipe(url)
        recipe_data = recipe_scraper.create_recipe_page(html, url)
        fake_db.insert_recipe(recipe_data)

        streamlit.success("Recipe Generated!!!")
