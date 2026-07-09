import os
import re

# 1. Update backend/app/config.py
config_path = "backend/app/config.py"
with open(config_path, "r") as f:
    config_content = f.read()

config_addition = """
    # Limits and config constants
    SOURCE_TRUNCATION_MAX_LINES: int = 30
    SOURCE_TRUNCATION_MAX_CHARACTERS: int = 1500
    
    OVERVIEW_RETRIEVAL_LIMIT: int = 10
    OVERVIEW_SAME_FILE_LIMIT: int = 2
    OVERVIEW_DEPENDENCY_LIMIT: int = 2
    OVERVIEW_CALL_NEIGHBOR_LIMIT: int = 2
    OVERVIEW_MAX_TOTAL_FUNCTIONS: int = 20
    
    CONTEXT_RETRIEVAL_LIMIT: int = 30
    CONTEXT_SAME_FILE_LIMIT: int = 3
    CONTEXT_DEPENDENCY_LIMIT: int = 3
    CONTEXT_CALL_NEIGHBOR_LIMIT: int = 4
    CONTEXT_MAX_TOTAL_FUNCTIONS: int = 12
"""
if "SOURCE_TRUNCATION_MAX_LINES" not in config_content:
    config_content = config_content.replace(
        "    model_config =", 
        config_addition + "\n    model_config ="
    )
    with open(config_path, "w") as f:
        f.write(config_content)

# 2. Update backend/repositories/metadata_repository.py
meta_repo_path = "backend/repositories/metadata_repository.py"
with open(meta_repo_path, "r") as f:
    meta_content = f.read()

meta_content = meta_content.replace("def _ensure_schema(self):", "def initialize_schema(self):")
meta_content = re.sub(r'^[ \t]*self\._ensure_schema\(\)\n?', '', meta_content, flags=re.MULTILINE)
with open(meta_repo_path, "w") as f:
    f.write(meta_content)

# 3. Update backend/repositories/embedding_repository.py
embed_repo_path = "backend/repositories/embedding_repository.py"
with open(embed_repo_path, "r") as f:
    embed_content = f.read()

embed_content = embed_content.replace("def _ensure_schema(self):", "def initialize_schema(self):")
embed_content = re.sub(r'^[ \t]*self\._ensure_schema\(\)\n?', '', embed_content, flags=re.MULTILINE)
with open(embed_repo_path, "w") as f:
    f.write(embed_content)

# 4. Update backend/app/main.py
main_path = "backend/app/main.py"
with open(main_path, "r") as f:
    main_content = f.read()

if "metadata_repository.initialize_schema()" not in main_content:
    imports = """from repositories.metadata_repository import metadata_repository
from repositories.embedding_repository import embedding_repository
"""
    main_content = imports + main_content
    
    init_code = """    postgres_connection.connect()
    neo4j_connection.connect()
    
    # Initialize schemas exactly once
    metadata_repository.initialize_schema()
    embedding_repository.initialize_schema()
"""
    main_content = main_content.replace("    postgres_connection.connect()\n    neo4j_connection.connect()\n", init_code)
    with open(main_path, "w") as f:
        f.write(main_content)

# 5. Update backend/services/llm_service.py
llm_service_path = "backend/services/llm_service.py"
with open(llm_service_path, "r") as f:
    llm_content = f.read()

if "def extract_json" not in llm_content:
    if "import json" not in llm_content:
        llm_content = "import json\n" + llm_content
    
    json_method = """
    def extract_json(self, text: str) -> dict | list:
        clean_text = text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        elif clean_text.startswith("```"):
            clean_text = clean_text[3:]
            
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
            
        return json.loads(clean_text.strip())
"""
    llm_content = llm_content + json_method
    with open(llm_service_path, "w") as f:
        f.write(llm_content)

# 6. Update backend/services/prompt_builder.py
prompt_builder_path = "backend/services/prompt_builder.py"
with open(prompt_builder_path, "r") as f:
    prompt_content = f.read()

if "from app.config import settings" not in prompt_content:
    prompt_content = "from app.config import settings\n" + prompt_content

