from __future__ import annotations

from pathlib import Path

from ..utils.comfy_paths import get_output_directory
from ..utils.models import ExportedFile, ShotBoundaryResult, ShotTextExportResult
from ..utils.path_utils import (
    build_output_filename_stem,
    ensure_directory,
    make_unique_path,
    normalize_output_subdirectory,
)


class ShotTextExportService:
    def export(
        self,
        shot_boundaries: ShotBoundaryResult,
        output_subdirectory: str,
        filename_stem: str,
        overwrite_existing: bool,
    ) -> ShotTextExportResult:
        output_root = get_output_directory()
        export_dir = ensure_directory(output_root / normalize_output_subdirectory(output_subdirectory))
        stem = build_output_filename_stem(shot_boundaries.video.source_video_path, filename_stem)

        shots_path = make_unique_path(export_dir / f"{stem}_shots.txt", overwrite_existing)
        shots_path.write_text(self._format_shot_file(shot_boundaries), encoding="utf-8")

        return ShotTextExportResult(
            shots_file=self._build_exported_file("shots", shots_path, output_root),
        )

    def _build_exported_file(self, label: str, file_path: Path, output_root: Path) -> ExportedFile:
        relative_output_path = file_path.resolve(strict=False).relative_to(output_root.resolve(strict=False)).as_posix()
        return ExportedFile(
            label=label,
            file_path=str(file_path),
            relative_output_path=relative_output_path,
            filename=file_path.name,
        )

    def _format_shot_file(self, shot_boundaries: ShotBoundaryResult) -> str:
        lines = [
            f"{shot.index}\t{shot.start_frame}\t{shot.end_frame}\t{shot.start_sec:.6f}\t{shot.end_sec:.6f}"
            for shot in shot_boundaries.shots
        ]
        return "\n".join(lines) + ("\n" if lines else "")
