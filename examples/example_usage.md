# Example Usage - SmartVideoCompressor

## Basic Compression

Compress a video to under 200 MB (default):

```bash
python video_compressor.py vacation.mp4
```

## Specify Target Size

```bash
# Compress to under 100 MB
python video_compressor.py vacation.mp4 --target-size 100

# Compress to under 500 MB
python video_compressor.py movie.mkv -s 500
```

## Specify Output Path

```bash
python video_compressor.py vacation.mp4 -o ./compressed/vacation_small.mp4
```

## CRF-Based Quality Control

```bash
# High quality (lower CRF = better quality)
python video_compressor.py source.mp4 --crf 18

# Balanced quality (default auto-range: 21-23)
python video_compressor.py source.mp4 --crf 23

# Smaller file, acceptable quality
python video_compressor.py source.mp4 --crf 26
```

## Two-Pass Encoding (Accurate File Size)

```bash
python video_compressor.py source.mp4 --target-size 500 --two-pass
```

## Encoding Presets

```bash
# Fastest encoding, larger output
python video_compressor.py source.mp4 --preset ultrafast

# Balanced (default)
python video_compressor.py source.mp4 --preset medium

# Better compression, slower
python video_compressor.py source.mp4 --preset slow

# Best compression, slowest
python video_compressor.py source.mp4 --preset veryslow --target-size 1000
```

## Content-Specific Tuning

```bash
# Animation / cartoons
python video_compressor.py anime.mkv --tune animation

# Film / movies
python video_compressor.py movie.mkv --tune film

# Screen recordings / slides
python video_compressor.py recording.mp4 --tune stillimage

# Grainy footage
python video_compressor.py old_film.mkv --tune grain
```

## Batch Processing

```bash
# Compress all videos in a directory
python video_compressor.py --batch ./videos --target-size 500

# Batch with slow preset for archival
python video_compressor.py --batch ./raw_footage --target-size 2000 --preset slow
```

## HDR / Dolby Vision Preservation

The script automatically detects and preserves HDR metadata. No special flags needed:

```bash
# HDR10 video - metadata preserved automatically
python video_compressor.py hdr_movie.mkv --target-size 800

# Dolby Vision video - RPU data preserved
python video_compressor.py dovi_video.mp4 --target-size 1000
```

## Custom FFmpeg Path

```bash
python video_compressor.py video.mp4 --ffmpeg "C:\ffmpeg\bin\ffmpeg.exe" --ffprobe "C:\ffmpeg\bin\ffprobe.exe"
```

## Full Example: Archival Compression

Combine slow preset, two-pass, and a generous target size for archiving:

```bash
python video_compressor.py family_video.mp4 \
    --target-size 2000 \
    --preset veryslow \
    --two-pass \
    --output ./archive/family_video_archival.mp4
```

## Full Example: Quick Preview

Fast compression for preview/sharing:

```bash
python video_compressor.py presentation.mp4 \
    --target-size 50 \
    --preset veryfast \
    --output preview.mp4
```
