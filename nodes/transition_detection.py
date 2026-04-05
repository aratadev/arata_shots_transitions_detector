from __future__ import annotations

from ..services.transition_service import PySceneDetectGradualTransitionService
from ..utils.path_utils import build_file_signature


class ArataPySceneDetectGradualTransitionDetect:
    CATEGORY = "Arata/Video Analysis"
    FUNCTION = "detect_transitions"
    RETURN_TYPES = ("ARATA_TRANSITION_BOUNDARIES",)
    RETURN_NAMES = ("transition_boundaries",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_path": ("STRING", {"default": ""}),
                "threshold": ("FLOAT", {"default": 12.0, "min": 0.0, "max": 255.0, "step": 0.5}),
                "min_transition_length_frames": ("INT", {"default": 4, "min": 1, "max": 10000}),
                "method": (["floor", "ceiling"], {"default": "floor"}),
            }
        }

    @classmethod
    def IS_CHANGED(cls, video_path: str, **_: object) -> str:
        return build_file_signature(video_path)

    def detect_transitions(
        self,
        video_path: str,
        threshold: float,
        min_transition_length_frames: int,
        method: str,
    ):
        service = PySceneDetectGradualTransitionService()
        result = service.detect_transitions(
            video_path=video_path,
            threshold=float(threshold),
            min_transition_length_frames=int(min_transition_length_frames),
            method=method,
        )
        return (result,)
