import requests
from bs4 import BeautifulSoup

from settings import DOMAIN, ENDPOINT, MOVIES_PER_PAGE


def get_html(url):
    """Запрашивает искомую страницу."""
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def parser_html(html):
    """Парсит html переданной страницы."""
    data = []
    soup = BeautifulSoup(html, 'lxml')
    cards_film = soup.find_all('div', class_='element')
    for card in cards_film:
        movies = {}
        info = card.find('div', class_='info')
        movies['title'] = get_data_or_none(
            "soup.find('p', class_='name').find('a').text", info)
        alt_title_and_time = get_data_or_none(
            "soup.find_all('span', class_='gray')[0].text", info)
        movies['alternative_title'] = extract_alternative_title(alt_title_and_time)
        movies['play_time'] = extract_play_time(alt_title_and_time)
        movies['kp_rating'] = get_data_or_none(
            "soup.find('div', class_='rating').text", card)
        production_year = get_data_or_none(
            "soup.find('span', class_='year').text", info)
        movies['production_year'] = extract_production_year(production_year)
        movies['director'] = get_data_or_none(
            "soup.find_all('span', class_='gray')[1].find('a', class_='lined').text", info)
        movies['kp_link'] = get_data_or_none(
            "DOMAIN + soup.find('a').get('href')", info)
        country_and_genre = get_data_or_none(
            "soup.find_all('span', class_='gray')[1].contents", info)
        movies['country'] = extract_country(country_and_genre)
        movies['genres'] = extract_genres(country_and_genre)
        actors_link = get_data_or_none(
            "DOMAIN + soup.find('div', class_='right').find('a').get('href')", card)
        movies['actors_link'] = check_actors_link(actors_link)
        data.append(movies)
    return data


def clean_string(dirty_string):
    """Очищает строку от посторонних элементов."""
    return dirty_string.replace(',', '').replace('...', '').strip()


def extract_country(dirty_data):
    """Извлекает и очищает страну."""
    if not dirty_data:
        return None
    country = clean_string(dirty_data[0])
    if not country:
        return None
    return country


def extract_genres(dirty_data: list):
    """Извлекает, очищает и возвращает список жанров."""
    if not dirty_data:
        return None
    genres = clean_string(dirty_data[-1]).replace('(', '').replace(')', '').strip()
    if genres:
        return genres.split(' ')
    return None


def extract_production_year(dirty_data):
    """Извлекает, очищает и возвращает год производства фильма."""
    return clean_string(dirty_data).replace('–', '').strip()


def extract_play_time(dirty_string):
    """Извлекает продолжительность фильма из строки."""
    if dirty_string and 'мин' in dirty_string:
        if dirty_string.find(',') != -1:
            play_time = dirty_string[dirty_string.rfind(','):]
            play_time = clean_string(play_time)
        else:
            play_time = clean_string(dirty_string)
        return int(play_time.replace('мин', ''))
    return None


def extract_alternative_title(dirty_string):
    """Извлекает альтернативное название фильма из строки."""
    if not dirty_string:
        return None
    if 'мин' not in dirty_string:
        return clean_string(dirty_string)
    elif dirty_string.find(',') != -1:
        return dirty_string[:dirty_string.rfind(',')]
    return None


def get_data_or_none(expression, soup):
    """Возвращает данные если они существуют."""
    try:
        return eval(expression)
    except Exception:
        return None


def check_actors_link(link):
    """Проверяет, что ссылка ведет на страницу с актерами."""
    if link and 'actor' in link:
        return link
    return None


def get_number_pages(year):
    """Возвращает колличество страниц для парсинга."""
    page = 1
    url = DOMAIN + ENDPOINT.format(year, page)
    html_page = get_html(url)
    soup = BeautifulSoup(html_page, 'lxml')
    dirty_string = soup.find('span',
                             class_='search_results_topText').contents[-1]
    number_movies = dirty_string.split(' ')[-1]
    number_pages = round(int(number_movies) / MOVIES_PER_PAGE)
    return number_pages


def get_movies_data(year, page):
    """Возвращает словарь с данными фильмов."""
    url = DOMAIN + ENDPOINT.format(year, page)
    html_page = get_html(url)
    return parser_html(html_page)

