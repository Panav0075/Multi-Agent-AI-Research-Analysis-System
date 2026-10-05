import argparse
import json
from pathlib import Path

from .orchestrator import MultiAgentOrchestrator


def main():
    parser = argparse.ArgumentParser(description="Run the multi-agent workflow.")
    parser.add_argument("request")
    parser.add_argument("--trace", default=None)
    args = parser.parse_args()

    system = MultiAgentOrchestrator.from_config("config.yaml")
    result = system.run(args.request)

    print("\nFINAL ANSWER")
    print("============")
    print(result.final_answer)

    print("\nEXECUTION TRACE")
    print("===============")
    for event in result.trace:
        print(f"{event.agent:14} {event.status:20} {event.summary}")

    if args.trace:
        path = Path(args.trace)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(result.to_dict(), indent=2),
            encoding="utf-8",
        )
        print(f"\nTrace saved -> {path}")


if __name__ == "__main__":
    main()
