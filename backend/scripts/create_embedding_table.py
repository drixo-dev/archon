from app.db.postgres import (
    postgres_connection
)

def create_table():
    postgres_connection.connect()
    connection = (
        postgres_connection.get_connection()
    )
    cursor = connection.cursor()
    cursor.execute("""
        CREATE EXTENSION IF NOT EXISTS vector;

        CREATE TABLE IF NOT EXISTS
        function_embeddings (

            id TEXT PRIMARY KEY,

            file_path TEXT,

            source_code TEXT,

            embedding VECTOR(384)
        );
    """)
    connection.commit()
    cursor.close()
    postgres_connection.close()
    print("Embedding table created.")

if __name__ == "__main__":
    create_table()