# Placeholder — stack trace parser
# Extracts file paths, line numbers, and function names from a raw stack trace

import re
from dataclasses import dataclass

@dataclass
class StackFrame:
    file_path: str
    line_number: int | None
    function_name: str | None

def parse_stack_trace(stack_trace: str) -> list[StackFrame]:
    """
    Parse a raw stack trace string into a list of StackFrames.
    Supports Python tracebacks for now.
    """
    frames = []

    # Python traceback pattern: File "path/to/file.py", line N, in function_name
    python_pattern = re.compile(
        r'File "([^"]+)", line (\d+)(?:, in (.+))?'
    )

    for match in python_pattern.finditer(stack_trace):
        file_path = match.group(1)
        line_number = int(match.group(2))
        function_name = match.group(3).strip() if match.group(3) else None

        # Skip stdlib and venv paths
        if any(skip in file_path for skip in ["site-packages", "/usr/lib", "<"]):
            continue

        frames.append(StackFrame(
            file_path=file_path,
            line_number=line_number,
            function_name=function_name
        ))

    return frames
