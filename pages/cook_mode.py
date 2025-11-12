import streamlit
import fake_db

params = streamlit.query_params
recipe_id = params.get("recipe_id")

_, center, _ = streamlit.columns([2, 2, 2])
with center:
    streamlit.title("Cook Mode")

# Got here from navbar
if not recipe_id:
    streamlit.error(
        "(╯°□°）╯︵ ┻━┻ Where’s the recipe?! Go pick one from View Recipes to enter Cook Mode"
    )
    _, center, _ = streamlit.columns([2, 2, 2])
    with center:
        streamlit.page_link(
            "pages/view_recipes.py",
            help="Pick a recipe from list to view in Cook Mode",
            label="View Recipes",
            icon="⬅️",
        )
    streamlit.stop()

# get recipe
content = fake_db.get_recipe_by_id(recipe_id)

if not len(content["recipe_html"]):
    streamlit.error(
        "(╥﹏╥) Recipe not found. Try viewing the recipe in Cook Mode Again (╥﹏╥)"
    )
    _, center, _ = streamlit.columns([2, 2, 2])
    with center:
        streamlit.page_link(
            "pages/view_recipes.py",
            help="Pick a recipe from list to view in Cook Mode",
            label="View Recipes",
            icon="⬅️",
        )
    streamlit.stop()

# Otherwise render the cooking screen
recipe_html = content["recipe_html"][0]

_, center_column, _ = streamlit.columns([2, 2, 2])
with center_column:
    streamlit.link_button(
        label="View Original Recipe",
        help="Support recipe owner or view original recipe",
        url=content["url"][0],
        icon="📝",
    )
# Wrap the recipe HTML in a styled container
styled_html = f"""
<html>
    <head>
        <style>
            body {{
                background-color: white;
                color: black;
                margin: 0;
                padding: 2rem;
                font-family: system-ui, sans-serif;
            }}
            .recipe-container {{
                max-width: 800px;
                margin: auto;
                background: white;
                border-radius: 12px;
                box-shadow: 0 0 12px rgba(0,0,0,0.1);
                padding: 2rem;
            }}
        </style>
    </head>
    <body>
        <div class="recipe-container">
            {recipe_html}
        </div>
    </body>
</html>
"""

# Render recipe taking full width
streamlit.components.v1.html(styled_html, height=1500, scrolling=True)

# Spacer before link
streamlit.markdown("<br><br>", unsafe_allow_html=True)

# Back link at bottom
streamlit.page_link("pages/view_recipes.py", label="← Back to list", icon="⬅️")
