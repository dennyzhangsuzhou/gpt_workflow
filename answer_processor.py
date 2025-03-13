import json
from typing import Any, Union, Dict, List


def post_run(answer: str) -> Union[Dict[str, Any], List[Any], None]:
    if "```" in answer:
        start_pos = answer.find("```")
        first_newline = answer.find("\n", start_pos)
        if first_newline != -1:
            end_pos = answer.rfind("```")
            if end_pos > first_newline:
                answer = answer[first_newline + 1 : end_pos].strip()
            else:
                answer = answer[first_newline + 1 :].strip()

    try:
        return json.loads(answer)
    except json.JSONDecodeError:
        return None
