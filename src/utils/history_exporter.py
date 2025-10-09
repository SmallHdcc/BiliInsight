"""Utilities for exporting watch history to structured files."""
from __future__ import annotations

import csv
import os
import time
from pathlib import Path
from typing import Any, Dict, Iterable

__all__ = ["export_history_to_csv"]


def export_history_to_csv(history: Iterable[Dict[str, Any]], output_dir: str | os.PathLike[str] = "exports") -> Path:
    """Export watch history to a CSV file.

    Args:
        history: Iterable of history records.
        output_dir: Directory to store exported CSV files.

    Returns:
        Path to the exported CSV file.
    """
    records = list(history)
    if not records:
        raise ValueError("history is empty")

    export_dir = Path(output_dir)
    export_dir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    file_path = export_dir / f"bili_history_{timestamp}.csv"

    fieldnames = [
        "title",
        "author",
        "category",
        "view_time",
        "watch_duration_seconds",
        "total_duration_seconds",
        "bvid",
        "uri",
    ]

    with file_path.open("w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for item in records:
            writer.writerow(
                {
                    "title": item.get("title", ""),
                    "author": item.get("author_name") or item.get("author", ""),
                    "category": item.get("tag_name", ""),
                    "view_time": _format_timestamp(item.get("view_at")),
                    "watch_duration_seconds": _get_watch_seconds(item),
                    "total_duration_seconds": _get_total_duration(item),
                    "bvid": item.get("bvid") or item.get("history", {}).get("bvid", ""),
                    "uri": item.get("uri") or item.get("short_link", ""),
                }
            )

    return file_path


def _format_timestamp(timestamp: Any) -> str:
    if not timestamp:
        return ""
    try:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(timestamp)))
    except (TypeError, ValueError):
        return ""


def _get_watch_seconds(item: Dict[str, Any]) -> int:
    progress = int(item.get("progress", 0) or 0)
    if progress < 0:
        progress = int(item.get("duration", 0) or 0)
    return max(progress, 0)


def _get_total_duration(item: Dict[str, Any]) -> int:
    try:
        duration = int(item.get("duration", 0) or 0)
    except (TypeError, ValueError):
        duration = 0
    return max(duration, _get_watch_seconds(item))
