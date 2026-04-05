from __future__ import annotations

from ..services.transnet_service import TransNetV2ShotDetectionService
from ..utils.path_utils import build_file_signature


class ArataTransNetV2ShotDetect:
    CATEGORY = "Arata/Video Analysis"
    FUNCTION = "detect_shots"
    RETURN_TYPES = ("ARATA_SHOT_BOUNDARIES",)
    RETURN_NAMES = ("shot_boundaries",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_path": ("STRING", {"default": ""}),
                "threshold": ("FLOAT", {"default": 0.50, "min": 0.01, "max": 0.99, "step": 0.01}),
                "min_scene_length_frames": ("INT", {"default": 30, "min": 1, "max": 10000}),
                "device": (["auto", "cuda", "cpu", "mps"], {"default": "auto"}),
            }
        }

    @classmethod
    def IS_CHANGED(cls, video_path: str, **_: object) -> str:
        return build_file_signature(video_path)

    def detect_shots(
        self,
        video_path: str,
        threshold: float,
        min_scene_length_frames: int,
        device: str,
    ):
        service = TransNetV2ShotDetectionService()
        result = service.detect_shots(
            video_path=video_path,
            threshold=float(threshold),
            min_scene_length_frames=int(min_scene_length_frames),
            device=device,
        )
        return (result,)
