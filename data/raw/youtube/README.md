# YouTube Raw Data

The YouTube data collector writes JSON files here by default.

Generated files include:

- `brandbridge_youtube_dataset_<timestamp>.json`
- `brandbridge_youtube_creators_<timestamp>.json`
- `brandbridge_youtube_videos_<timestamp>.json`
- `brandbridge_youtube_dataset.latest.json`
- `brandbridge_youtube_creators.latest.json`
- `brandbridge_youtube_videos.latest.json`

These generated files are ignored by Git because they can be large and come from an external API.
