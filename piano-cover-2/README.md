# Piano cover — "Ingatkah… kapan terakhir kita bicara" (key D)

Video course style: chord pill, piano diagram card (frosted glass), lyrics karaoke, cinematic grade.

- `output/piano-cover-ingatkah-biru.mp4`, `output/piano-cover-ingatkah-merah.mp4` (1080x1920, 30fps, 88.6s)
- `song.json` — chord timings (detected from audio, ~70 BPM) and lyric lines. Edit, then re-render.
- Render: `python3 render.py <source.mov> biru|merah <out.mp4> [--preview 10]` (needs ffmpeg + Pillow)

Lyrics are only filled in for the first verse (2.6s–28s); later sections show a `• • •` placeholder
until lyrics are added to `song.json`.
