from __future__ import annotations

from ..services.export_service import ShotJsonExportService


class ArataShotJsonExport:
    CATEGORY = "Arata/Video Analysis"
    FUNCTION = "export_file"
    OUTPUT_NODE = True
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("shots_json_path",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "shot_boundaries": ("ARATA_SHOT_BOUNDARIES",),
                "output_subdirectory": ("STRING", {"default": "arata_transnetv2"}),
                "filename_stem": ("STRING", {"default": ""}),
                "overwrite_existing": ("BOOLEAN", {"default": False}),
            }
        }

    def export_file(
        self,
        shot_boundaries,
        output_subdirectory: str,
        filename_stem: str,
        overwrite_existing: bool,
    ):
        service = ShotJsonExportService()
        export_result = service.export(
            shot_boundaries=shot_boundaries,
            output_subdirectory=output_subdirectory,
            filename_stem=filename_stem,
            overwrite_existing=bool(overwrite_existing),
        )
        ui_payload = [export_result.shots_file.to_ui_payload()]
        return {
            "ui": {"boundary_files": ui_payload},
            "result": (export_result.shots_file.file_path,),
        }
