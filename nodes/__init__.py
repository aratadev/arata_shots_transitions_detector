from .export_text_files import ArataShotTxtExport
from .shot_detection import ArataTransNetV2ShotDetect

NODE_CLASS_MAPPINGS = {
    "ArataTransNetV2ShotDetect": ArataTransNetV2ShotDetect,
    "ArataShotTxtExport": ArataShotTxtExport,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ArataTransNetV2ShotDetect": "Arata Detect Shots (TransNetV2)",
    "ArataShotTxtExport": "Arata Export Shots TXT",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
