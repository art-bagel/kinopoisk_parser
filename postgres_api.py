import psycopg2


class PostgresqlAPI:
    def __init__(self, dbname, user, password, host):
        self.conn = psycopg2.connect(
            dbname=dbname, user=user, password=password, host=host)

    def __enter__(self):
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
        self.cursor.close()

    def postgresql_requests(self, sql, values):
        """Отправляет запрос в базу данных."""
        return self.cursor.execute(sql, values)

    def commit(self):
        self.conn.commit()

    def insert_movie(self, **kwargs):
        """Добавляет данные о фильме в таблицу."""
        sql = '''INSERT INTO movies(title, 
                                    alternative_title, 
                                    kp_rating, 
                                    production_year, 
                                    play_time, 
                                    kp_link,
                                    actors_link
                                    ) VALUES(%s, %s, %s, %s, %s, %s, %s) 
                                      RETURNING movie_id;'''
        values = (kwargs['title'],
                  kwargs['alternative_title'],
                  kwargs['kp_rating'],
                  kwargs['production_year'],
                  kwargs['play_time'],
                  kwargs['kp_link'],
                  kwargs['actors_link']
                  )
        self.postgresql_requests(sql, values)
        return self.cursor.fetchone()[0]

    def insert_genres(self, genres):
        """Добавляет жанры в таблицу."""
        sql = '''INSERT INTO genres(genre) VALUES(%s) 
                 ON CONFLICT (genre) DO UPDATE SET genre = %s RETURNING genre_id;'''
        genres_id = []
        for genre in genres:
            self.postgresql_requests(sql, values=(genre, genre))
            genres_id.append(self.cursor.fetchone()[0])
        return genres_id

    def insert_movies_genres(self, movie_id, genres_id):
        """Добавляет свзяь между фильмом и жанрами."""
        sql = '''INSERT INTO movies_genres(movie_id, genre_id) VALUES (%s, %s);'''
        for genre_id in genres_id:
            self.postgresql_requests(sql, values=(movie_id, genre_id))

    def insert_country(self, country):
        """Добавляет страну в таблицу."""
        sql = '''INSERT INTO countries(country) VALUES (%s) 
                 ON CONFLICT (country) DO UPDATE SET country = %s RETURNING country_id;'''
        self.postgresql_requests(sql, values=(country, country))
        return self.cursor.fetchone()[0]

    def insert_movies_countries(self, movie_id, country_id):
        """Добавляет свзяь между фильмом и страной."""
        sql = '''INSERT INTO movies_countries(movie_id, country_id) values(%s, %s);'''
        self.postgresql_requests(sql, values=(movie_id, country_id))

    def insert_directors(self, director_name):
        """Добавляет режисера в таблицу."""
        sql = '''INSERT INTO directors(director_name) VALUES (%s) 
                 ON CONFLICT (director_name) DO UPDATE SET director_name = %s RETURNING director_id;'''
        self.postgresql_requests(sql, values=(director_name, director_name))
        return self.cursor.fetchone()[0]

    def insert_movies_directors(self, movie_id, director_id):
        """Добавляет связь между фильмом и режисером."""
        sql = '''INSERT INTO movies_directors(movie_id, director_id) values(%s, %s)'''
        self.postgresql_requests(sql, values=(movie_id, director_id))

    def create_table_movies(self):
        """Создает таблицу с фильмами."""
        sql = '''create table movies(
                                     movie_id serial primary key,
                                     title varchar(200) not null,
                                     alternative_title varchar(200),
                                     kp_rating decimal(4,3),
                                     production_year int,
                                     play_time int,
                                     kp_link varchar(250),
                                     actors_link varchar(250)
                                     );'''
        self.postgresql_requests(sql, values=None)

    def create_table_genres(self):
        """Создает таблицу с жанрами."""
        sql = '''create table genres(
	                                 genre_id serial primary key,
	                                 genre varchar(25) unique
                                     );'''
        self.postgresql_requests(sql, values=None)

    def create_table_countries(self):
        """Создает страницу со странами."""
        sql = '''create table countries(
                                        country_id serial primary key,
                                        country varchar(25) unique
                                        );'''
        self.postgresql_requests(sql, values=None)

    def create_table_directors(self):
        """Создает таблицу с режисерами фильмов."""
        sql = '''create table directors(
                                      director_id serial primary key,
                                      director_name varchar(50) unique
                                      ); '''
        self.postgresql_requests(sql, values=None)

    def create_table_movies_genres(self):
        """Создает таблицу связывающую фильм и жанры."""
        sql = '''create table movies_genres(
                                            movies_genres_id serial primary key,
                                            movie_id int not null,
                                            genre_id int not null,
                                            foreign key (movie_id) references movies(movie_id),
                                            foreign key (genre_id) references genres(genre_id)
                                            );'''
        self.postgresql_requests(sql, values=None)

    def create_table_movies_countries(self):
        """Создает таблицу связывающую фильм и страну."""
        sql = '''create table movies_countries(
                                               movies_countries_id serial primary key,
                                               movie_id int not null,
                                               country_id int not null,
                                               foreign key (movie_id) references movies(movie_id),
                                               foreign key (country_id) references countries(country_id)
                                               );'''
        self.postgresql_requests(sql, values=None)

    def create_table_movies_directors(self):
        """Создает таблицу связывающую фильм и режисера."""
        sql = '''create table movies_directors(
	                                          movies_directors_id serial primary key,
                                              movie_id int not null,
                                              director_id int not null,
                                              foreign key (movie_id) references movies(movie_id),
                                              foreign key (director_id) references directors(director_id)
                                              );'''
        self.postgresql_requests(sql, values=None)

    def drop_all_table(self):
        """Удаляет все созданные таблицы если они существуют."""
        sql = '''drop table if exists movies_genres;
                 drop table if exists movies_countries;
                 drop table if exists movies_director;
                 drop table if exists movies;
                 drop table if exists genres;
                 drop table if exists countries;
                 drop table if exists persons;'''
        self.postgresql_requests(sql, values=None)
