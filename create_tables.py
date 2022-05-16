from postgres_api import PostgresqlAPI
import settings as st


def create_tables():
    with PostgresqlAPI(st.DB_NAME,
                       st.DB_USERNAME,
                       st.DB_PASSWORD,
                       st.DB_HOST) as db:
        db.create_table_movies()
        db.create_table_genres()
        db.create_table_countries()
        db.create_table_directors()
        db.create_table_movies_genres()
        db.create_table_movies_countries()
        db.create_table_movies_directors()
        db.commit()


if __name__ == '__main__':
    create_tables()