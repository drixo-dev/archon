from app.db.postgres import postgres_connection

class MetadataRepository:
    def _ensure_schema(self):
        connection = postgres_connection.get_connection()
        if not connection:
            return

        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS repositories (
                id TEXT PRIMARY KEY,
                name TEXT,
                github_url TEXT,
                status TEXT,
                progress INTEGER,
                created_at TEXT,
                files_scanned INTEGER,
                functions_indexed INTEGER,
                embeddings_generated INTEGER,
                error TEXT,
                last_indexed_at TEXT
            )
            """
        )
        try:
            cursor.execute("ALTER TABLE repositories ADD COLUMN IF NOT EXISTS last_indexed_at TEXT")
        except Exception:
            pass
        connection.commit()
        cursor.close()

    def insert_repository(self, repo_dict: dict):
        self._ensure_schema()
        connection = postgres_connection.get_connection()
        cursor = connection.cursor()
        
        cursor.execute(
            """
            INSERT INTO repositories (
                id, name, github_url, status, progress, created_at,
                files_scanned, functions_indexed, embeddings_generated, error, last_indexed_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                github_url = EXCLUDED.github_url,
                status = EXCLUDED.status,
                progress = EXCLUDED.progress,
                created_at = EXCLUDED.created_at,
                files_scanned = EXCLUDED.files_scanned,
                functions_indexed = EXCLUDED.functions_indexed,
                embeddings_generated = EXCLUDED.embeddings_generated,
                error = EXCLUDED.error,
                last_indexed_at = COALESCE(EXCLUDED.last_indexed_at, repositories.last_indexed_at)
            """,
            (
                repo_dict["id"],
                repo_dict["name"],
                repo_dict["github_url"],
                repo_dict["status"],
                repo_dict["progress"],
                repo_dict["created_at"],
                repo_dict["files_scanned"],
                repo_dict["functions_indexed"],
                repo_dict["embeddings_generated"],
                repo_dict["error"],
                repo_dict.get("last_indexed_at")
            )
        )
        connection.commit()
        cursor.close()

    def update_repository(self, repository_id: str, updates: dict):
        self._ensure_schema()
        connection = postgres_connection.get_connection()
        cursor = connection.cursor()
        
        if not updates:
            return

        set_clauses = []
        values = []
        for key, value in updates.items():
            set_clauses.append(f"{key} = %s")
            values.append(value)
            
        values.append(repository_id)
        
        query = f"UPDATE repositories SET {', '.join(set_clauses)} WHERE id = %s"
        cursor.execute(query, tuple(values))
        connection.commit()
        cursor.close()

    def get_repository(self, repository_id: str) -> dict | None:
        self._ensure_schema()
        connection = postgres_connection.get_connection()
        cursor = connection.cursor()
        
        cursor.execute(
            """
            SELECT 
                id, name, github_url, status, progress, created_at,
                files_scanned, functions_indexed, embeddings_generated, error, last_indexed_at
            FROM repositories
            WHERE id = %s
            """,
            (repository_id,)
        )
        row = cursor.fetchone()
        cursor.close()
        
        if not row:
            return None
            
        return {
            "id": row[0],
            "name": row[1],
            "github_url": row[2],
            "status": row[3],
            "progress": row[4],
            "created_at": row[5],
            "files_scanned": row[6],
            "functions_indexed": row[7],
            "embeddings_generated": row[8],
            "error": row[9],
            "last_indexed_at": row[10]
        }

    def list_repositories(self) -> list[dict]:
        self._ensure_schema()
        connection = postgres_connection.get_connection()
        cursor = connection.cursor()
        
        cursor.execute(
            """
            SELECT 
                id, name, github_url, status, progress, created_at,
                files_scanned, functions_indexed, embeddings_generated, error, last_indexed_at
            FROM repositories
            """
        )
        rows = cursor.fetchall()
        cursor.close()
        
        repos = []
        for row in rows:
            repos.append({
                "id": row[0],
                "name": row[1],
                "github_url": row[2],
                "status": row[3],
                "progress": row[4],
                "created_at": row[5],
                "files_scanned": row[6],
                "functions_indexed": row[7],
                "embeddings_generated": row[8],
                "error": row[9],
                "last_indexed_at": row[10]
            })
            
        return repos

metadata_repository = MetadataRepository()
