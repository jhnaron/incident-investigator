# Tool definitions for the Claude agent
# These are the functions Claude can call during investigation

from app.github_client import get_file_content, get_repo_tree

# Noise files to skip automatically
SKIP_EXTENSIONS = {
    ".lock", ".min.js", ".min.css", ".map",
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico",
    ".woff", ".woff2", ".ttf", ".eot"
}

SKIP_FILENAMES = {
    "package-lock.json", "yarn.lock", "poetry.lock",
    "uv.lock", "Pipfile.lock", ".DS_Store"
}

def should_skip(file_path: str) -> bool:
    import os
    _, ext = os.path.splitext(file_path)
    filename = os.path.basename(file_path)
    return ext in SKIP_EXTENSIONS or filename in SKIP_FILENAMES

def make_tools(token: str, repo_full_name: str) -> list[dict]:
    """
    Returns the tool definitions Claude will receive.
    Token and repo are captured in the closures below.
    """
    return [
        {
            "name": "fetch_file",
            "description": (
                "Fetch the content of a specific file from the GitHub repository. "
                "Use this to read source files referenced in the stack trace or "
                "related files that may contain the root cause."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file relative to the repo root. Example: src/api/routes.py"
                    }
                },
                "required": ["file_path"]
            }
        },
        {
            "name": "list_repo_files",
            "description": (
                "List all files in the repository. "
                "Use this when you need to find a file but don't know its exact path, "
                "or to understand the project structure."
            ),
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    ]

def execute_tool(tool_name: str, tool_input: dict, token: str, repo_full_name: str) -> str:
    """Execute a tool call and return the result as a string."""

    if tool_name == "fetch_file":
        file_path = tool_input.get("file_path", "")

        if should_skip(file_path):
            return f"Skipped {file_path} — noise file."

        content = get_file_content(token, repo_full_name, file_path)
        if content is None:
            return f"Could not fetch {file_path}. File may not exist or is inaccessible."

        # Cap file size to avoid blowing context
        MAX_CHARS = 8000
        if len(content) > MAX_CHARS:
            content = content[:MAX_CHARS] + f"\n... [truncated at {MAX_CHARS} chars]"

        return f"Contents of {file_path}:\n\n{content}"

    elif tool_name == "list_repo_files":
        files = get_repo_tree(token, repo_full_name)
        filtered = [f for f in files if not should_skip(f)]
        return "Repository files:\n" + "\n".join(filtered)

    return f"Unknown tool: {tool_name}"
