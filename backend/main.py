from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

import uvicorn


def run() -> None:
    uvicorn.run("backend.api.server:create_app", host="0.0.0.0", port=8000, factory=True)


if __name__ == "__main__":
    run()
