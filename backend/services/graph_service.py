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

    def create_file(
        self,
        repository_name: str,
        file_path: str,
        language: str = "python"
    ):
        query = """
        MERGE (r:Repository {name: $repository_name})

        MERGE (f:File {path: $file_path})
        SET f.language = $language

        MERGE (r)-[:CONTAINS]->(f)

        RETURN f
        """

        with neo4j_connection.get_session() as session:
            result = session.run(
                query,
                repository_name=repository_name,
                file_path=file_path,
                language=language
            )

            return result.single()
        

    def create_function(
        self,
        file_path: str,
        function_name: str
    ):
        qualified_name = f"{file_path}:{function_name}"

        query = """
        MERGE (f:File {path: $file_path})

        MERGE (func:Function {
            qualified_name: $qualified_name
        })

        SET func.name = $function_name
        SET func.file_path = $file_path

        MERGE (f)-[:DEFINES]->(func)

        RETURN func
        """

        with neo4j_connection.get_session() as session:
            result = session.run(
                query,
                file_path=file_path,
                function_name=function_name,
                qualified_name=qualified_name
            )

            return result.single()

graph_service = GraphService()