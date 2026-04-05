from __future__ import annotations

import math
from typing import Any

from ..utils.models import ShotBoundary, ShotBoundaryResult, VideoMetadata
from ..utils.path_utils import resolve_video_path
from ..utils.video_metadata import probe_video_metadata


class TransNetV2ShotDetectionService:
    def detect_shots(
        self,
        video_path: str,
        threshold: float,
        min_scene_length_frames: int,
        device: str,
    ) -> ShotBoundaryResult:
        resolved_path = resolve_video_path(video_path)
        self._validate_video_path(video_path, resolved_path)
        source_metadata = probe_video_metadata(resolved_path)

        transnet_cls = self._require_transnet()
        model = self._build_model(transnet_cls, device)
        raw_result = self._run_inference(model, resolved_path, threshold)
        raw_scenes, fps = self._extract_scenes_and_fps(raw_result)

        if fps is None:
            fps = source_metadata.fps
        if fps is None or fps <= 0:
            raise RuntimeError(
                "Unable to determine FPS for TransNetV2 results. "
                "Ensure the video is readable and PySceneDetect is installed with a video backend."
            )

        merged_scenes = self._apply_min_scene_length(raw_scenes, fps, min_scene_length_frames)
        shot_boundaries = tuple(
            ShotBoundary(
                index=index,
                start_frame=self._seconds_to_start_frame(start_sec, fps),
                end_frame=self._seconds_to_end_frame(end_sec, fps),
                start_sec=round(float(start_sec), 6),
                end_sec=round(float(end_sec), 6),
            )
            for index, (start_sec, end_sec) in enumerate(merged_scenes, start=1)
        )

        total_frames = source_metadata.total_frames or (shot_boundaries[-1].end_frame if shot_boundaries else None)
        duration_sec = source_metadata.duration_sec or (shot_boundaries[-1].end_sec if shot_boundaries else None)
        return ShotBoundaryResult(
            video=VideoMetadata(
                source_video_path=resolved_path,
                fps=float(fps),
                total_frames=total_frames,
                duration_sec=duration_sec,
            ),
            shots=shot_boundaries,
            parameters={
                "threshold": float(threshold),
                "min_scene_length_frames": int(min_scene_length_frames),
                "device": str(device or "auto"),
            },
        )

    def _require_transnet(self):
        try:
            from transnetv2_pytorch import TransNetV2
        except Exception as exc:
            raise RuntimeError(
                "TransNetV2 import failed. Install `transnetv2-pytorch` and restart ComfyUI. "
                f"Original error: {exc}"
            ) from exc
        return TransNetV2

    def _build_model(self, transnet_cls, device: str):
        normalized_device = str(device or "auto").strip().lower() or "auto"
        init_errors: list[str] = []
        for kwargs in ({"device": normalized_device}, {}):
            try:
                model = transnet_cls(**kwargs)
                if hasattr(model, "eval"):
                    model.eval()
                return model
            except Exception as exc:
                init_errors.append(str(exc))
        raise RuntimeError(f"Failed to initialize TransNetV2 model: {init_errors[:2]}")

    def _run_inference(self, model, video_path: str, threshold: float) -> Any:
        inference_errors: list[str] = []
        for method_name in ("detect_scenes", "analyze_video", "predict_video"):
            method = getattr(model, method_name, None)
            if not callable(method):
                continue
            for kwargs in ({"threshold": float(threshold)}, {}):
                try:
                    return method(video_path, **kwargs)
                except TypeError:
                    continue
                except Exception as exc:
                    inference_errors.append(f"{method_name}: {exc}")
                    break
        raise RuntimeError(f"TransNetV2 inference failed: {inference_errors[:2]}")

    def _extract_scenes_and_fps(self, raw_result: Any) -> tuple[list[tuple[float, float]], float | None]:
        fps: float | None = None
        scenes: Any = raw_result

        if isinstance(raw_result, dict):
            scenes = raw_result.get("scenes", raw_result)
            fps = self._coerce_positive_float(raw_result.get("fps"))

        if hasattr(scenes, "tolist"):
            scenes = scenes.tolist()

        normalized_scenes: list[tuple[float, float]] = []
        if not isinstance(scenes, list):
            return normalized_scenes, fps

        for entry in scenes:
            start_sec, end_sec = self._extract_time_range(entry, fps)
            if start_sec is None or end_sec is None or end_sec <= start_sec:
                continue
            normalized_scenes.append((float(start_sec), float(end_sec)))

        normalized_scenes.sort(key=lambda item: (item[0], item[1]))
        return normalized_scenes, fps

    def _extract_time_range(self, entry: Any, fps: float | None) -> tuple[float | None, float | None]:
        if isinstance(entry, dict):
            start_sec = self._coerce_float(
                entry.get("start_seconds", entry.get("start_time", entry.get("start")))
            )
            end_sec = self._coerce_float(
                entry.get("end_seconds", entry.get("end_time", entry.get("end")))
            )
            if start_sec is not None and end_sec is not None:
                return start_sec, end_sec

            start_frame = self._coerce_int(entry.get("start_frame"))
            end_frame = self._coerce_int(entry.get("end_frame"))
            if fps and start_frame is not None and end_frame is not None:
                return start_frame / fps, end_frame / fps
            return None, None

        if isinstance(entry, (list, tuple)) and len(entry) >= 2:
            start_sec = self._coerce_float(entry[0])
            end_sec = self._coerce_float(entry[1])
            if start_sec is not None and end_sec is not None:
                return start_sec, end_sec
        return None, None

    def _apply_min_scene_length(
        self,
        scenes: list[tuple[float, float]],
        fps: float,
        min_scene_length_frames: int,
    ) -> list[tuple[float, float]]:
        if not scenes:
            return []

        min_duration_sec = max(0.0, float(min_scene_length_frames) / float(fps))
        if min_duration_sec <= 0:
            return scenes

        merged: list[list[float]] = []
        for start_sec, end_sec in scenes:
            if not merged:
                merged.append([start_sec, end_sec])
                continue

            duration_sec = end_sec - start_sec
            if duration_sec < min_duration_sec:
                merged[-1][1] = max(merged[-1][1], end_sec)
                continue
            merged.append([start_sec, end_sec])

        return [(float(start_sec), float(end_sec)) for start_sec, end_sec in merged if end_sec > start_sec]

    def _seconds_to_start_frame(self, seconds: float, fps: float) -> int:
        return max(0, int(math.floor(float(seconds) * float(fps) + 1e-9)))

    def _seconds_to_end_frame(self, seconds: float, fps: float) -> int:
        return max(0, int(math.ceil(float(seconds) * float(fps) - 1e-9)))

    def _coerce_float(self, value: Any) -> float | None:
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _coerce_positive_float(self, value: Any) -> float | None:
        coerced = self._coerce_float(value)
        if coerced is None or coerced <= 0:
            return None
        return coerced

    def _coerce_int(self, value: Any) -> int | None:
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _validate_video_path(self, original_path: str, resolved_path: str) -> None:
        if not resolved_path:
            raise ValueError("Video path is empty.")
        from pathlib import Path

        if not Path(resolved_path).is_file():
            raise ValueError(f"Video path not found: {original_path}")
