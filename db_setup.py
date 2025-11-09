import duckdb

# to use a database file (shared between processes)
CONNECTION = duckdb.connect(database="./my-db.duckdb")


def main():
    CONNECTION.execute("CREATE SEQUENCE recipes_id_seq START 1 INCREMENT 1;")
    # create a table
    CONNECTION.execute(
        """CREATE TABLE recipes (
        id INTEGER PRIMARY KEY DEFAULT(nextval('recipes_id_seq')),
        title TEXT,
        image TEXT,
        url TEXT,
        recipe_html TEXT,
        rating INTEGER,
        times_made INTEGER)
        """
    )


if __name__ == "__main__":
    main()
