from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from backend.blockchain.contracts import ContractManager
from backend.blockchain.reputation_poster import ReputationPoster
from backend.utils.config import ROOT_DIR, get_settings


CHECKPOINTS_FILE = ROOT_DIR / "checkpoints.jsonl"
FEEDBACK_FILE = ROOT_DIR / "reputation-feedback.jsonl"


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def existing_validation_hashes(agent_id: int) -> set[str]:
    hashes: set[str] = set()
    for row in load_jsonl(FEEDBACK_FILE):
        if row.get("agent_id") != agent_id:
            continue
        if row.get("feedback_type") != "VALIDATION_SCORE":
            continue
        if not row.get("feedback_tx_hash"):
            continue
        outcome_hash = row.get("outcome_hash")
        if isinstance(outcome_hash, str) and outcome_hash:
            hashes.add(outcome_hash.lower().removeprefix("0x"))
    return hashes


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay missing validation checkpoints into reputation feedback.")
    parser.add_argument("--limit", type=int, default=0, help="Process at most this many missing checkpoints (0 = all).")
    parser.add_argument("--dry-run", action="store_true", help="Compute and print what would be posted without sending transactions.")
    args = parser.parse_args()

    settings = get_settings()
    checkpoints = load_jsonl(CHECKPOINTS_FILE)
    if not checkpoints:
        print("No checkpoints found.")
        return

    already_posted = existing_validation_hashes(settings.agent_id)
    pending = [
        row
        for row in checkpoints
        if row.get("agent_id") == settings.agent_id
        and isinstance(row.get("checkpoint_hash"), str)
        and row["checkpoint_hash"].lower().removeprefix("0x") not in already_posted
    ]
    if args.limit > 0:
        pending = pending[: args.limit]

    print(f"Agent ID: {settings.agent_id}")
    print(f"Checkpoints found: {len(checkpoints)}")
    print(f"Missing validation feedback entries: {len(pending)}")

    if not pending:
        print("Nothing to backfill.")
        return

    if args.dry_run:
        for row in pending[:10]:
            print(
                f"DRY RUN | action={row.get('action')} pair={row.get('pair')} "
                f"score={row.get('score')} checkpoint={row.get('checkpoint_hash')}"
            )
        if len(pending) > 10:
            print(f"... and {len(pending) - 10} more")
        return

    cm = ContractManager(settings)
    poster = ReputationPoster(cm)
    posted = 0
    failed = 0

    for row in pending:
        result = poster.post_validation_feedback(
            checkpoint_hash=row["checkpoint_hash"],
            validation_score=int(row.get("score", 0)),
            action=str(row.get("action", "HOLD")),
            symbol=str(row.get("pair", settings.symbol)),
        )
        if result.get("feedback_tx_hash"):
            posted += 1
            print(
                f"POSTED | action={row.get('action')} pair={row.get('pair')} "
                f"score={row.get('score')} tx={result['feedback_tx_hash']}"
            )
        else:
            failed += 1
            print(
                f"FAILED | action={row.get('action')} pair={row.get('pair')} "
                f"score={row.get('score')} checkpoint={row.get('checkpoint_hash')}"
            )

    print(f"Completed. Posted={posted} Failed={failed}")
    if cm.connected:
        try:
            avg = poster.get_average_reputation_score()
            print(f"Current on-chain average reputation score: {avg}")
        except Exception:
            pass


if __name__ == "__main__":
    main()
