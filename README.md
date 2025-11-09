# recipe_scraper

This project eliminates the business of blog posts or web pages when all you want is a recipe.
Currently it is using Streamlit for FE and is an actual app to:
- store recipes you like by generating a simplied recipe
- view all your recipes

## Setup
```bash
uv venv
source .venv/bin/activate
uv sync --dev
```

## How to use
### Step 1
Setup DB by running:
```bash
python db_setup.py
```

### Step 2
Run the application by:
```bash
streamlit run app.py
```

### Step 3
Then navigate to homepage by going to url:
- http://localhost:8501/
