# SmartVideoCompressor

<p align="center">
  <b>Smart Video Compressor</b> — Maintain HDR/Dolby Vision Metadata, Keep Original Resolution & Frame Rate
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.6+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg" alt="Platform">
</p>

---

A professional video compression script that reduces video file size while preserving original quality. Specially optimized for retaining **HDR10 / HDR10+ / HLG / Dolby Vision** metadata.

## Features

- **Preserve Original Quality**
  - No resolution downscaling — keeps original resolution
  - No frame rate reduction — keeps original frame rate
  - HDR metadata preservation — HDR10, HDR10+, HLG, Dolby Vision RPU
  - Audio pass-through — no re-encoding, no quality loss

- **Smart Compression**
  - Automatic HDR metadata detection and preservation
  - H.265 (HEVC) encoding with CRF mode
  - Intelligent CRF auto-calculation based on target file size
  - Optional two-pass encoding for precise file size control

- **Ease of Use**
  - Output files placed alongside originals with `_compressed` suffix
  - Batch processing support
  - Detailed progress and parameter display

## Requirements

- **Python 3.6+**
- **FFmpeg** (must be installed and available on system PATH)

### FFmpeg Installation

**Windows**
```powershell
# Download from https://ffmpeg.org/download.html
# Extract to C:\ffmpeg, then add C:\ffmpeg\bin to PATH
```

**macOS**
```bash
brew install ffmpeg
```

**Linux**
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# CentOS/RHEL
sudo yum install epel-release && sudo yum install ffmpeg
```

## Quick Start

```bash
# Clone the repository
git clone https://github.com/leoecn/SmartVideoCompressor.git
cd SmartVideoCompressor

# Compress a video to under 200 MB (default)
python video_compressor.py input.mp4

# Specify target size (100 MB)
python video_compressor.py input.mp4 --target-size 100

# Batch process all videos in a directory
python video_compressor.py --batch ./videos --target-size 500
```

## Usage

```
usage: video_compressor.py [-h] [-o OUTPUT] [-s TARGET_SIZE] [--crf CRF]
                           [--two-pass] [--preset {ultrafast,...,veryslow}]
                           [--tune {film,...,zerolatency}] [--batch BATCH]
                           [--ffmpeg FFMPEG] [--ffprobe FFPROBE]
                           [input]

Smart Video Compressor — Reduce file size while preserving original quality

positional arguments:
  input                 Input video file path

options:
  -o, --output          Output file path (default: "_compressed" suffix)
  -s, --target-size     Target file size in MB (default: 200)
  --crf                 CRF value 18-28 (default: auto-calculated)
  --two-pass            Enable two-pass encoding for precise sizing
  --preset              Encoding preset (default: medium)
  --tune                Tuning parameter
  --batch               Batch process all videos in a directory
  --ffmpeg              Path to ffmpeg executable
  --ffprobe             Path to ffprobe executable
```

### CRF Reference

| CRF | Quality | File Size |
|-----|---------|-----------|
| 18-20 | Near-lossless | Large |
| 21-23 | High (default range) | Moderate |
| 24-26 | Good | Smaller |
| 27-28 | Acceptable | Smallest |

### Preset Reference

| Preset | Speed | Compression |
|--------|-------|-------------|
| ultrafast | Fastest | Lowest |
| medium | Balanced (default) | Balanced |
| veryslow | Slowest | Highest |

## HDR / Dolby Vision Support

The script automatically detects and preserves:

| Format | Metadata Preserved |
|--------|-------------------|
| **Dolby Vision** | Full RPU metadata (profile 8.1) |
| **HDR10** | Mastering Display + Content Light Level |
| **HDR10+** | Dynamic metadata |
| **HLG** | Transfer characteristics |

No special flags required — the script extracts exact color parameters (primaries, transfer, matrix) from the source and passes them to the x265 encoder.

## Examples

See [examples/example_usage.md](examples/example_usage.md) for more command examples including:
- CRF-based quality control
- Two-pass encoding
- Content-specific tuning (animation, film, grain)
- Batch processing workflows
- Archival & preview compression strategies

## Advanced

### Two-Pass Encoding

```bash
python video_compressor.py movie.mkv --target-size 1000 --two-pass
```
Precisely hits the target file size. Encoding time increases by ~50%.

### Smart CRF Calculation

The script auto-calculates CRF based on:
1. Original resolution
2. Original frame rate
3. Target file size
4. Audio stream size
5. Compression ratio to original bitrate

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ffmpeg not found` | Install FFmpeg and add to PATH |
| Output exceeds target size | Use `--two-pass` or increase CRF: `--crf 26` |
| HDR metadata lost | Ensure FFmpeg is up-to-date; use `--preset medium` or slower |
| Encoding too slow | Use `--preset veryfast` or faster |

## Contributing

Contributions are welcome. Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Changelog

### v1.0.0 (2024-01)
- Initial release
- HDR10 / Dolby Vision metadata preservation
- Smart CRF auto-calculation
- Batch processing
- Two-pass encoding support

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  <sub>⭐ If you find this useful, please consider starring the repository!</sub>
</p>

<!-- Star History placeholder -->
<!-- [![Star History Chart](https://api.star-history.com/svg?repos=leoecn/SmartVideoCompressor&type=Date)](https://star-history.com/#leoecn/SmartVideoCompressor&Date) -->
