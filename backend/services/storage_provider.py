from __future__ import annotations

import re
from pathlib import Path
from typing import BinaryIO

from backend.core.config import settings


class StorageProvider:
    def __init__(self) -> None:
        self.base_dir = Path(settings.local_upload_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _safe_name(self, filename: str) -> str:
        normalized = re.sub(r"[^A-Za-z0-9._-]", "-", filename).strip("-.")
        return normalized or "upload.bin"

    def save_text_artifact(self, folder: str, filename: str, content: str) -> str:
        target_dir = self.base_dir / folder
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / self._safe_name(filename)
        target_path.write_text(content, encoding="utf-8")
        return str(target_path)

    def save_binary_artifact(self, folder: str, filename: str, stream: BinaryIO) -> str:
        target_dir = self.base_dir / folder
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / self._safe_name(filename)
        with target_path.open("wb") as handle:
            handle.write(stream.read())
        return str(target_path)
