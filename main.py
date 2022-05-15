import logging.config
import time

from requests import ConnectionError, HTTPError

from postgres_api import PostgresqlAPI
from parser_movies import get_number_pages, get_movies_data
import settings as st
from loging_config import LOGGING_CONFIG


logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('main')


def save_parsing_state(year='', page=''):
    """Сохраняет состояние незавершенного парсинга."""
    with open('last_parsed_state.txt', 'w') as file:
        file.write(str(year) + '\n' + str(page))


def set_start_settings():
    """Если был незавершенный парсинг, возвращает последнее состояние,
    иначе возвращает дефолтные настройки.
    """
    start_settings = {
        'sleep': st.SLEEP,
        'finish_year': st.DEFAULT_FINISH_YEAR
    }
    with open('last_parsed_state.txt', 'r+') as file:
        year = file.readline()
        page = file.readline(2)
        if year and page:
            start_settings['year'] = int(year)
            start_settings['page'] = int(page)
        else:
            start_settings['year'] = st.DEFAULT_START_YEAR
            start_settings['page'] = st.DEFAULT_START_PAGE
    save_parsing_state()
    return start_settings


def insert_data_base(movies):
    """Добавляет полученные данные от парсера в базу данных."""
    with PostgresqlAPI(st.DB_NAME,
                       st.DB_USERNAME,
                       st.DB_PASSWORD,
                       st.DB_HOST) as db:
        for movie in movies:
            movie_id = db.insert_movie(**movie)
            if movie['genres']:
                genres_id = db.insert_genres(movie['genres'])
                db.insert_movies_genres(movie_id, genres_id)
            if movie['country']:
                country_id = db.insert_country(movie['country'])
                db.insert_movies_countries(movie_id, country_id)
            if movie['director']:
                director_id = db.insert_directors(movie['director'])
                db.insert_movies_directors(movie_id, director_id)
        db.commit()


def main():
    start_settings = set_start_settings()
    try:
        for year in range(start_settings['year'], start_settings['finish_year'], -1):
            number_pages = get_number_pages(year)
            for page in range(start_settings['page'], number_pages + 1):
                movies = get_movies_data(year, page)
                insert_data_base(movies)
                logger.info(f'Парсинг {page} страницы завершен успешно! '
                            f'Фильмы добавлены в базу данных!')
                time.sleep(start_settings['sleep'])
            logger.info(f'Фильмы за {year} год в базе данных!')
    except HTTPError as error:
        logger.error(f'Ошибка при запросе страницы {error}')
    except ConnectionError as error:
        logger.error(f'Проблемы с интернет соединением {error}')
    except Exception as error:
        logger.error(f'Произошла ошибка: {error}', exc_info=True)
        save_parsing_state(year, page)


if __name__ == '__main__':
    main()