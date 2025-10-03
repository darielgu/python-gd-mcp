#!/usr/bin/env python3
"""Convenience launcher for the FastAPI app using uv."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    src_dir = project_root / "src"

    # Ensure the app package can be imported when uvicorn starts.
    pythonpath = os.environ.get("PYTHONPATH", "")
    parts = [p for p in pythonpath.split(os.pathsep) if p]
    if str(src_dir) not in parts:
        parts.append(str(src_dir))
        os.environ["PYTHONPATH"] = os.pathsep.join(parts)

    cmd = [
        "uv",
        "run",
        "uvicorn",
        "app.main:app",
        "--app-dir",
        str(src_dir),
        "--host",
        os.environ.get("FASTAPI_HOST", "127.0.0.1"),
        "--port",
        os.environ.get("FASTAPI_PORT", "8003"),
    ]

    if os.environ.get("FASTAPI_RELOAD", "1") not in {"0", "false", "False"}:
        cmd.append("--reload")

    print("Launching FastAPI server...", file=sys.stderr)
    os.execvp(cmd[0], cmd)


if __name__ == "__main__":
    main()

