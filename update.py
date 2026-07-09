import re

with open("backend/services/folder_service.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Rename get_folder_overview to get_repository_guide
content = content.replace("def get_folder_overview(self, repository_id: str) -> dict:", "def get_repository_guide(self, repository_id: str) -> dict:")

# 2. Add repo_max_incoming calculation
loop_start_old = """        folders_result = []
        for folder, stats in folder_stats.items():"""
loop_start_new = """        folders_result = []
        repo_max_incoming = max((s["incoming_deps"] for s in folder_stats.values()), default=0)
        
        for folder, stats in folder_stats.items():"""
content = content.replace(loop_start_old, loop_start_new)

# 3. Update the inner loop inside `for folder, stats in folder_stats.items():`
inner_old = """            # Depends on (top-level folders)
            depends_on = set()
            for out_dep in stats["outgoing_deps_files"]:
                out_parts = out_dep.split("/")
                if len(out_parts) > 1:
                    dep_folder = out_parts[0]
                    if dep_folder != folder:
                        depends_on.add(dep_folder)
            depends_on_list = sorted(list(depends_on))
            
            # Difficulty
            difficulty = self._compute_difficulty(folder, repository["name"], stats, depends_on_list)"""

inner_new = """            # Depends on (top-level folders)
            depends_on = set()
            for out_dep in stats["outgoing_deps_files"]:
                out_parts = out_dep.split("/")
                if len(out_parts) > 1:
                    dep_folder = out_parts[0]
                    if dep_folder != folder:
                        depends_on.add(self._infer_title(dep_folder, repository["name"]))
            depends_on_list = sorted(list(depends_on))
            
            # Difficulty
            difficulty = self._compute_difficulty(folder, repository["name"], stats, depends_on_list)
            
            # Contains
            contains_set = set()
            for f in stats["files"]:
                parts = f["path"].split("/")
                if len(parts) > 1 and parts[0] == folder:
                    contains_set.add(parts[1])
            contains_list = sorted(list(contains_set))
            
            # Importance
            incoming_score = (stats["incoming_deps"] / repo_max_incoming * 100) if repo_max_incoming > 0 else 0
            score = int(min(100, incoming_score * 0.7 + percentage * 0.3))
            if stats["incoming_deps"] == repo_max_incoming and repo_max_incoming > 0:
                importance_reason = "Most internal modules depend on this folder."
            elif score > 75:
                importance_reason = "Highly referenced across the repository."
            elif percentage > 20:
                importance_reason = "Contains a significant portion of the codebase."
            else:
                importance_reason = "Standard component with isolated responsibilities."
            
            importance = {"score": score, "reason": importance_reason}
            """
content = content.replace(inner_old, inner_new)

# 4. Update the dictionary being appended to folders_result
dict_old = """            folders_result.append({
                "name": folder,
                "purpose": self._infer_purpose(folder, repository["name"]),
                "statistics": {
                    "files": file_count,
                    "functions": stats["functions"],
                    "percentage_of_repository": percentage
                },
                "dominant_file_types": dominant_file_types,
                "important_files": important_files,
                "depends_on": depends_on_list,
                "reading_priority": self._compute_reading_priority(folder, repository["name"]),
                "difficulty": difficulty
            })"""

dict_new = """            folders_result.append({
                "name": folder,
                "purpose": self._infer_purpose(folder, repository["name"]),
                "contains": contains_list,
                "responsibilities": self._infer_responsibilities(folder, repository["name"]),
                "statistics": {
                    "files": file_count,
                    "functions": stats["functions"],
                    "repository_share": percentage
                },
                "dominant_file_types": dominant_file_types,
                "important_files": important_files,
                "depends_on": depends_on_list,
                "reading_priority": self._compute_reading_priority(folder, repository["name"]),
                "difficulty": difficulty,
                "importance": importance,
                "why_read": self._infer_why_read(folder, repository["name"])
            })"""
content = content.replace(dict_old, dict_new)

# 5. Fix sorting and most_important_folder logic
sort_old = """        # Sorting
        folders_result.sort(key=lambda x: (x["reading_priority"], -x["statistics"]["functions"], x["name"]))"""
sort_new = """        # Sorting
        folders_result.sort(key=lambda x: (x["reading_priority"]["rank"], -x["statistics"]["functions"], x["name"]))"""
content = content.replace(sort_old, sort_new)

import_old = """        if folders_result:
            largest_folder = max(folders_result, key=lambda x: x["statistics"]["files"])["name"]
            most_important_folder = max(folders_result, key=lambda x: (6 - x["reading_priority"], x["statistics"]["functions"]))["name"]"""
import_new = """        if folders_result:
            largest_folder = max(folders_result, key=lambda x: x["statistics"]["files"])["name"]
            most_important_folder = max(folders_result, key=lambda x: (6 - x["reading_priority"]["rank"], x["statistics"]["functions"]))["name"]"""
content = content.replace(import_old, import_new)

# 6. Add new helper methods at the end of the class
methods_old = """    def _infer_purpose(self, folder_name: str, repository_name: str) -> str:
        name = folder_name.lower()
        if name == repository_name.lower():
            return "Core Framework"
            
        rules = {
            "app": "Application Core",
            "src": "Source Code",
            "api": "REST API Layer",
            "cli": "Command Line Interface",
            "services": "Business Logic",
            "parser": "Source Code Parser",
            "config": "Configuration",
            "database": "Database Layer",
            "db": "Database Layer",
            "repositories": "Persistence Layer",
            "models": "Data Models",
            "middleware": "Middleware",
            "auth": "Authentication",
            "utils": "Shared Utilities",
            "common": "Shared Utilities",
            "helpers": "Shared Utilities",
            "static": "Static Assets",
            "assets": "Static Assets",
            "templates": "UI Templates",
            "views": "UI Templates",
            "docs": "Documentation & Examples",
            "docs_src": "Documentation & Examples",
            "examples": "Documentation & Examples",
            "example": "Documentation & Examples",
            "tests": "Test Suite",
            "scripts": "Utility Scripts",
        }
        return rules.get(name, "General Module")

    def _compute_reading_priority(self, folder_name: str, repository_name: str) -> int:
        name = folder_name.lower()
        if name == repository_name.lower() or name in ["app", "src"]:
            return 1
            
        if name in ["api", "services", "cli"]:
            return 2
        if name in ["models", "parser", "database", "db", "repositories", "middleware", "auth"]:
            return 3
        if name in ["utils", "common", "helpers", "config", "docs", "docs_src", "examples", "example", "static", "assets", "templates", "views", "scripts"]:
            return 4
        if name in ["tests"]:
            return 5
            
        return 3"""

methods_new = """    def _infer_title(self, folder_name: str, repository_name: str) -> str:
        name = folder_name.lower()
        if name == repository_name.lower(): return "Core Framework"
        rules = {"app": "Application Core", "api": "REST API Layer", "cli": "Command Line Interface", "services": "Business Logic", "parser": "Source Code Parser", "models": "Data Models", "repositories": "Persistence Layer", "utils": "Shared Utilities", "tests": "Test Suite", "scripts": "Utility Scripts", "docs": "Documentation"}
        return rules.get(name, folder_name.title())

    def _infer_purpose(self, folder_name: str, repository_name: str) -> str:
        name = folder_name.lower()
        if name == repository_name.lower():
            return "Implements the core framework, central abstractions, and main utilities for the library."
        rules = {
            "app": "Orchestrates application startup, dependency injection, and high-level routing.",
            "api": "Exposes REST endpoints, validates incoming requests, and handles HTTP responses.",
            "cli": "Implements the command-line interface, parsing arguments, and terminal output.",
            "services": "Contains the core business logic and acts as a bridge between the API and data layers.",
            "parser": "Handles parsing of source code, AST generation, and tokenization.",
            "models": "Defines data schemas, ORM models, and type definitions used throughout the app.",
            "repositories": "Manages database interactions, abstracting away SQL queries and data persistence.",
            "utils": "Provides shared helper functions, constants, and utilities for other modules.",
            "tests": "Contains unit and integration tests to ensure code correctness and prevent regressions.",
            "scripts": "Provides standalone utility scripts for development, deployment, and data migration.",
            "docs": "Contains documentation, tutorials, and configuration for generating static sites.",
        }
        return rules.get(name, "Provides internal components and general logic for the application.")

    def _infer_responsibilities(self, folder_name: str, repository_name: str) -> list[str]:
        name = folder_name.lower()
        if name == repository_name.lower():
             return ["Core implementation", "Main abstractions", "Framework setup"]
        rules = {
            "app": ["Application initialization", "Dependency injection", "High-level routing"],
            "api": ["Request validation", "Endpoint routing", "Response serialization"],
            "cli": ["Argument parsing", "Command registration", "Terminal help generation"],
            "services": ["Business logic execution", "Service coordination", "Transaction management"],
            "parser": ["AST generation", "Tokenization", "Syntax tree traversal"],
            "models": ["Data serialization", "Schema definition", "Type hinting"],
            "repositories": ["Database connections", "Query execution", "Data persistence"],
            "utils": ["String manipulation", "Date formatting", "Common helpers"],
            "tests": ["Test fixtures", "Unit testing", "Integration testing"],
            "scripts": ["Database migration", "Deployment automation", "Data seeding"],
            "docs": ["Markdown guides", "API references", "Site configuration"],
        }
        return rules.get(name, ["General processing", "Internal helper logic"])

    def _infer_why_read(self, folder_name: str, repository_name: str) -> str:
        name = folder_name.lower()
        if name == repository_name.lower():
            return "Read this first to understand the fundamental building blocks and abstractions the rest of the project relies on."
        rules = {
            "app": "Essential for understanding how the application is wired together and started.",
            "api": "Crucial for understanding the public interface and how external clients interact with the system.",
            "cli": "Read this to understand how commands are created, registered, and executed.",
            "services": "Contains the core domain logic. Read this to understand how business rules are enforced.",
            "parser": "Key to understanding how input text is transformed into actionable data structures.",
            "models": "Important for understanding the shape of the data and database schema.",
            "repositories": "Read this to understand how data is queried and persisted.",
            "utils": "Reference this when you need to understand shared helper functions.",
            "tests": "Review these to understand expected behaviors and edge cases.",
            "scripts": "Useful for understanding operational workflows and developer tooling.",
            "docs": "Read this for high-level concepts and usage guides.",
        }
        return rules.get(name, "Read this to understand specific module-level details and implementations.")

    def _compute_reading_priority(self, folder_name: str, repository_name: str) -> dict:
        name = folder_name.lower()
        
        rank = 3
        if name == repository_name.lower() or name in ["app", "src"]:
            rank = 1
        elif name in ["api", "services", "cli"]:
            rank = 2
        elif name in ["models", "parser", "database", "db", "repositories", "middleware", "auth"]:
            rank = 3
        elif name in ["utils", "common", "helpers", "config", "docs", "docs_src", "examples", "example", "static", "assets", "templates", "views", "scripts"]:
            rank = 4
        elif name in ["tests"]:
            rank = 5
            
        labels = {
            1: "⭐ Start Here",
            2: "⭐⭐ Learn Next",
            3: "⭐⭐⭐ Optional",
            4: "⭐⭐⭐⭐ Reference",
            5: "⭐⭐⭐⭐⭐ Tests"
        }
        return {"rank": rank, "label": labels.get(rank, "⭐⭐⭐ Optional")}"""

content = content.replace(methods_old, methods_new)

with open("backend/services/folder_service.py", "w", encoding="utf-8") as f:
    f.write(content)
