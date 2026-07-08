import psycopg2


class PostgresConnection:
    def __init__(self):
        self.connection = None

    def connect(self):
        if self.connection:
            return self.connection

        self.connection = psycopg2.connect(
            host="postgres",
            port=5432,
            dbname="archon",
            user="archon",
            password="archon"
        )
        print("Connected to PostgreSQL")
        return self.connection

    def get_connection(self):
        return self.connection

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None


postgres_connection = PostgresConnection()