if "OVERVIEW_QUESTION" not in prompt_content:
    prompt_content = prompt_content.replace("class PromptBuilder:", "class PromptBuilder:\n    OVERVIEW_QUESTION = \"Explain the architecture, main components, and purpose of this repository.\"\n")

prompt_content = prompt_content.replace("max_lines: int = 30", "max_lines: int = settings.SOURCE_TRUNCATION_MAX_LINES")
prompt_content = prompt_content.replace("max_characters: int = 1500", "max_characters: int = settings.SOURCE_TRUNCATION_MAX_CHARACTERS")

with open(prompt_builder_path, "w") as f:
    f.write(prompt_content)

# 7. Update backend/services/overview_service.py
overview_service_path = "backend/services/overview_service.py"
with open(overview_service_path, "r") as f:
    overview_content = f.read()

if "from app.config import settings" not in overview_content:
    overview_content = "from app.config import settings\n" + overview_content

overview_content = re.sub(r'question\s*=\s*"Explain the architecture, main components, and purpose of this repository."', 'question = prompt_builder.OVERVIEW_QUESTION', overview_content)

overview_content = re.sub(r'retrieval_limit=\d+', 'retrieval_limit=settings.OVERVIEW_RETRIEVAL_LIMIT', overview_content)
overview_content = re.sub(r'same_file_limit=\d+', 'same_file_limit=settings.OVERVIEW_SAME_FILE_LIMIT', overview_content)
overview_content = re.sub(r'dependency_limit=\d+', 'dependency_limit=settings.OVERVIEW_DEPENDENCY_LIMIT', overview_content)
overview_content = re.sub(r'call_neighbor_limit=\d+', 'call_neighbor_limit=settings.OVERVIEW_CALL_NEIGHBOR_LIMIT', overview_content)
overview_content = re.sub(r'max_total_functions=\d+', 'max_total_functions=settings.OVERVIEW_MAX_TOTAL_FUNCTIONS', overview_content)

old_json_logic = '''        try:
            answer = llm_service.generate_answer(prompt)
            clean_answer = answer.strip()
            if clean_answer.startswith("```json"):
                clean_answer = clean_answer[7:]
            if clean_answer.endswith("```"):
                clean_answer = clean_answer[:-3]
            
            clean_answer = clean_answer.strip()
            return json.loads(clean_answer)
        except json.JSONDecodeError:
            return {"error": "Failed to parse overview JSON", "raw_response": answer}
        except Exception as error:
            return {"error": f"Failed to generate overview: {error}"}'''

new_json_logic = '''        try:
            answer = llm_service.generate_answer(prompt)
            return llm_service.extract_json(answer)
        except json.JSONDecodeError:
            return {"error": "Failed to parse overview JSON", "raw_response": answer}
        except Exception as error:
            return {"error": f"Failed to generate overview: {error}"}'''

overview_content = overview_content.replace(old_json_logic, new_json_logic)
with open(overview_service_path, "w") as f:
    f.write(overview_content)

# 8. Update backend/services/context_builder.py
context_builder_path = "backend/services/context_builder.py"
with open(context_builder_path, "r") as f:
    context_content = f.read()

if "from app.config import settings" not in context_content:
    context_content = "from app.config import settings\n" + context_content

context_content = re.sub(r'retrieval_limit: int = 30', 'retrieval_limit: int = settings.CONTEXT_RETRIEVAL_LIMIT', context_content)
context_content = re.sub(r'same_file_limit: int = 3', 'same_file_limit: int = settings.CONTEXT_SAME_FILE_LIMIT', context_content)
context_content = re.sub(r'dependency_limit: int = 3', 'dependency_limit: int = settings.CONTEXT_DEPENDENCY_LIMIT', context_content)
context_content = re.sub(r'call_neighbor_limit: int = 4', 'call_neighbor_limit: int = settings.CONTEXT_CALL_NEIGHBOR_LIMIT', context_content)
context_content = re.sub(r'max_total_functions: int = 12', 'max_total_functions: int = settings.CONTEXT_MAX_TOTAL_FUNCTIONS', context_content)

with open(context_builder_path, "w") as f:
    f.write(context_content)

print("Cleanup complete!")
