import streamlit

import fake_db
import recipe_scraper

streamlit.title("Recipe Converter")

# --- Initialize session state ---
# URL state
streamlit.session_state.setdefault("generate_url", None)

url = streamlit.text_input("Enter recipe URL:", key="generate_url")


def clear_url():
    # Safe way to reset the text input
    streamlit.session_state.generate_url = ""


left_column, _, right_column = streamlit.columns([2, 2, 2])
with left_column:
    if streamlit.button(
        "Generate Recipe", help="Generate Simple Recipe from Recipe URL", icon="✨"
    ):
        if not url:
            streamlit.error("Enter a URL Please")
            streamlit.stop()

        with streamlit.spinner("Grabbing Recipe...."):
            html = recipe_scraper.get_recipe(url)
            if not html:
                error_message = "Something went wrong, please check URL"
                streamlit.error(f"(＞﹏＜) {error_message} (＞﹏＜)")
                streamlit.stop()

            recipe_data = recipe_scraper.create_recipe_page(html, url)

            if not recipe_data:
                error_message = "Couldnt Find Recipe Elements"
                streamlit.error(f"(╥﹏╥) {error_message} (╥﹏╥)")
            else:
                fake_db.insert_recipe(recipe_data)
                streamlit.success("Recipe Generated!!!")

with right_column:
    streamlit.button("Clear URL", on_click=clear_url, icon="❌")
