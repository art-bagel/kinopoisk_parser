import os

from dotenv import load_dotenv

load_dotenv()

DOMAIN = 'https://www.kinopoisk.ru'
ENDPOINT = '/s/type/film/list/1/order/rating/m_act[year]/{}/m_act[type]/film/page/{}/'
MOVIES_PER_PAGE = 100
DEFAULT_START_YEAR = 2021
DEFAULT_FINISH_YEAR = 2020
DEFAULT_START_PAGE = 1
SLEEP = 8

DB_NAME = os.getenv('DB_NAME')
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
