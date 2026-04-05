from __future__ import annotations

from pathlib import Path
from typing import Any

from .models import VideoMetadata


def probe_video_metadata(video_path: str) -> VideoMetadata:
    resolved_path = Path(video_path).resolve(strict=False)
    if not resolved_path.is_file():
        raise ValueError(f"Video path not found: {video_path}")

    try:
        from scenedetect import open_video
    except Exception as exc:
        raise RuntimeError(
            "Video metadata probing requires PySceneDetect. Install `scenedetect[opencv]`."
        ) from exc

    video = open_video(str(resolved_path))
    try:
        fps = _coerce_positive_float(getattr(video, "frame_rate", None) or getattr(video, "fps", None))
        duration = getattr(video, "duration", None)
        total_frames = _coerce_int(getattr(duration, "frame_num", None)) if duration is not None else None
        duration_sec = None
        if duration is not None and hasattr(duration, "get_seconds"):
            try:
                duration_sec = float(duration.get_seconds())
            except Exception:
                duration_sec = None
        if duration_sec is None and fps and total_frames:
            duration_sec = float(total_frames) / float(fps)
        return VideoMetadata(
            source_video_path=str(resolved_path),
            fps=fps,
            total_frames=total_frames,
            duration_sec=duration_sec,
        )
    finally:
        for method_name in ("close", "release"):
            method = getattr(video, method_name, None)
            if callable(method):
                try:
                    method()
                except Exception:
                    pass


def _coerce_positive_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number <= 0:
        return None
    return number


def _coerce_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
