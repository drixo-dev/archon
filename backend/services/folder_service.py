from services.graph_service import graph_service
from services.repository_service import repository_service

class FolderService:
    def get_repository_guide(self, repository_id: str) -> dict:
        repository = repository_service.get_repository(repository_id)
        if not repository:
            return None

        files_data = graph_service.get_file_statistics_for_folders(repository_id)
        
        total_files_in_repo = len(files_data)
        
        folder_stats = {}
        for file_data in files_data:
            path = file_data["path"]
            parts = path.split("/")
            if len(parts) <= 1:
                continue # Skip root files
            
            folder = parts[0]
            if folder not in folder_stats:
                folder_stats[folder] = {
                    "files": [],
                    "functions": 0,
                    "incoming_deps": 0,
                    "outgoing_deps_files": set(),
                }
            
            folder_stats[folder]["files"].append(file_data)
            folder_stats[folder]["functions"] += file_data["function_count"]
            folder_stats[folder]["incoming_deps"] += file_data["incoming_deps"]
            for out_dep in file_data["outgoing_deps"]:
                folder_stats[folder]["outgoing_deps_files"].add(out_dep)

        # Calculate integer percentages using Largest Remainder Method to ensure they sum correctly to 100
        integer_percentages = {}
        if total_files_in_repo > 0:
            root_files_count = total_files_in_repo - sum(len(s["files"]) for s in folder_stats.values())
            remainders = []
            
            for f_name, s in folder_stats.items():
                exact = (len(s["files"]) / total_files_in_repo) * 100
                integer_percentages[f_name] = int(exact)
                remainders.append((f_name, exact - int(exact)))
                
            if root_files_count > 0:
                exact = (root_files_count / total_files_in_repo) * 100
                integer_percentages["__root__"] = int(exact)
                remainders.append(("__root__", exact - int(exact)))
                
            shortfall = 100 - sum(integer_percentages.values())
            # Sort remainders desc. On tie, sort by name for determinism.
            remainders.sort(key=lambda x: (-x[1], x[0]))
            
            for i in range(shortfall):
                if i < len(remainders):
                    integer_percentages[remainders[i][0]] += 1

        folders_result = []
        repo_max_incoming = max((s["incoming_deps"] for s in folder_stats.values()), default=0)
        
        for folder, stats in folder_stats.items():
            file_count = len(stats["files"])
            percentage = integer_percentages.get(folder, 0)
            
            # Dominant file types
            extensions = {}
            for f in stats["files"]:
                ext = "." + f["path"].split(".")[-1] if "." in f["path"] else "none"
                extensions[ext] = extensions.get(ext, 0) + 1
            # Sort by count desc, then by extension name asc for determinism
            sorted_exts = sorted(extensions.items(), key=lambda x: (-x[1], x[0]))
            dominant_file_types = [sorted_exts[0][0]] if sorted_exts else []

            # Important files
            max_fc = max((f["function_count"] for f in stats["files"]), default=0)
            max_ic = max((f["incoming_deps"] for f in stats["files"]), default=0)

            # Sort by function + incoming desc, then by name for stable sort
            sorted_files = sorted(stats["files"], key=lambda x: (-(x["function_count"] + x["incoming_deps"]), x["path"]))
            important_files = []
            for f in sorted_files[:2]:
                filename = f["path"].split("/")[-1]
                
                if filename in ["main.py", "__init__.py", "index.py"]:
                    reason = "Entry point of this folder."
                elif filename in ["core.py", "base.py"]:
                    reason = "Central implementation file."
                elif f["incoming_deps"] == max_ic and max_ic > 0:
                    reason = "Referenced by the largest number of files."
                elif f["function_count"] == max_fc and max_fc > 0:
                    reason = "Highest function count in this folder."
                elif f["function_count"] > 0:
                    reason = "Contains most exported functionality."
                else:
                    reason = "Defines core public APIs."
                    
                important_files.append({
                    "name": filename,
                    "reason": reason
                })

            # Depends on (top-level folders)
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
            

            folders_result.append({
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
            })

        # Sorting
        folders_result.sort(key=lambda x: (x["reading_priority"]["rank"], -x["statistics"]["functions"], x["name"]))

        # Summary
        largest_folder = ""
        most_important_folder = ""
        recommended_start_folder = ""
        estimated_learning_order = []
        
        if folders_result:
            largest_folder = max(folders_result, key=lambda x: x["statistics"]["files"])["name"]
            most_important_folder = max(folders_result, key=lambda x: (6 - x["reading_priority"]["rank"], x["statistics"]["functions"]))["name"]
            estimated_learning_order = [f["name"] for f in folders_result]
            recommended_start_folder = estimated_learning_order[0]

        return {
            "repository": {
                "id": repository["id"],
                "name": repository["name"]
            },
            "summary": {
                "total_folders": len(folders_result),
                "largest_folder": largest_folder,
                "most_important_folder": most_important_folder,
                "recommended_start_folder": recommended_start_folder,
                "estimated_learning_order": estimated_learning_order
            },
            "folders": folders_result
        }

    def _infer_title(self, folder_name: str, repository_name: str) -> str:
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
        return {"rank": rank, "label": labels.get(rank, "⭐⭐⭐ Optional")}

    def _compute_difficulty(self, folder_name: str, repository_name: str, stats: dict, depends_on: list) -> str:
        name = folder_name.lower()
        
        if name in ["api", "examples", "example", "tests", "docs", "docs_src"]:
            return "Beginner"
            
        if name == repository_name.lower() or name in ["parser", "app", "src", "core"]:
            return "Advanced"
            
        if name in ["services", "utils", "common", "helpers", "middleware"]:
            return "Intermediate"
            
        score = stats["functions"] + len(depends_on) * 5 + stats["incoming_deps"]
        if score > 50:
            return "Advanced"
        elif score > 20:
            return "Intermediate"
        else:
            return "Beginner"

folder_service = FolderService()
