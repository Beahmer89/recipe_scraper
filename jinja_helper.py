from jinja2 import Environment, FileSystemLoader


def create_simplified_recipe(
    title: str, ingredients: list, instructions: list, total_time: str
):
    # loading the environment
    env = Environment(loader=FileSystemLoader("templates"))
    # loading the template
    template = env.get_template("recipe_template.jinja")
    # rendering the template and storing the resultant text in variable output
    simplified_recipe = template.render(
        title=title,
        ingredients=ingredients,
        instructions=instructions,
        total_time=total_time,
    )

    return simplified_recipe
