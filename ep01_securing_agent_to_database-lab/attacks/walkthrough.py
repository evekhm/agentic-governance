"""Interactive chapter-by-chapter & before/after attack walkthrough CLI."""

from __future__ import annotations

import argparse
from attacks.payloads import ATTACK_SCENARIOS


def main() -> None:
    parser = argparse.ArgumentParser(description="Episode 01 Reference Lab Walkthrough")
    parser.add_argument("--target", choices=["track-a", "track-b"], default="track-a")
    parser.add_argument("--threat", choices=list(ATTACK_SCENARIOS.keys()), default="T1")
    args = parser.parse_args()
    scenario = ATTACK_SCENARIOS[args.threat]
    print(f"[{args.target}] {scenario.threat_id}: {scenario.title} (expected layer: {scenario.expected_blocked_layer})")
    print(f"Prompt: {scenario.prompt}")


if __name__ == "__main__":
    main()
