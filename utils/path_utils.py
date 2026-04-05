from __future__ import annotations

import re
from pathlib import Path

from .comfy_paths import get_annotated_filepath, get_input_directory

_INVALID_PATH_CHARS_RE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def strip_comfy_path_annotation(path_text: str) -> str:
    value = str(path_text or "").strip()
    if value.endswith("]") and " [" in value:
        value = value.rsplit(" [", 1)[0].strip()
    return value


def resolve_video_path(path_text: str) -> str:
    candidate_text = strip_comfy_path_annotation(path_text)
    if not candidate_text:
        return ""

    candidate = Path(candidate_text).expanduser()
    if candidate.is_file():
        return str(candidate.resolve())

    annotated = get_annotated_filepath(candidate_text)
    if annotated and Path(annotated).is_file():
        return str(Path(annotated).resolve())

    input_directory = get_input_directory()
    for variant in (
        input_directory / candidate_text,
        input_directory / Path(candidate_text).name,
    ):
        if variant.is_file():
            return str(variant.resolve())

    return str(candidate.resolve(strict=False)) if candidate.is_absolute() else str(candidate)


def build_file_signature(path_text: str) -> str:
    resolved_path = resolve_video_path(path_text)
    candidate = Path(resolved_path)
    if not resolved_path or not candidate.is_file():
        return resolved_path
    stat = candidate.stat()
    return f"{candidate.resolve()}:{stat.st_size}:{stat.st_mtime_ns}"


def normalize_output_subdirectory(subdirectory: str) -> Path:
    raw_value = str(subdirectory or "").strip().replace("\\", "/").strip("/")
    if not raw_value:
        return Path("arata_transnetv2")

    parts: list[str] = []
    for raw_part in raw_value.split("/"):
        part = raw_part.strip()
        if not part or part == ".":
            continue
        if part == "..":
            raise ValueError("Output subdirectory must stay inside the ComfyUI output directory.")
        parts.append(sanitize_path_component(part))

    if not parts:
        return Path("arata_transnetv2")
    return Path(*parts)


def build_output_filename_stem(video_path: str, filename_stem: str) -> str:
    explicit_stem = sanitize_filename_stem(filename_stem)
    if explicit_stem:
        return explicit_stem
    return sanitize_filename_stem(Path(video_path).stem) or "video"


def sanitize_filename_stem(value: str) -> str:
    text = _INVALID_PATH_CHARS_RE.sub("_", str(value or "").strip())
    text = re.sub(r"\s+", "_", text)
    return text.strip("._")


def sanitize_path_component(value: str) -> str:
    cleaned = _INVALID_PATH_CHARS_RE.sub("_", str(value or "").strip())
    cleaned = cleaned.strip(".")
    if not cleaned:
        raise ValueError("Encountered an empty output path component after sanitization.")
    return cleaned


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def make_unique_path(path: Path, overwrite_existing: bool) -> Path:
    if overwrite_existing or not path.exists():
        return path

    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    index = 1
    while True:
        candidate = parent / f"{stem}_{index:03d}{suffix}"
        if not candidate.exists():
            return candidate
        index += 1


def resolve_download_path(relative_path: str, output_root: Path) -> Path:
    cleaned = str(relative_path or "").strip().replace("\\", "/")
    if not cleaned:
        raise ValueError("Download path is empty.")

    candidate = Path(cleaned)
    if candidate.is_absolute():
        raise ValueError("Download path must be relative to the ComfyUI output directory.")

    resolved_root = output_root.resolve(strict=False)
    resolved_path = (resolved_root / candidate).resolve(strict=False)
    if resolved_root not in resolved_path.parents and resolved_path != resolved_root:
        raise ValueError("Download path escapes the ComfyUI output directory.")
    return resolved_path
