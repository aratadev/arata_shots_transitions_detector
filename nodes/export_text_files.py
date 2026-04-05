from __future__ import annotations

from ..services.export_service import BoundaryTextExportService


class ArataBoundaryTxtExport:
    CATEGORY = "Arata/Video Analysis"
    FUNCTION = "export_files"
    OUTPUT_NODE = True
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("shots_txt_path", "transitions_txt_path")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "shot_boundaries": ("ARATA_SHOT_BOUNDARIES",),
                "transition_boundaries": ("ARATA_TRANSITION_BOUNDARIES",),
                "output_subdirectory": ("STRING", {"default": "arata_transnetv2"}),
                "filename_stem": ("STRING", {"default": ""}),
                "overwrite_existing": ("BOOLEAN", {"default": False}),
            }
        }

    def export_files(
        self,
        shot_boundaries,
        transition_boundaries,
        output_subdirectory: str,
        filename_stem: str,
        overwrite_existing: bool,
    ):
        service = BoundaryTextExportService()
        export_result = service.export(
            shot_boundaries=shot_boundaries,
            transition_boundaries=transition_boundaries,
            output_subdirectory=output_subdirectory,
            filename_stem=filename_stem,
            overwrite_existing=bool(overwrite_existing),
        )
        ui_payload = [
            export_result.shots_file.to_ui_payload(),
            export_result.transitions_file.to_ui_payload(),
        ]
        return {
            "ui": {"boundary_files": ui_payload},
            "result": (
                export_result.shots_file.file_path,
                export_result.transitions_file.file_path,
            ),
        }
