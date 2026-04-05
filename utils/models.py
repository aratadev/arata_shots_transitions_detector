from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class VideoMetadata:
    source_video_path: str
    fps: float | None
    total_frames: int | None = None
    duration_sec: float | None = None


@dataclass(frozen=True)
class ShotBoundary:
    index: int
    start_frame: int
    end_frame: int
    start_sec: float
    end_sec: float


@dataclass(frozen=True)
class TransitionBoundary:
    index: int
    start_frame: int
    end_frame: int
    start_sec: float
    end_sec: float
    transition_type: str = "gradual"


@dataclass(frozen=True)
class ShotBoundaryResult:
    video: VideoMetadata
    shots: tuple[ShotBoundary, ...]
    detector: str = "transnetv2"
    version: int = 1
    parameters: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TransitionBoundaryResult:
    video: VideoMetadata
    transitions: tuple[TransitionBoundary, ...]
    detector: str = "pyscenedetect-threshold"
    version: int = 1
    parameters: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExportedFile:
    label: str
    file_path: str
    relative_output_path: str
    filename: str

    def to_ui_payload(self) -> dict[str, str]:
        return {
            "label": self.label,
            "filename": self.filename,
            "file_path": self.file_path,
            "relative_output_path": self.relative_output_path,
        }


@dataclass(frozen=True)
class BoundaryTextExportResult:
    shots_file: ExportedFile
    transitions_file: ExportedFile
