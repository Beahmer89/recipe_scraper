from db_setup import CONNECTION
import logging

LOGGER = logging.getLogger()
logging.basicConfig(level="INFO")


def get_recipes():
    fetch_result = CONNECTION.execute(
        "SELECT id, title, image, url, recipe_html FROM recipes;"
    ).fetchnumpy()

    result = [
        {
            "id": int(fetch_result["id"][i]),
            "url": str(fetch_result["url"][i]),
            "title": str(fetch_result["title"][i]),
            "image": str(fetch_result["image"][i]),
            "html": str(fetch_result["recipe_html"][i]),
        }
        for i in range(len(fetch_result["id"]))
    ]

    return result


def get_recipes_paginated(limit: int, offset: int):
    fetch_result = CONNECTION.execute(
        """SELECT id, title, image, url, recipe_html
        FROM recipes
        LIMIT ? OFFSET ?
        """,
        [limit, offset],
    ).fetchnumpy()

    result = [
        {
            "id": int(fetch_result["id"][i]),
            "url": str(fetch_result["url"][i]),
            "title": str(fetch_result["title"][i]),
            "image": str(fetch_result["image"][i]),
            "html": str(fetch_result["recipe_html"][i]),
        }
        for i in range(len(fetch_result["id"]))
    ]

    return result


def get_recipe_total():
    fetch_result = CONNECTION.execute(
        "SELECT count(*) as total FROM recipes;"
    ).fetchnumpy()

    return fetch_result["total"][0]


def get_recipe_by_id(recipe_id: int):
    fetch_result = CONNECTION.execute(
        """SELECT title, image, url, recipe_html
        FROM recipes
        WHERE id = ?;""",
        [recipe_id],
    ).fetchnumpy()

    return fetch_result


def insert_recipe(recipe: dict):
    data = [recipe["title"], recipe["image"], recipe["url"], recipe["recipe"]]
    CONNECTION.execute(
        "INSERT INTO recipes (title, image, url, recipe_html) VALUES(?, ?, ?, ?)", data
    )


def update_recipe_by_id(recipe_id: int, recipe_html):
    CONNECTION.execute(
        """UPDATE recipes
        SET recipe_html = ?
        WHERE id = ?;""",
        [recipe_html, recipe_id],
    )


def delete_recipe_by_id(recipe_id: int):
    fetch_result = CONNECTION.execute(
        """DELETE FROM recipes
        WHERE id = ?;""",
        [recipe_id],
    ).fetchnumpy()

    return fetch_result
