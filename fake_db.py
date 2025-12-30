from db_setup import CONNECTION
import logging

import streamlit

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


@streamlit.cache_data
def get_current_meal_plan():
    LOGGER.info("Query executing")
    fetch_result = CONNECTION.sql(
        """SELECT mp.id as meal_plan_id, r.*, mpr.assigned_day, mpr.recipe_type
        FROM meal_plan mp
        INNER JOIN meal_plan_recipes mpr ON mp.id = mpr.meal_plan_id
        INNER JOIN recipes r ON mpr.recipe_id = r.id
        WHERE mp.status = 'current';""",
    ).fetchnumpy()

    result = [
        {
            "meal_plan_id": int(fetch_result["meal_plan_id"][i]),
            "id": int(fetch_result["id"][i]),
            "url": str(fetch_result["url"][i]),
            "title": str(fetch_result["title"][i]),
            "assigned_day": str(fetch_result["assigned_day"][i]),
            "recipe_type": str(fetch_result["recipe_type"][i]),
        }
        for i in range(len(fetch_result["id"]))
    ]

    LOGGER.info("Query done")
    return result


def complete_meal_plan(meal_plan_id):
    CONNECTION.execute(
        """UPDATE meal_plan SET status = 'complete',
        updated_at = (NOW() AT TIME ZONE 'UTC')
        WHERE id = ?  """,
        [meal_plan_id],
    )


def save_meal_plan(current_meal_plan, meal_plan_id=None):
    if not meal_plan_id:
        name = "NEW Meal Plan"
        return_value = CONNECTION.execute(
            """INSERT INTO meal_plan (name, status, created_at, updated_at)
            VALUES(?, 'current', NOW() AT TIME ZONE 'UTC', NOW() AT TIME ZONE 'UTC') RETURNING id;""",
            [name],
        ).fetchone()
        meal_plan_id = return_value[0]

    for day, meal_types in current_meal_plan.items():
        for meal_type, recipe_info in meal_types.items():
            recipe_id = recipe_info["id"]
            CONNECTION.execute(
                """INSERT INTO meal_plan_recipes(meal_plan_id, recipe_id, assigned_day, recipe_type)
                VALUES(?, ?, ?, ?)
                ON CONFLICT (meal_plan_id, assigned_day, recipe_type)
                DO UPDATE SET
                    recipe_id=EXCLUDED.recipe_id;""",
                [meal_plan_id, recipe_id, day, meal_type],
            )

    return meal_plan_id


def delete_recipe_from_meal_plan_by_id(recipe_id: int, meal_plan_id: int):
    CONNECTION.execute(
        """DELETE FROM meal_plan_recipes
        WHERE recipe_id = ? and meal_plan_id = ?;""",
        [recipe_id, meal_plan_id],
    )
