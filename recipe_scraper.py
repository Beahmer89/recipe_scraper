import logging

from bs4 import BeautifulSoup, NavigableString
import httpx

UNWANTED_TAGS = {"h3", "script", "style", "button"}  # tags to skip entirely
LOGGER = logging.getLogger()
logging.basicConfig(level="INFO")


def get_recipe(url: str) -> str:
    LOGGER.info("Getting recipe")
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
    recipe = list()
    image = ""
    soup = BeautifulSoup(html, "html.parser")
    title = soup.find_all("title")
    LOGGER.info(f"TITLES FOUND: {len(title)}")
    new_title = str(title[0]).replace("title", "h1")

    # Find Image
    og_image = soup.find("meta", property="og:image")
    if og_image and og_image.get("content"):
        image = og_image["content"]

    for div in soup.find_all("div"):
        LOGGER.info(div.get("class"))
        if div.get("class"):
            if "ingredients" in div["class"][0] or "instructions" in div["class"][0]:
                for content in div.contents:
                    if isinstance(content, NavigableString):
                        continue
                    if content.find_all("button"):
                        continue
                    if content.name in UNWANTED_TAGS:
                        continue
                    recipe.append(str(content))

    LOGGER.info(f"Recipe Elements: {len(recipe)}")
    if recipe:
        simplified_recipe = " ".join(recipe)
        bold_title = new_title.replace("h1", "b")
        return {
            "title": bold_title,
            "image": image,
            "url": url,
            "recipe": simplified_recipe,
        }

    LOGGER.error(f"No Recipe found for {url}")
    return {}
