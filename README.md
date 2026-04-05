# Arata TransNetV2 Node

ComfyUI custom nodes for exporting a shot-boundary text file from a video.

## Nodes

- `Arata Detect Shots (TransNetV2)`
- `Arata Export Shots TXT`

## Workflow Shape

1. Feed `video_path` into `Arata Detect Shots (TransNetV2)`.
2. Connect its output into `Arata Export Shots TXT`.
3. Run the workflow.
4. Use the download button on the export node to fetch the generated `.txt` file.

## Output Format

Shot file columns:

```text
shot_index\tstart_frame\tend_frame\tstart_sec\tend_sec
```

The file begins with `#` metadata lines.
Frame semantics are:

- `start_frame`: inclusive
- `end_frame`: exclusive
