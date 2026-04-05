from .export_text_files import ArataBoundaryTxtExport
from .shot_detection import ArataTransNetV2ShotDetect
from .transition_detection import ArataPySceneDetectGradualTransitionDetect

NODE_CLASS_MAPPINGS = {
    "ArataTransNetV2ShotDetect": ArataTransNetV2ShotDetect,
    "ArataPySceneDetectGradualTransitionDetect": ArataPySceneDetectGradualTransitionDetect,
    "ArataBoundaryTxtExport": ArataBoundaryTxtExport,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ArataTransNetV2ShotDetect": "Arata Detect Shots (TransNetV2)",
    "ArataPySceneDetectGradualTransitionDetect": "Arata Detect Gradual Transitions (PySceneDetect)",
    "ArataBoundaryTxtExport": "Arata Export Boundary TXT",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
