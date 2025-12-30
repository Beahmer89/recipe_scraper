import duckdb

# to use a database file (shared between processes)
CONNECTION = duckdb.connect(database="./my-db.duckdb")


def main():
    CONNECTION.execute(
        "CREATE SEQUENCE IF NOT EXISTS recipes_id_seq START 1 INCREMENT 1;"
    )
    # create a table
    CONNECTION.execute(
        """CREATE TABLE IF NOT EXISTS recipes (
        id INTEGER PRIMARY KEY DEFAULT(nextval('recipes_id_seq')),
        title TEXT,
        image TEXT,
        url TEXT,
        recipe_html TEXT,
        rating INTEGER,
        times_made INTEGER)
        """
    )

    CONNECTION.execute(
        "CREATE SEQUENCE IF NOT EXISTS meal_plan_id_seq START 1 INCREMENT 1;"
    )
    CONNECTION.execute(
        "CREATE SEQUENCE IF NOT EXISTS meal_plan_recipe_id_seq START 1 INCREMENT 1;"
    )

    CONNECTION.execute(
        """CREATE TABLE IF NOT EXISTS meal_plan(
        id INTEGER PRIMARY KEY DEFAULT(nextval('meal_plan_id_seq')),
        name TEXT,
        status TEXT,
        created_at TIMESTAMP WITH TIME ZONE,
        updated_at TIMESTAMP WITH TIME ZONE,
        )
        """
    )

    CONNECTION.execute(
        """CREATE TABLE IF NOT EXISTS meal_plan_recipes(
        id INTEGER PRIMARY KEY DEFAULT(nextval('meal_plan_recipe_id_seq')),
        meal_plan_id INTEGER REFERENCES meal_plan,
        recipe_id INTEGER REFERENCES recipes,
        assigned_day TEXT,
        recipe_type TEXT
        )
        """
    )

    CONNECTION.execute(
        """
        DROP INDEX IF EXISTS meal_plan_recipe_unique_idx;
        """
    )

    CONNECTION.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS meal_plan_recipe_unique_idx
        ON meal_plan_recipes(meal_plan_id, assigned_day, recipe_type);
        """
    )


if __name__ == "__main__":
    main()
