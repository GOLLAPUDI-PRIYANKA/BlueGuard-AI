from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class EnvironmentAdapter:
    """Loads the small sample environmental dataset used by the MVP."""

    def __init__(self, data_file: Optional[str | Path] = None) -> None:
        if data_file is None:
            data_file = (
                Path(__file__).resolve().parents[1]
                / "environmental"
                / "arabian_sea_aug2026.json"
            )
        self.data_file = Path(data_file)

    def load(self) -> List[Dict[str, Any]]:
        if not self.data_file.exists():
            return []

        with self.data_file.open("r", encoding="utf-8") as f:
            payload = json.load(f)

        if isinstance(payload, dict):
            rows = payload.get("records", [])
        else:
            rows = payload

        return rows if isinstance(rows, list) else []

    def get_for_time_range(
        self,
        start_time: str,
        end_time: str,
    ) -> List[Dict[str, Any]]:
        rows = self.load()
        start = self._parse(start_time)
        end = self._parse(end_time)

        result = []
        for row in rows:
            try:
                ts = self._parse(row["timestamp"])
            except (KeyError, ValueError, TypeError):
                continue

            if start <= ts <= end:
                result.append(row)

        return result

    @staticmethod
    def _parse(value: str) -> datetime:
        text = value.strip()
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"

        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        return dt.astimezone(timezone.utc)
