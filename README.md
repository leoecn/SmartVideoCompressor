# SmartVideoCompressor / 智能视频压缩工具

<p align="center">
  <b>Smart Video Compressor</b> — Maintain HDR/Dolby Vision Metadata, Keep Original Resolution & Frame Rate<br>
  <b>智能视频压缩工具</b> — 保持HDR/Dolby Vision元数据，不降低分辨率与帧率
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.6+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg" alt="Platform">
</p>

---

> A professional video compression script that reduces video file size while preserving original quality. Specially optimized for retaining **HDR10 / HDR10+ / HLG / Dolby Vision** metadata.
>
> 一款专业的视频压缩脚本，在压缩文件体积的同时保持原始画质，针对 **HDR10 / HDR10+ / HLG / Dolby Vision** 元数据保留做了专项优化。

---

## Features / 核心特性

| Category | English | 中文 |
|----------|---------|------|
| **Preserve Quality** / **保持画质** | No resolution downscaling · No frame rate reduction · HDR metadata preservation (HDR10, HDR10+, HLG, Dolby Vision RPU) · Audio pass-through (no re-encoding) | 不降分辨率 · 不降帧率 · HDR元数据完整保留（HDR10 / HDR10+ / HLG / Dolby Vision） · 音频直通不重编码 |
| **Smart Compression** / **智能压缩** | Auto HDR detection & preservation · H.265 (HEVC) + CRF mode · Intelligent CRF auto-calculation · Optional two-pass encoding | 自动检测并保留HDR元数据 · H.265 (HEVC) 编码 + CRF 模式 · 智能CRF自动计算 · 可选两遍编码精确控大小 |
| **Ease of Use** / **简单易用** | Output with `_compressed` suffix · Batch processing · Detailed progress display | 输出文件自动添加 `_compressed` 后缀 · 支持批量处理 · 详细进度与参数展示 |

## Requirements / 环境要求

- **Python 3.6+**
- **FFmpeg** — must be installed and available on system PATH / 必须安装并添加到系统 PATH

### FFmpeg Installation / FFmpeg 安装

| OS | Command / 命令 |
|----|----------------|
| **Windows** | Download from https://ffmpeg.org/download.html, extract to `C:\ffmpeg`, add `C:\ffmpeg\bin` to PATH |
| **macOS** | `brew install ffmpeg` |
| **Linux** (Debian) | `sudo apt update && sudo apt install ffmpeg` |
| **Linux** (RHEL) | `sudo yum install epel-release && sudo yum install ffmpeg` |

## Quick Start / 快速开始

```bash
# Clone / 克隆仓库
git clone https://github.com/leoecn/SmartVideoCompressor.git
cd SmartVideoCompressor

# Compress to under 200 MB (default) / 压缩至200MB以下（默认）
python video_compressor.py input.mp4

# Specify target size (100 MB) / 指定目标大小100MB
python video_compressor.py input.mp4 --target-size 100

# Batch process all videos in a directory / 批量处理目录内所有视频
python video_compressor.py --batch ./videos --target-size 500
```

## Usage / 使用说明

```
usage: video_compressor.py [-h] [-o OUTPUT] [-s TARGET_SIZE] [--crf CRF]
                           [--two-pass] [--preset {ultrafast,...,veryslow}]
                           [--tune {film,...,zerolatency}] [--batch BATCH]
                           [--ffmpeg FFMPEG] [--ffprobe FFPROBE]
                           [input]

Smart Video Compressor — Reduce file size while preserving original quality
智能视频压缩器 — 压缩文件体积，保持原始画质
```

| Argument / 参数 | Description / 说明 | Default / 默认值 |
|-----------------|-------------------|------------------|
| `input` | Input video file path / 输入视频路径 | — |
| `-o, --output` | Output file path / 输出文件路径 | `_compressed` suffix |
| `-s, --target-size` | Target file size in MB / 目标大小(MB) | `200` |
| `--crf` | CRF value 18-28 / CRF值 18-28 | Auto-calculated / 自动计算 |
| `--two-pass` | Two-pass encoding / 两遍编码 | Off |
| `--preset` | Encoding preset / 编码预设 | `medium` |
| `--tune` | Tuning parameter / 调优参数 | — |
| `--batch` | Batch process directory / 批量处理目录 | — |

### CRF Reference / CRF 参考

| CRF | Quality / 画质 | File Size / 体积 |
|-----|---------------|------------------|
| 18-20 | Near-lossless / 近乎无损 | Large / 较大 |
| 21-23 | High (default) / 高质量（默认） | Moderate / 中等 |
| 24-26 | Good / 良好 | Smaller / 较小 |
| 27-28 | Acceptable / 可接受 | Smallest / 最小 |

### Preset Reference / 预设参考

