from app.db.neo4j import neo4j_connection

class GraphService:

    def create_repository(self, name: str, url: str):
        query = """
        MERGE (r:Repository {name: $name})
        SET r.url = $url
        RETURN r
        """

        with neo4j_connection.get_session() as session:
            result = session.run(
                query,
                name=name,
                url=url
            )

            return result.single()

graph_service = GraphService()
