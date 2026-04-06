# Arata TransNetV2 Node

ComfyUI custom nodes for exporting a shot-boundary JSON file from a video.

## Nodes

- `Arata Detect Shots (TransNetV2)`
- `Arata Export Shots JSON`

## Workflow Shape

1. Feed `video_path` into `Arata Detect Shots (TransNetV2)`.
2. Connect its output into `Arata Export Shots JSON`.
3. Run the workflow.
4. Use the download button on the export node to fetch the generated `.json` file.

## Migration Note

The export node internal id is now `ArataShotJsonExport`.
Older saved workflows that reference the previous export node id must be updated before they will load correctly.

## Output Format

```json
{
  "video": {
    "fps": 24.0,
    "total_frames": 2400,
    "duration_sec": 100.0
  },
  "frame_semantics": {
    "start_frame": "inclusive",
    "end_frame": "exclusive"
  },
  "shots": [
    {
      "index": 1,
      "start_frame": 0,
      "end_frame": 124,
      "start_sec": 0.0,
      "end_sec": 5.166667
    }
  ]
}
```
