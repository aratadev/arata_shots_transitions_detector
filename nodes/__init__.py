from .export_json_files import ArataShotJsonExport
from .shot_detection import ArataTransNetV2ShotDetect

NODE_CLASS_MAPPINGS = {
    "ArataTransNetV2ShotDetect": ArataTransNetV2ShotDetect,
    "ArataShotJsonExport": ArataShotJsonExport,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ArataTransNetV2ShotDetect": "Arata Detect Shots (TransNetV2)",
    "ArataShotJsonExport": "Arata Export Shots JSON",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
