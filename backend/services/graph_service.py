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
        function_name: str,
        source_code: str = None
    ):
        qualified_name = f"{file_path}:{function_name}"

        query = """
        MERGE (f:File {path: $file_path})

        MERGE (func:Function {
            qualified_name: $qualified_name
        })

        SET func.name = $function_name
        SET func.file_path = $file_path
        SET func.source_code = $source_code

        MERGE (f)-[:DEFINES]->(func)

        RETURN func
        """

        with neo4j_connection.get_session() as session:
            result = session.run(
                query,
                file_path=file_path,
                function_name=function_name,
                qualified_name=qualified_name,
                source_code=source_code
            )

            return result.single()

    def create_import_node(
        self,
        module,
        import_type,
        alias=None,
        imported_name=None
    ):
        query = """
        MERGE (i:Import {
            module: $module,
            type: $type
        })

        SET i.alias = $alias
        SET i.imported_name = $imported_name

        RETURN i
        """

        with neo4j_connection.get_session() as session:
            result = session.run(
                query,
                module=module,
                type=import_type,
                alias=alias,
                imported_name=imported_name
            )

            return result.single()

    def create_file_import_relationship(
        self,
        file_path,
        module,
        import_type,
        alias=None,
        imported_name=None
    ):
        query = """
        MATCH (f:File {path: $file_path})

        MATCH (i:Import {
            module: $module,
            type: $type
        })

        MERGE (f)-[:IMPORTS]->(i)
        """

        with neo4j_connection.get_session() as session:
            session.run(
                query,
                file_path=file_path,
                module=module,
                type=import_type
            )

    def create_dependency_relationship(
        self,
        source_file_path,
        target_file_path
    ):
        query = """
        MATCH (source:File {path: $source_file_path})
        MATCH (target:File {path: $target_file_path})

        MERGE (source)-[:DEPENDS_ON]->(target)
        """

        with neo4j_connection.get_session() as session:
            session.run(
                query,
                source_file_path=source_file_path,
                target_file_path=target_file_path
            )

    def create_function_call_relationship(
        self,
        caller_qualified_name,
        callee_qualified_name
    ):
        query = """
        MATCH (caller:Function {
            qualified_name: $caller_qualified_name
        })

        MATCH (callee:Function {
            qualified_name: $callee_qualified_name
        })

        MERGE (caller)-[:CALLS]->(callee)
        """

        with neo4j_connection.get_session() as session:
            session.run(
                query,
                caller_qualified_name=caller_qualified_name,
                callee_qualified_name=callee_qualified_name
            )
    
    def get_all_functions(
        self,
        exclude_tests: bool = True
    ):
        query = """
        MATCH (f:Function)
        WHERE f.source_code IS NOT NULL
        RETURN
            f.qualified_name AS qualified_name,
            f.file_path AS file_path,
            f.source_code AS source_code
        """

        with neo4j_connection.get_session() as session:

            results = session.run(query)

            functions = []

            for record in results:

                if (
                    exclude_tests
                    and record["file_path"].startswith(
                        "tests/"
                    )
                ):
                    continue

                functions.append(
                    {
                        "qualified_name":
                            record["qualified_name"],
                        "file_path":
                            record["file_path"],
                        "source_code":
                            record["source_code"]
                    }
                )

            return functions
        
        
    def get_function_neighbors(
        self,
        qualified_name: str
    ):

        query = """
        MATCH (f:Function {
            qualified_name: $qualified_name
        })

        OPTIONAL MATCH
            (f)-[:CALLS]->(callee:Function)

        OPTIONAL MATCH
            (caller:Function)-[:CALLS]->(f)

        RETURN
            f.qualified_name AS function_name,

            collect(
                DISTINCT callee.qualified_name
            ) AS callees,

            collect(
                DISTINCT caller.qualified_name
            ) AS callers
        """

        with neo4j_connection.get_session() as session:

            result = session.run(
                query,
                qualified_name=qualified_name
            )

            record = result.single()

            if not record:
                return None

            return {
                "function":
                    record["function_name"],

                "callees":
                    [
                        c for c in record["callees"]
                        if c
                    ],

                "callers":
                    [
                        c for c in record["callers"]
                        if c
                    ]
            }

    def get_functions_by_file(
        self,
        file_path: str,
        limit: int = 10
    ):
        query = """
        MATCH (file:File {path: $file_path})
            -[:DEFINES]->(function:Function)
        WHERE function.source_code IS NOT NULL

        RETURN
            function.qualified_name AS qualified_name,
            function.file_path AS file_path,
            function.source_code AS source_code
        LIMIT $limit
        """

        with neo4j_connection.get_session() as session:

            results = session.run(
                query,
                file_path=file_path,
                limit=limit
            )

            return [
                {
                    "qualified_name":
                        record["qualified_name"],
                    "file_path":
                        record["file_path"],
                    "source_code":
                        record["source_code"]
                }
                for record in results
            ]

    def get_functions_by_qualified_names(
        self,
        qualified_names: list[str]
    ):
        if not qualified_names:
            return []

        query = """
        MATCH (function:Function)
        WHERE
            function.qualified_name IN $qualified_names
            AND function.source_code IS NOT NULL

        RETURN
            function.qualified_name AS qualified_name,
            function.file_path AS file_path,
            function.source_code AS source_code
        """

        with neo4j_connection.get_session() as session:

            results = session.run(
                query,
                qualified_names=qualified_names
            )

            return [
                {
                    "qualified_name":
                        record["qualified_name"],
                    "file_path":
                        record["file_path"],
                    "source_code":
                        record["source_code"]
                }
                for record in results
            ]

    def get_dependency_functions(
        self,
        file_path: str,
        limit: int = 10
    ):
        query = """
        MATCH (source:File {path: $file_path})
            -[:DEPENDS_ON]->(target:File)
            -[:DEFINES]->(function:Function)
        WHERE function.source_code IS NOT NULL

        RETURN
            function.qualified_name AS qualified_name,
            function.file_path AS file_path,
            function.source_code AS source_code
        LIMIT $limit
        """

        with neo4j_connection.get_session() as session:

            results = session.run(
                query,
                file_path=file_path,
                limit=limit
            )

            return [
                {
                    "qualified_name":
                        record["qualified_name"],
                    "file_path":
                        record["file_path"],
                    "source_code":
                        record["source_code"]
                }
                for record in results
            ]

graph_service = GraphService()
