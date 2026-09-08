"""Small repeatable smoke evaluation for the spoiler-free assistant.

Run with:
    python evaluate.py

The checks measure two user-facing properties: grounded episode answers and
the anti-spoiler boundary. The output can be used as evidence in the Nebius
challenge submission.
"""

import time

from main_agent import get_response_stream


CASES = [
    {
        "name": "Episode summary is grounded",
        "prompt": "What happens in Episode 1?",
        "expected": ("episode 1", "pilot"),
    },
    {
        "name": "Episode 2 summary is grounded",
        "prompt": "What happens in Episode 2?",
        "expected": ("episode 2", "models and mortals"),
    },
    {
        "name": "Future episode is blocked",
        "prompt": "What happens in Episode 3?",
        "expected": ("spoiler", "cannot"),
    },
]


def run_case(case: dict) -> tuple[bool, float, str]:
    started = time.perf_counter()
    response = ""
    for event_type, data in get_response_stream(
        [{"role": "user", "content": case["prompt"]}],
        current_episode_id=2,
    ):
        if event_type == "token":
            response += data

    elapsed_ms = (time.perf_counter() - started) * 1000
    normalized = response.lower()
    passed = any(term in normalized for term in case["expected"])
    return passed, elapsed_ms, response.replace("\n", " ")


def main() -> None:
    passed_count = 0
    total_ms = 0.0

    print("Where Was AI? evaluation")
    print("Provider is configured through AI_PROVIDER in .env\n")

    for case in CASES:
        passed, elapsed_ms, response = run_case(case)
        passed_count += int(passed)
        total_ms += elapsed_ms
        marker = "PASS" if passed else "FAIL"
        print(f"[{marker}] {case['name']} ({elapsed_ms:.0f} ms)")
        print(f"      {response[:240]}{'...' if len(response) > 240 else ''}")

    print(f"\nResult: {passed_count}/{len(CASES)} checks passed")
    print(f"Average response time: {total_ms / len(CASES):.0f} ms")


if __name__ == "__main__":
    main()
