import logging

from bs4 import BeautifulSoup, NavigableString
import httpx

UNWANTED_TAGS = {"h3", "script", "style", "button"}  # tags to skip entirely
LOGGER = logging.getLogger()
logging.basicConfig(level="INFO")


def get_recipe(url):
    LOGGER.info("Getting recipe")
    try:
        with httpx.Client() as client:
            response = client.get(url)
            response.raise_for_status
    except (httpx.HTTPStatusError, httpx.RequestError, httpx.ConnectError):
        LOGGER.error("INVALID URL: %s", url)
        return ""

    return response.text


def create_recipe_page(html, url):
    recipe = list()
    soup = BeautifulSoup(html, "html.parser")
    title = soup.find_all("title")
    LOGGER.info(f"TITLES FOUND: {len(title)}")
    new_title = str(title[0]).replace("title", "h1")
    recipe.append(str(new_title))

    # Find Image
    og_image = soup.find("meta", property="og:image")
    if og_image and og_image.get("content"):
        image = og_image["content"]

    for div in soup.find_all("div"):
        if div.get("class"):
            if "ingredients" in div["class"][0] or "instructions" in div["class"][0]:
                for content in div.contents:
                    if isinstance(content, NavigableString):
                        continue
                    if content.find_all("button"):
                        LOGGER.info("button")
                        continue
                    if content.name in UNWANTED_TAGS:
                        continue
                    recipe.append(str(content))

    simplified_recipe = " ".join(recipe)
    bold_title = new_title.replace("h1", "b")

    # return values to insert INTO DATABASE
    return [bold_title, image, url, simplified_recipe]
