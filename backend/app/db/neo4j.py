from neo4j import GraphDatabase
from app.config import settings


class Neo4jConnection:
    def __init__(self):
        self.driver = None

    def connect(self):
        if self.driver:
            return self.driver

        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(
                settings.NEO4J_USERNAME,
                settings.NEO4J_PASSWORD
            )
        )
        return self.driver

    def close(self):
        if not self.driver:
            return

        try:
            self.driver.close()
        except Exception:
            pass
        finally:
            self.driver = None

    def get_session(self):
        if not self.driver:
            raise Exception("Neo4j driver not initialized")

        return self.driver.session()


neo4j_connection = Neo4jConnection()
