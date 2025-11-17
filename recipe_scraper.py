import logging
import json

from bs4 import BeautifulSoup
import httpx

import jinja_helper


LOGGER = logging.getLogger()
logging.basicConfig(level="INFO")


def get_recipe(url: str) -> str:
    LOGGER.info("Getting recipe: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        with httpx.Client() as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()
    except (httpx.HTTPStatusError, httpx.RequestError, httpx.ConnectError) as error:
        LOGGER.error("INVALID URL: %s ERROR: %s", url, error)
        return ""

    return response.text


def create_recipe_page(html: str, url: str) -> dict:
    image = ""
    soup = BeautifulSoup(html, "html.parser")
    title = soup.find_all("title")
    LOGGER.info(f"TITLES FOUND: {len(title)}")
    new_title = str(title[0]).replace("title", "h1")
    bold_title = new_title.replace("h1", "b")

    # Find Image
    og_image = soup.find("meta", property="og:image")
    if og_image and og_image.get("content"):
        image = og_image["content"]

    # Find Script that seems to have all recipe info
    json_script = soup.find_all("script", type="application/ld+json")
    if (
        not json_script
        or hasattr(json_script, "contents")
        or not json_script[0].contents
    ):
        LOGGER.error(f"Could not locate script with recipe info for {url}")
        return {}

    script_info = json.loads(json_script[0].contents[0])
    LOGGER.info(f"LENGTH OF {type(script_info)} SCRIPT: {len(script_info)}")

    if isinstance(script_info, list):
        recipe_details = script_info[0]
    else:
        # @graph is a list dict: [{}] and other times its just a dict
        if script_info.get("@graph"):
            recipe_section = [
                element
                for element in script_info["@graph"]
                if element.get("recipeIngredient")
            ]
            recipe_details = recipe_section[0] if recipe_section else {}
        else:
            recipe_details = script_info

    # Get Recipe elements
    ingredients = recipe_details.get("recipeIngredient", [])
    instructions = recipe_details.get("recipeInstructions", [])
    total_time = recipe_details.get("totalTime", "n/a")
    if isinstance(total_time, dict):
        total_time = total_time.get("minValue", "n/a")
    total_time = total_time.split("PT")

    LOGGER.info(f"TIME for {url}: {total_time}")
    total_time = total_time[1] if len(total_time) == 2 else total_time[0]
    LOGGER.info(f"INGREDIENTS for {url}: {len(ingredients)}")
    LOGGER.info(f"INSTRUCTIONS for {url}: {len(instructions)}")

    if not instructions or not ingredients:
        LOGGER.error("Did not find instructions or ingredients")
        return {}

    instruction_steps = []
    for instruction in instructions:
        if instruction.get("text"):
            instruction_steps.append(instruction["text"])
        if instruction.get("itemListElement"):
            for list_element in instruction["itemListElement"]:
                if list_element.get("text"):
                    instruction_steps.append(list_element["text"])

    simplified_recipe = jinja_helper.create_simplified_recipe(
        title=new_title,
        ingredients=ingredients,
        instructions=instruction_steps,
        total_time=total_time,
    )

    return {
        "title": bold_title,
        "image": image,
        "url": url,
        "recipe": simplified_recipe,
    }
