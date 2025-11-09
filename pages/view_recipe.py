import streamlit
import fake_db

params = streamlit.query_params
recipe_id = params.get("recipe_id")


if recipe_id:
    content = fake_db.get_recipe_by_id(recipe_id)
    recipe_html = content["recipe_html"][0]

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
else:
    streamlit.error("(╥﹏╥) Recipe not found (╥﹏╥)")
