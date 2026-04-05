from __future__ import annotations

import json
from pathlib import Path

from ..utils.comfy_paths import get_output_directory
from ..utils.models import (
    BoundaryTextExportResult,
    ExportedFile,
    ShotBoundaryResult,
    TransitionBoundaryResult,
)
from ..utils.path_utils import (
    build_output_filename_stem,
    ensure_directory,
    make_unique_path,
    normalize_output_subdirectory,
)


class BoundaryTextExportService:
    def export(
        self,
        shot_boundaries: ShotBoundaryResult,
        transition_boundaries: TransitionBoundaryResult,
        output_subdirectory: str,
        filename_stem: str,
        overwrite_existing: bool,
    ) -> BoundaryTextExportResult:
        self._validate_matching_sources(shot_boundaries, transition_boundaries)

        output_root = get_output_directory()
        export_dir = ensure_directory(output_root / normalize_output_subdirectory(output_subdirectory))
        stem = build_output_filename_stem(shot_boundaries.video.source_video_path, filename_stem)

        shots_path = make_unique_path(export_dir / f"{stem}_shots.txt", overwrite_existing)
        transitions_path = make_unique_path(export_dir / f"{stem}_transitions.txt", overwrite_existing)

        shots_path.write_text(self._format_shot_file(shot_boundaries), encoding="utf-8")
        transitions_path.write_text(self._format_transition_file(transition_boundaries), encoding="utf-8")

        return BoundaryTextExportResult(
            shots_file=self._build_exported_file("shots", shots_path, output_root),
            transitions_file=self._build_exported_file("transitions", transitions_path, output_root),
        )

    def _validate_matching_sources(
        self,
        shot_boundaries: ShotBoundaryResult,
        transition_boundaries: TransitionBoundaryResult,
    ) -> None:
        shot_source = Path(shot_boundaries.video.source_video_path).resolve(strict=False)
        transition_source = Path(transition_boundaries.video.source_video_path).resolve(strict=False)
        if shot_source != transition_source:
            raise ValueError(
                "Shot boundaries and transition boundaries were produced from different source videos."
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

    def _format_transition_file(self, transition_boundaries: TransitionBoundaryResult) -> str:
        lines = [
            "# format_version=1",
            f"# detector={transition_boundaries.detector}",
            f"# source_video_path={transition_boundaries.video.source_video_path}",
            f"# fps={self._format_optional_float(transition_boundaries.video.fps)}",
            f"# parameters_json={json.dumps(transition_boundaries.parameters, sort_keys=True)}",
            "# columns: transition_index\tstart_frame\tend_frame\tstart_sec\tend_sec\ttype",
            "# frame_semantics: start_frame inclusive, end_frame exclusive",
        ]
        lines.extend(
            (
                f"{transition.index}\t{transition.start_frame}\t{transition.end_frame}\t"
                f"{transition.start_sec:.6f}\t{transition.end_sec:.6f}\t{transition.transition_type}"
            )
            for transition in transition_boundaries.transitions
        )
        return "\n".join(lines) + "\n"

    def _format_optional_float(self, value: float | None) -> str:
        if value is None:
            return "unknown"
        return f"{float(value):.6f}"
