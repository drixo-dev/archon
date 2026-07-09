from app.db.neo4j import neo4j_connection
from repositories.metadata_repository import metadata_repository

class StatisticsService:
    def get_repository_statistics(self, repository_id: str) -> dict | None:
        repo = metadata_repository.get_repository(repository_id)
        if not repo:
            return None

        with neo4j_connection.get_session() as session:
            # Files count
            result = session.run("MATCH (f:File {repository_name: $repo}) RETURN count(f) as c", repo=repository_id)
            files_count = result.single()["c"]

            # Functions count
            result = session.run("MATCH (f:Function {repository_name: $repo}) RETURN count(f) as c", repo=repository_id)
            functions_count = result.single()["c"]

            # Imports count
            result = session.run("MATCH (f:File {repository_name: $repo})-[r:IMPORTS]->() RETURN count(r) as c", repo=repository_id)
            imports_count = result.single()["c"]

            # Internal dependencies count
            result = session.run("MATCH (f:File {repository_name: $repo})-[r:DEPENDS_ON]->() RETURN count(r) as c", repo=repository_id)
            internal_deps_count = result.single()["c"]

            # Call relationships count
            result = session.run("MATCH (f:Function {repository_name: $repo})-[r:CALLS]->() RETURN count(r) as c", repo=repository_id)
            calls_count = result.single()["c"]
            
            # Graph nodes count
            result = session.run("MATCH (n) WHERE n.repository_name = $repo OR (n:Repository AND n.name = $repo) RETURN count(n) as c", repo=repository_id)
            base_nodes_count = result.single()["c"]
            
            result = session.run("MATCH (f:File {repository_name: $repo})-[:IMPORTS]->(i:Import) RETURN count(DISTINCT i) as c", repo=repository_id)
            imports_nodes = result.single()["c"]
            
            graph_nodes = base_nodes_count + imports_nodes

            # Graph relationships count
            result = session.run("MATCH (n) WHERE n.repository_name = $repo OR (n:Repository AND n.name = $repo) MATCH (n)-[r]->() RETURN count(r) as c", repo=repository_id)
            graph_relationships = result.single()["c"]

            # Top level folders
            result = session.run("MATCH (f:File {repository_name: $repo}) RETURN f.path as path", repo=repository_id)
            paths = [record["path"] for record in result]
            top_level_folders = set()
            for p in paths:
                parts = p.split("/")
                if len(parts) > 1:
                    top_level_folders.add(parts[0])
            sorted_folders = sorted(list(top_level_folders))
            
            # Primary language
            result = session.run("MATCH (f:File {repository_name: $repo}) RETURN f.language as lang, count(f) as c ORDER BY c DESC LIMIT 1", repo=repository_id)
            record = result.single()
            primary_language = record["lang"].capitalize() if record else "Unknown"

        embeddings = repo.get("embeddings_generated", 0)
        indexed_functions = repo.get("functions_indexed", 0)
        index_completion = 0
        if indexed_functions > 0:
            index_completion = round((embeddings / indexed_functions) * 100)

        return {
            "repository": {
                "id": repo["id"],
                "name": repo["name"],
                "primary_language": primary_language,
                "last_indexed_at": repo.get("last_indexed_at")
            },
            "codebase": {
                "files": files_count,
                "functions": functions_count,
                "imports": imports_count,
                "top_level_folders": {
                    "count": len(sorted_folders),
                    "folders": sorted_folders
                }
            },
            "knowledge_graph": {
                "internal_dependencies": internal_deps_count,
                "call_relationships": calls_count,
                "graph_nodes": graph_nodes,
                "graph_relationships": graph_relationships
            },
            "ai_index": {
                "embeddings": embeddings,
                "indexed_functions": indexed_functions,
                "index_completion": index_completion
            }
        }

statistics_service = StatisticsService()
