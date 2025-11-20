from datetime import datetime
from typing import Dict, Any


def format_metrics_line(timestamp: datetime, metrics: Dict[str, Any]) -> str:
    lines = [f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}]"]
    for key, value in metrics.items():
        lines.append(f"  {key:15} = {value}")
    return "\n".join(lines)



def write_line(line: str, output: str) -> None:
    if output == "stdout":
        print(line)
    else:
        with open(output, "a", encoding="utf-8") as f:
            f.write(line + "\n")