| Preset | Speed / 速度 | Compression / 压缩率 |
|--------|-------------|---------------------|
| `ultrafast` | Fastest / 最快 | Lowest / 最低 |
| `medium` | Balanced (default) / 平衡（默认） | Balanced / 平衡 |
| `veryslow` | Slowest / 最慢 | Highest / 最高 |

## HDR / Dolby Vision Support / HDR / Dolby Vision 支持

> The script automatically detects and preserves HDR metadata. No special flags required.
>
> 脚本自动检测并保留 HDR 元数据，无需额外参数。

| Format / 格式 | Metadata Preserved / 保留的元数据 |
|---------------|----------------------------------|
| **Dolby Vision** | Full RPU metadata (Profile 8.1) / 完整 RPU 元数据 |
| **HDR10** | Mastering Display + Content Light Level |
| **HDR10+** | Dynamic metadata / 动态元数据 |
| **HLG** | Transfer characteristics / 传输特性 |

## Examples / 使用示例

See [examples/example_usage.md](examples/example_usage.md) for more command examples.
详细命令示例见 [examples/example_usage.md](examples/example_usage.md)。

| Scenario / 场景 | Command / 命令 |
|-----------------|---------------|
| CRF quality control / CRF质量控制 | `python video_compressor.py video.mp4 --crf 22` |
| Two-pass encoding / 两遍编码 | `python video_compressor.py movie.mkv --target-size 1000 --two-pass` |
| Animation tuning / 动画调优 | `python video_compressor.py anime.mkv --tune animation` |
| Archive compression / 归档压缩 | `python video_compressor.py archive.mp4 --preset veryslow --target-size 500` |
| Quick preview / 快速预览 | `python video_compressor.py clip.mp4 --preset veryfast --target-size 50` |
| Batch processing / 批量处理 | `python video_compressor.py --batch ./videos --target-size 200` |

## Advanced / 高级功能

### Two-Pass Encoding / 两遍编码

```bash
python video_compressor.py movie.mkv --target-size 1000 --two-pass
```

> Precisely hits the target file size. Encoding time increases by ~50%.
>
> 精确命中目标文件大小，编码时间约增加 50%。

### Smart CRF Calculation / 智能 CRF 计算

The script auto-calculates CRF based on / 脚本基于以下因素自动计算 CRF：

| Factor / 因素 | Weight / 作用 |
|---------------|--------------|
| Original resolution / 原始分辨率 | Higher resolution → lower CRF / 分辨率越高 → CRF越低 |
| Original frame rate / 原始帧率 | Higher fps → lower CRF / 帧率越高 → CRF越低 |
| Target file size / 目标大小 | Smaller target → higher CRF / 目标越小 → CRF越高 |
| Audio stream size / 音频流大小 | Subtracted from video budget / 从视频预算中扣除 |
| Compression ratio / 压缩比 | Higher ratio → higher CRF / 压缩比越高 → CRF越高 |

## Troubleshooting / 常见问题

| Issue / 问题 | Solution / 解决方法 |
|-------------|-------------------|
| `ffmpeg not found` / 找不到ffmpeg | Install FFmpeg and add to PATH / 安装FFmpeg并添加到PATH |
| Output exceeds target / 输出超过目标大小 | Use `--two-pass` or `--crf 26` |
| HDR metadata lost / HDR元数据丢失 | Update FFmpeg; use `--preset medium` or slower / 更新FFmpeg，使用 `--preset medium` 或更慢 |
| Encoding too slow / 编码太慢 | Use `--preset veryfast` or faster / 使用 `--preset veryfast` |

## Contributing / 参与贡献

Contributions are welcome. Please / 欢迎贡献，请遵循以下步骤：

1. Fork the repository / Fork 本仓库
2. Create a feature branch / 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. Commit your changes / 提交改动 (`git commit -m 'Add amazing feature'`)
4. Push to the branch / 推送到分支 (`git push origin feature/amazing-feature`)
5. Open a Pull Request / 发起 Pull Request

## Changelog / 更新日志

### v1.0.0 (2026-05)

| EN | 中文 |
|----|------|
| Initial release | 首次发布 |
| HDR10 / Dolby Vision metadata preservation | HDR10 / Dolby Vision 元数据保留 |
| Smart CRF auto-calculation | 智能 CRF 自动计算 |
| Batch processing | 批量处理 |
| Two-pass encoding support | 两遍编码支持 |

## License / 许可证

MIT License — see [LICENSE](LICENSE) for details / 详见 [LICENSE](LICENSE)

---

<p align="center">
  <sub>⭐ If you find this useful, please consider starring the repository!</sub><br>
  <sub>⭐ 如果对你有帮助，欢迎 Star 本仓库！</sub>
</p>

<!-- Star History placeholder -->
<!-- [![Star History Chart](https://api.star-history.com/svg?repos=leoecn/SmartVideoCompressor&type=Date)](https://star-history.com/#leoecn/SmartVideoCompressor&Date) -->