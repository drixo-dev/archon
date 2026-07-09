from services.graph_service import graph_service
from services.repository_service import repository_service

class FolderService:
    def get_folder_overview(self, repository_id: str) -> dict:
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
                        depends_on.add(dep_folder)
            depends_on_list = sorted(list(depends_on))
            
            # Difficulty
            difficulty = self._compute_difficulty(folder, repository["name"], stats, depends_on_list)

            folders_result.append({
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
            })

        # Sorting
        folders_result.sort(key=lambda x: (x["reading_priority"], -x["statistics"]["functions"], x["name"]))

        # Summary
        largest_folder = ""
        most_important_folder = ""
        recommended_start_folder = ""
        estimated_learning_order = []
        
        if folders_result:
            largest_folder = max(folders_result, key=lambda x: x["statistics"]["files"])["name"]
            most_important_folder = max(folders_result, key=lambda x: (6 - x["reading_priority"], x["statistics"]["functions"]))["name"]
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

    def _infer_purpose(self, folder_name: str, repository_name: str) -> str:
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
            
        return 3

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
