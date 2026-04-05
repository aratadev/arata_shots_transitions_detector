# Arata TransNetV2 Node

ComfyUI custom nodes for exporting two separate text files from a video:

- shot boundaries via TransNetV2
- gradual transition intervals via PySceneDetect

## Nodes

- `Arata Detect Shots (TransNetV2)`
- `Arata Detect Gradual Transitions (PySceneDetect)`
- `Arata Export Boundary TXT`

## Workflow Shape

1. Feed the same `video_path` string into both detector nodes.
2. Connect both detector outputs into `Arata Export Boundary TXT`.
3. Run the workflow.
4. Use the two download buttons on the export node to fetch the generated `.txt` files.

## Output Format

Shot file columns:

```text
shot_index\tstart_frame\tend_frame\tstart_sec\tend_sec
```

Transition file columns:

```text
transition_index\tstart_frame\tend_frame\tstart_sec\tend_sec\ttype
```

Both files begin with `#` metadata lines.
Frame semantics are:

- `start_frame`: inclusive
- `end_frame`: exclusive

This means transition intervals can overlap neighboring shot ranges without ambiguity.

## Important Note About PySceneDetect Transitions

The transition detector uses PySceneDetect's threshold-based brightness analysis.
In practice this is best suited to gradual fades or other brightness-threshold crossings.
It does not try to reinterpret hard cuts as transitions, and it is not a general dissolve/wipe detector.
