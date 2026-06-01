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
Investigate the error by reading the relevant source files using the available tools.

Use fetch_file to read files referenced in the stack trace.
Use list_repo_files if you need to find a file whose path you are unsure of.
Follow the call chain as needed — if a function calls another function that may be the cause, fetch that file too.

Investigation rules:
- Only fetch files directly relevant to the error
- Do not fetch more than 10 files per investigation
- Stop when you have enough context to explain the root cause
- Say "likely" when uncertain

When you have finished investigating and are ready to write the final report, you MUST:
- Output ONLY the structured report below — no preamble, no "based on my analysis", no thinking out loud
- Start your response directly with ## What Failed
- Use exactly these three sections and no others:

## What Failed
One or two sentences. What broke and where in the code.

## Root Cause
The actual reason it failed. Reference specific files, functions, and line numbers.

## Suggested Fix
Concrete code change or action the developer should take. Use a code block if showing code.
"""

REPORT_TRIGGER = (
    "You have read enough files. "
    "Now write the final investigation report. "
    "Output ONLY the three sections: ## What Failed, ## Root Cause, ## Suggested Fix. "
    "Do not include any preamble or explanation outside these sections. "
    "Start your response with ## What Failed."
)

MAX_HOPS = 10


def run_investigation(
    repo_full_name: str,
    stack_trace: str,
    token: str,
    on_tool_call=None
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
                f"Investigate this error in the repository `{repo_full_name}`.\n\n"
                f"**Stack trace / error:**\n```\n{stack_trace}\n```\n\n"
                f"Start by reading the files referenced in the stack trace, "
                f"then follow the call chain until you understand the root cause."
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

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            # Model finished on its own — extract text
            for block in response.content:
                if hasattr(block, "text"):
                    text = block.text.strip()
                    # If it starts with a preamble, trigger a correction pass
                    if not text.startswith("## What Failed"):
                        return _force_structured_report(messages, tools)
                    return text
            return "Investigation complete but no report was generated."

        if response.stop_reason == "tool_use":
            tool_results = []

            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input

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

    # Hit max hops — force a report from what we have
    return _force_structured_report(messages, tools)


def _force_structured_report(messages: list, tools: list) -> str:
    """
    Send a follow-up message that forces the model to output only
    the structured report, no preamble.
    """
    messages_with_trigger = messages + [
        {"role": "user", "content": REPORT_TRIGGER}
    ]

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        tools=tools,
        messages=messages_with_trigger
    )

    for block in response.content:
        if hasattr(block, "text"):
            return block.text.strip()

    return "Investigation complete but no report was generated."
