from __future__ import annotations

import json
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
            "# format_version=1",
            f"# detector={shot_boundaries.detector}",
            f"# source_video_path={shot_boundaries.video.source_video_path}",
            f"# fps={self._format_optional_float(shot_boundaries.video.fps)}",
            f"# parameters_json={json.dumps(shot_boundaries.parameters, sort_keys=True)}",
            "# columns: shot_index\tstart_frame\tend_frame\tstart_sec\tend_sec",
            "# frame_semantics: start_frame inclusive, end_frame exclusive",
        ]
        lines.extend(
            f"{shot.index}\t{shot.start_frame}\t{shot.end_frame}\t{shot.start_sec:.6f}\t{shot.end_sec:.6f}"
            for shot in shot_boundaries.shots
        )
        return "\n".join(lines) + "\n"

    def _format_optional_float(self, value: float | None) -> str:
        if value is None:
            return "unknown"
        return f"{float(value):.6f}"
