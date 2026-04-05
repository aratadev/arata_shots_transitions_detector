from __future__ import annotations

from pathlib import Path
from typing import Any

from ..utils.models import TransitionBoundary, TransitionBoundaryResult, VideoMetadata
from ..utils.path_utils import resolve_video_path


class PySceneDetectGradualTransitionService:
    def detect_transitions(
        self,
        video_path: str,
        threshold: float,
        min_transition_length_frames: int,
        method: str,
    ) -> TransitionBoundaryResult:
        resolved_path = resolve_video_path(video_path)
        if not resolved_path or not Path(resolved_path).is_file():
            raise ValueError(f"Video path not found: {video_path}")

        SceneManager, StatsManager, ThresholdDetector, open_video = self._require_scenedetect()
        video = open_video(resolved_path)
        try:
            stats_manager = self._build_stats_manager(StatsManager, video)
            scene_manager = self._build_scene_manager(SceneManager, stats_manager)

            detector_method = self._resolve_threshold_method(ThresholdDetector, method)
            detector = ThresholdDetector(
                threshold=float(threshold),
                min_scene_len=1,
                method=detector_method,
            )
            scene_manager.add_detector(detector)
            scene_manager.detect_scenes(video)

            fps = self._coerce_positive_float(getattr(video, "frame_rate", None) or getattr(video, "fps", None))
            if fps is None:
                raise RuntimeError("PySceneDetect could not determine the video's FPS.")

            total_frames = self._extract_total_frames(video, scene_manager)
            intervals = self._extract_transition_intervals(
                stats_manager=stats_manager,
                total_frames=total_frames,
                threshold=float(threshold),
                min_transition_length_frames=int(min_transition_length_frames),
                method=str(method or "floor"),
                metric_key=ThresholdDetector.THRESHOLD_VALUE_KEY,
            )
            transitions = tuple(
                TransitionBoundary(
                    index=index,
                    start_frame=start_frame,
                    end_frame=end_frame,
                    start_sec=round(start_frame / fps, 6),
                    end_sec=round(end_frame / fps, 6),
                    transition_type="gradual",
                )
                for index, (start_frame, end_frame) in enumerate(intervals, start=1)
            )

            duration_sec = round(total_frames / fps, 6) if total_frames is not None else None
            return TransitionBoundaryResult(
                video=VideoMetadata(
                    source_video_path=resolved_path,
                    fps=float(fps),
                    total_frames=total_frames,
                    duration_sec=duration_sec,
                ),
                transitions=transitions,
                parameters={
                    "threshold": float(threshold),
                    "min_transition_length_frames": int(min_transition_length_frames),
                    "method": str(method or "floor"),
                },
            )
        finally:
            self._close_video(video)

    def _require_scenedetect(self):
        try:
            from scenedetect import SceneManager, open_video
            from scenedetect.detectors import ThresholdDetector
            from scenedetect.stats_manager import StatsManager
        except Exception as exc:
            raise RuntimeError(
                "PySceneDetect import failed. Install `scenedetect[opencv]` and restart ComfyUI. "
                f"Original error: {exc}"
            ) from exc
        return SceneManager, StatsManager, ThresholdDetector, open_video

    def _build_stats_manager(self, stats_manager_cls, video):
        base_timecode = getattr(video, "base_timecode", None)
        for args, kwargs in (((base_timecode,), {}), ((), {"base_timecode": base_timecode}), ((), {})):
            try:
                return stats_manager_cls(*args, **kwargs)
            except TypeError:
                continue
        raise RuntimeError("Failed to initialize PySceneDetect StatsManager.")

    def _build_scene_manager(self, scene_manager_cls, stats_manager):
        for args, kwargs in (((stats_manager,), {}), ((), {"stats_manager": stats_manager}), ((), {})):
            try:
                return scene_manager_cls(*args, **kwargs)
            except TypeError:
                continue
        raise RuntimeError("Failed to initialize PySceneDetect SceneManager.")

    def _resolve_threshold_method(self, threshold_detector_cls, method: str):
        normalized = str(method or "floor").strip().upper() or "FLOOR"
        try:
            return getattr(threshold_detector_cls.Method, normalized)
        except AttributeError as exc:
            raise ValueError(f"Unsupported PySceneDetect threshold method: {method}") from exc

    def _extract_total_frames(self, video, scene_manager) -> int:
        duration = getattr(video, "duration", None)
        frame_count = self._coerce_int(getattr(duration, "frame_num", None)) if duration is not None else None
        if frame_count is not None and frame_count > 0:
            return frame_count

        scenes = scene_manager.get_scene_list()
        if scenes:
            last_scene_end = scenes[-1][1]
            last_frame_num = self._coerce_int(getattr(last_scene_end, "frame_num", None))
            if last_frame_num is not None and last_frame_num > 0:
                return last_frame_num

        raise RuntimeError("PySceneDetect could not determine the video's total frame count.")

    def _extract_transition_intervals(
        self,
        stats_manager,
        total_frames: int,
        threshold: float,
        min_transition_length_frames: int,
        method: str,
        metric_key: str,
    ) -> list[tuple[int, int]]:
        intervals: list[tuple[int, int]] = []
        start_frame: int | None = None
        normalized_method = str(method or "floor").strip().lower() or "floor"

        for frame_num in range(total_frames):
            metric_value = self._get_metric(stats_manager, frame_num, metric_key)
            is_transition_frame = metric_value is not None and self._is_transition_frame(
                metric_value,
                threshold,
                normalized_method,
            )

            if is_transition_frame and start_frame is None:
                start_frame = frame_num
                continue

            if is_transition_frame or start_frame is None:
                continue

            if frame_num - start_frame >= min_transition_length_frames:
                intervals.append((start_frame, frame_num))
            start_frame = None

        if start_frame is not None and total_frames - start_frame >= min_transition_length_frames:
            intervals.append((start_frame, total_frames))

        return intervals

    def _get_metric(self, stats_manager, frame_num: int, metric_key: str) -> float | None:
        try:
            if not stats_manager.metrics_exist(frame_num, [metric_key]):
                return None
            values = stats_manager.get_metrics(frame_num, [metric_key])
        except Exception:
            return None
        if not values:
            return None
        return self._coerce_float(values[0])

    def _is_transition_frame(self, metric_value: float, threshold: float, method: str) -> bool:
        if method == "ceiling":
            return float(metric_value) >= float(threshold)
        return float(metric_value) < float(threshold)

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

    def _close_video(self, video) -> None:
        for method_name in ("close", "release"):
            method = getattr(video, method_name, None)
            if callable(method):
                try:
                    method()
                except Exception:
                    pass
