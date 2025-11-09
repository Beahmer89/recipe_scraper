import streamlit
from streamlit_extras.card import card

import fake_db

streamlit.title("View Recipes")

streamlit.markdown(
    """
<style>
.recipe-previewer {
        background-color: white;
        color: #111;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        max-width: 800px;
        margin: 1rem auto;
}
.card-title {
    margin-top: -100px;
    text-align: center;
    font-weight: 600;
}
.button-container {
    text-align: right;   /* center the button under the title */
    margin-top:  5px;     /* space below title */
}
</style>
""",
    unsafe_allow_html=True,
)

# get all recipies from database or subset
content = fake_db.get_recipes()

# For tracking which recipe’s modal is open
if "modal_id" not in streamlit.session_state:
    streamlit.session_state.dialog_id = None

columns_per_row = 2
for i in range(0, len(content), columns_per_row):
    cols = streamlit.columns(columns_per_row)
    for col, recipe in zip(cols, content[i : i + columns_per_row]):
        with col:
            card(
                title="",
                text="",
                url=f"/view_recipe?recipe_id={recipe['id']}",  # Link to your view_recipe page
                image=recipe["image"],
            )
            streamlit.markdown(
                f"<div class='card-title'>{recipe['title']}</div>",
                unsafe_allow_html=True,
            )
            left, center, right = streamlit.columns([2, 2, 2])
            with center:
                streamlit.markdown(
                    "<div class='button-container'></div>", unsafe_allow_html=True
                )
                if streamlit.button(
                    "👀 Preview", key=f"preview_{recipe['id']}", type="primary"
                ):
                    streamlit.session_state.dialog_id = recipe["id"]


# --- Modal section show dialog if one is selected ---
if streamlit.session_state.dialog_id:
    selected = next(
        (r for r in content if r["id"] == streamlit.session_state.dialog_id), None
    )
    if selected:

        @streamlit.dialog("Preview")
        def show_preview():
            styled_html = f"""
            <body style="background-color:white; color:#111; font-family: Arial, sans-serif; padding: 1rem;">
            <div class='recipe-previewer'>
            {selected["html"]}
            </div>
            </body>
            """
            streamlit.components.v1.html(styled_html, height=300, scrolling=True)
            if streamlit.button("Close"):
                streamlit.session_state.dialog_id = None

        show_preview()
