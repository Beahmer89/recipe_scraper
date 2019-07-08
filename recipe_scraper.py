import argparse
import logging

from bs4 import BeautifulSoup
import requests


LOGGER = logging.getLogger()
logging.basicConfig(level='INFO')


def get_args():
    parser = argparse.ArgumentParser(description='Read from specified file '
                                     'and update Mongo if present and data is '
                                     'different')
    parser.add_argument('-u', '--url', required=True, help='URL of recipe')
    return parser.parse_args()


def get_recipe(url):
    LOGGER.info('Getting recipe')
    try:
        response = requests.get(url)
    except (requests.exceptions.HTTPError, requests.exceptions.MissingSchema,
            requests.exceptions.ConnectionError):
        LOGGER.error('INVALID URL: %s', url)
        return ''

    return response.text


def create_recipe_page(html):
    LOGGER.info('Trying to construct new recipe page')
    soup = BeautifulSoup(html, 'html.parser')

    for div in soup.find_all('div'):
        if div.get('class'):
            if 'ingredients' in div['class'][0] or \
               'instructions' in div['class'][0]:
                with open('recipe.html', 'a+') as f:
                    for content in div.contents:
                        f.write(str(content))


def main():
    args = get_args()
    html = get_recipe(args.url)
    create_recipe_page(html)


if __name__ == "__main__":
    main()
