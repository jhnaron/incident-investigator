# The agent loop
# Drives the investigation using Claude + tool use

import anthropic
import os
from dotenv import load_dotenv
from app.tools import make_tools, execute_tool

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are an expert software engineer specializing in debugging and root cause analysis.

You have been given a GitHub repository and a stack trace or error message.
Your job is to investigate the error by reading the relevant source files and identify:
1. What failed and where
2. Why it happened (root cause)
3. A concrete suggested fix

Use the fetch_file tool to read files referenced in the stack trace.
Use list_repo_files if you need to find a file whose path you are unsure of.
Follow the call chain as needed — if a function calls another function that may be the cause, fetch that file too.

Rules:
- Only fetch files that are directly relevant to the error
- Do not fetch more than 10 files per investigation
- Stop when you have enough context to explain the root cause
- Be honest about confidence level — say "likely" when uncertain
- Format your final report with clear sections:
  ## What Failed
  ## Root Cause
  ## Suggested Fix
"""

MAX_HOPS = 10

def run_investigation(
    repo_full_name: str,
    stack_trace: str,
    token: str,
    on_tool_call=None  # callback to stream steps to UI
) -> str:
    """
    Run the agent loop. Returns the final investigation report.
    on_tool_call(tool_name, file_path) is called each time the agent uses a tool.
    """

    tools = make_tools(token, repo_full_name)
    messages = [
        {
            "role": "user",
            "content": (
                f"Please investigate this error in the repository `{repo_full_name}`.\n\n"
                f"**Stack trace / error:**\n```\n{stack_trace}\n```\n\n"
                f"Start by identifying the relevant files from the stack trace, "
                f"then read them to find the root cause."
            )
        }
    ]

    hops = 0

    while hops < MAX_HOPS:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages
        )

        # Append assistant response to history
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            # Extract final text response
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return "Investigation complete but no report was generated."

        if response.stop_reason == "tool_use":
            tool_results = []

            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input

                    # Notify UI
                    if on_tool_call:
                        label = tool_input.get("file_path", "") or tool_name
                        on_tool_call(tool_name, label)

                    result = execute_tool(tool_name, tool_input, token, repo_full_name)

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            messages.append({"role": "user", "content": tool_results})
            hops += 1

    return "Investigation stopped — maximum file reads reached. See partial findings above."
