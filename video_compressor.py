#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SmartVideoCompressor — Smart Video Compression Tool
====================================================

Compress videos to a target file size while preserving:
- Original resolution
- Original frame rate
- HDR metadata (HDR10 / HDR10+ / HLG / Dolby Vision)
- Audio quality (direct stream copy)

Requirements: FFmpeg and FFprobe must be installed and on system PATH.

Usage:
    python video_compressor.py input.mp4
    python video_compressor.py input.mp4 --target-size 100
    python video_compressor.py input.mp4 --crf 22 --preset slow
    python video_compressor.py --batch ./videos --target-size 500

For full documentation, see: https://github.com/leoecn/SmartVideoCompressor
"""

import os
import subprocess
import json
import math
import argparse
import sys
from pathlib import Path
import re


class VideoCompressor:
    """Smart video compressor with HDR/Dolby Vision awareness."""

    def __init__(self, ffmpeg_path="ffmpeg", ffprobe_path="ffprobe"):
        """
        Initialize the video compressor.

        Args:
            ffmpeg_path: Path to ffmpeg executable.
            ffprobe_path: Path to ffprobe executable.
        """
        self.ffmpeg_path = ffmpeg_path
        self.ffprobe_path = ffprobe_path

    def get_video_info(self, input_path):
        """
        Get detailed video information using ffprobe.

        Args:
            input_path: Input video file path.

        Returns:
            dict: Parsed JSON video information.

        Raises:
            RuntimeError: If ffprobe fails or returns invalid JSON.
        """
        cmd = [
            self.ffprobe_path,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            input_path
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            info = json.loads(result.stdout)
            return info
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to get video info: {e}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse video info: {e}")

    def extract_video_props(self, video_info):
        """
        Extract key encoding parameters for precise preservation.

        Args:
            video_info: Video info dict from get_video_info().

        Returns:
            dict: color_space, color_transfer, color_primaries, pix_fmt,
                  side_data_types and HDR detection flags.
        """
        props = {
            "color_space": None,
            "color_transfer": None,
            "color_primaries": None,
            "pix_fmt": None,
            "side_data_types": [],
            "has_mastering_display": False,
            "has_content_light_level": False,
            "has_dovi_rpu": False
        }

        for stream in video_info.get("streams", []):
            if stream.get("codec_type") == "video":
                props["color_space"] = stream.get("color_space")
                props["color_transfer"] = stream.get("color_transfer") or stream.get("color_trc")
                props["color_primaries"] = stream.get("color_primaries")
                props["pix_fmt"] = stream.get("pix_fmt")

                # Detect HDR metadata types from side_data
                side_data_list = stream.get("side_data_list", [])
                for side_data in side_data_list:
                    side_type = side_data.get("side_data_type", "")
                    props["side_data_types"].append(side_type)

                    if "Mastering display metadata" in side_type:
                        props["has_mastering_display"] = True
                    if "Content light level" in side_type:
                        props["has_content_light_level"] = True
                    if "Dolby Vision" in side_type or "DOVI" in side_type:
                        props["has_dovi_rpu"] = True

        return props

    def has_dolby_vision(self, video_props):
        """Check if the video contains Dolby Vision metadata."""
        return video_props["has_dovi_rpu"]

    def has_hdr(self, video_props):
        """Check if the video contains any HDR metadata."""
        if video_props["has_mastering_display"] or video_props["has_content_light_level"]:
            return True

        hdr_signatures = ["bt2020", "smpte2084", "arib-std-b67", "hlg"]
        for field in [video_props["color_space"], video_props["color_transfer"],
                       video_props["color_primaries"]]:
            if field and any(sig in (field or "").lower() for sig in hdr_signatures):
                return True
        return False

    def calculate_target_bitrate(self, input_path, target_size_mb, duration_sec, audio_bitrate_kbps):
        """
        Calculate target video bitrate based on target file size.

        Args:
            input_path: Input file path.
            target_size_mb: Target file size in MB.
            duration_sec: Video duration in seconds.
            audio_bitrate_kbps: Audio bitrate in kbps.

        Returns:
            int: Target video bitrate in kbps.
        """
        target_bits = target_size_mb * 8 * 1024 * 1024
        audio_bits = audio_bitrate_kbps * 1000 * duration_sec
        available_video_bits = target_bits - audio_bits

        if available_video_bits <= 0:
            raise ValueError("Target file size too small to accommodate audio stream")

        video_bitrate_kbps = int(available_video_bits / (duration_sec * 1000))
        min_bitrate = 500  # Minimum 500 kbps
        return max(video_bitrate_kbps, min_bitrate)

    def estimate_crf_from_bitrate(self, video_info, target_bitrate_kbps):
        """
        Estimate CRF value from target bitrate.

        Uses resolution, frame rate, and compression ratio heuristics.

        Args:
            video_info: Video info dict.
            target_bitrate_kbps: Target video bitrate in kbps.

        Returns:
            int: Estimated CRF value (18-28).
        """
        for stream in video_info.get("streams", []):
            if stream.get("codec_type") == "video":
                width = int(stream.get("width", 1920))
                height = int(stream.get("height", 1080))
                fps = eval(stream.get("avg_frame_rate", "30/1"))
                if isinstance(fps, tuple):
                    fps = fps[0] / fps[1] if fps[1] != 0 else 30

                pixels = width * height
                base_crf = 23  # Base CRF for 1080p

                # Resolution adjustment
                if pixels > 1920 * 1080:
                    crf_adjust = -2
                elif pixels < 1280 * 720:
                    crf_adjust = 2
                else:
                    crf_adjust = 0

                # Frame rate adjustment
                if fps > 60:
                    fps_adjust = -2
                elif fps > 30:
                    fps_adjust = -1
                else:
                    fps_adjust = 0

                estimated_crf = base_crf + crf_adjust + fps_adjust

                # Fine-tune based on target vs original bitrate
                original_bitrate = None
                if "bit_rate" in stream:
                    original_bitrate = int(stream["bit_rate"]) / 1000
                elif "bit_rate" in video_info.get("format", {}):
                    original_bitrate = int(video_info["format"]["bit_rate"]) / 1000

                if original_bitrate:
                    compression_ratio = target_bitrate_kbps / original_bitrate
                    if compression_ratio < 0.3:
                        estimated_crf += 4
                    elif compression_ratio < 0.5:
                        estimated_crf += 2
                    elif compression_ratio > 0.8:
                        estimated_crf -= 1

                return max(18, min(28, estimated_crf))

        return 23  # Default fallback

    def compress_video(self, input_path, output_path=None, target_size_mb=200,
                      crf=None, two_pass=False, preset="medium", tune=None):
        """
        Compress video to target file size.

        Args:
            input_path: Input video file path.
            output_path: Output file path (default: "_compressed" suffix).
            target_size_mb: Target file size in MB (default: 200).
            crf: CRF value 18-28 (None for auto-calculation).
            two_pass: Use two-pass encoding for precise size control.
            preset: x265 preset (ultrafast to veryslow).
            tune: x265 tuning parameter.

        Returns:
            str: Output file path.

        Raises:
            FileNotFoundError: If input file does not exist.
            ValueError: If duration cannot be determined.
        """
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        if output_path is None:
            output_path = input_path.parent / f"{input_path.stem}_compressed{input_path.suffix}"
        else:
            output_path = Path(output_path)

        # Gather video information
        print(f"Analyzing video: {input_path}")
        video_info = self.get_video_info(str(input_path))

        duration = float(video_info.get("format", {}).get("duration", 0))
        if duration == 0:
            raise ValueError("Could not determine video duration")

        # Get audio bitrate
        audio_bitrate = 0
        for stream in video_info.get("streams", []):
            if stream.get("codec_type") == "audio":
                if "bit_rate" in stream:
                    audio_bitrate = int(stream["bit_rate"]) / 1000
                break
        if audio_bitrate == 0:
            audio_bitrate = 128  # Default fallback

        # Extract video properties and detect HDR/Dolby Vision
        video_props = self.extract_video_props(video_info)
        has_hdr = self.has_hdr(video_props)
        has_dovi = self.has_dolby_vision(video_props)

        print(f"Duration: {duration:.2f}s")
        print(f"Audio bitrate: {audio_bitrate:.0f} kbps")
        print(f"HDR: {'Yes' if has_hdr else 'No'}")
        print(f"Dolby Vision: {'Yes' if has_dovi else 'No'}")
        if has_hdr:
            print(f"  Color space: {video_props['color_space']}")
            print(f"  Transfer: {video_props['color_transfer']}")
            print(f"  Primaries: {video_props['color_primaries']}")
            print(f"  Pixel format: {video_props['pix_fmt']}")

        # Calculate target bitrate
        target_bitrate = self.calculate_target_bitrate(
            str(input_path), target_size_mb, duration, audio_bitrate
        )
        print(f"Target video bitrate: {target_bitrate:.0f} kbps")

        # Determine CRF
        if crf is None:
            crf = self.estimate_crf_from_bitrate(video_info, target_bitrate)
            print(f"Auto-calculated CRF: {crf}")
        else:
            print(f"Using specified CRF: {crf}")

        # Build FFmpeg command
        base_cmd = [self.ffmpeg_path, "-i", str(input_path)]

        # Video encoding parameters
        video_params = [
            "-c:v", "libx265",
            "-crf", str(crf),
            "-preset", preset,
            "-x265-params", "log-level=error"
        ]

        # HDR / Dolby Vision support — exact color parameter matching
        if has_hdr or has_dovi:
            src_color_primaries = video_props["color_primaries"] or "bt2020"
            src_color_trc = video_props["color_transfer"] or "arib-std-b67"
            src_color_space = video_props["color_space"] or "bt2020nc"

            video_params.extend([
                "-color_primaries", src_color_primaries,
                "-color_trc", src_color_trc,
                "-colorspace", src_color_space,
                "-pix_fmt", "yuv420p10le"
            ])

            x265_hdr_params = [
                f"colorprim={src_color_primaries}",
                f"transfer={src_color_trc}",
                f"colormatrix={src_color_space}",
                "hdr10-opt=1",
                "repeat-headers=1"
            ]

            if has_dovi:
                x265_hdr_params.append("dolby-vision-profile=8.1")

            video_params.extend(["-x265-params", ":".join(x265_hdr_params)])

        # Audio: direct copy (no re-encode)
        audio_params = ["-c:a", "copy"]

        # Additional parameters
        other_params = [
            "-map", "0",
            "-map_metadata", "0",
            "-movflags", "+faststart",
            "-y"
        ]

        if tune:
            video_params.extend(["-tune", tune])

        # Execute encoding
        if two_pass:
            print("Two-pass encoding...")

            # Pass 1
            pass1_cmd = base_cmd + [
                "-pass", "1",
                "-passlogfile", str(output_path.with_suffix(".log")),
                "-an",
                "-f", "null",
                "/dev/null" if sys.platform != "win32" else "NUL"
            ]
            pass1_cmd = pass1_cmd[:1] + video_params + pass1_cmd[1:]

            # Pass 2
            pass2_cmd = base_cmd + [
                "-pass", "2",
                "-passlogfile", str(output_path.with_suffix(".log")),
                str(output_path)
            ]
            pass2_cmd = pass2_cmd[:1] + video_params + audio_params + other_params + pass2_cmd[-2:]

            print("Pass 1/2...")
            subprocess.run(pass1_cmd, check=True)
            print("Pass 2/2...")
            subprocess.run(pass2_cmd, check=True)

            # Clean up log files
            log_file = output_path.with_suffix(".log")
            if log_file.exists():
                log_file.unlink()
        else:
            cmd = base_cmd + video_params + audio_params + other_params + [str(output_path)]
            print("Encoding...")
            subprocess.run(cmd, check=True)

        # Report results
        output_size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"Compression complete!")
        print(f"Output: {output_path}")
        print(f"Size: {output_size_mb:.2f} MB (target: {target_size_mb} MB)")

        return str(output_path)


def main():
    parser = argparse.ArgumentParser(
        description="SmartVideoCompressor — Reduce file size while preserving original quality",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python video_compressor.py input.mp4
  python video_compressor.py input.mp4 --target-size 100
  python video_compressor.py input.mp4 --output compressed.mp4
  python video_compressor.py input.mp4 --two-pass
  python video_compressor.py input.mp4 --crf 22
  python video_compressor.py input.mp4 --preset slow
  python video_compressor.py --batch ./videos --target-size 500
        """
    )

    parser.add_argument("input", nargs="?", help="Input video file path")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("-s", "--target-size", type=float, default=200,
                       help="Target file size in MB (default: 200)")
    parser.add_argument("--crf", type=int, help="CRF value 18-28 (default: auto)")
    parser.add_argument("--two-pass", action="store_true",
                       help="Enable two-pass encoding for precise sizing")
    parser.add_argument("--preset", default="medium",
                       choices=["ultrafast", "superfast", "veryfast", "faster",
                               "fast", "medium", "slow", "slower", "veryslow"],
                       help="Encoding preset (default: medium)")
    parser.add_argument("--tune", choices=["film", "animation", "grain",
                                          "stillimage", "fastdecode", "zerolatency"],
                       help="Tuning parameter")
    parser.add_argument("--batch", help="Batch process all videos in a directory")
    parser.add_argument("--ffmpeg", default="ffmpeg", help="Path to ffmpeg executable")
    parser.add_argument("--ffprobe", default="ffprobe", help="Path to ffprobe executable")

    args = parser.parse_args()

    compressor = VideoCompressor(args.ffmpeg, args.ffprobe)

    # Verify FFmpeg is available
    try:
        subprocess.run([args.ffmpeg, "-version"], capture_output=True, check=True)
        subprocess.run([args.ffprobe, "-version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: FFmpeg is required. Please install and add to PATH.")
        print("Download: https://ffmpeg.org/download.html")
        return 1

    if args.batch:
        # Batch processing mode
        batch_dir = Path(args.batch)
        if not batch_dir.exists() or not batch_dir.is_dir():
            print(f"Error: Directory not found: {batch_dir}")
            return 1

        video_extensions = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"}
        video_files = [f for f in batch_dir.iterdir()
                      if f.is_file() and f.suffix.lower() in video_extensions]

        if not video_files:
            print(f"No video files found in: {batch_dir}")
            return 0

        print(f"Found {len(video_files)} video file(s). Starting batch processing...")

        success_count = 0
        for video_file in video_files:
            try:
                print(f"\nProcessing: {video_file.name}")
                output_file = video_file.parent / f"{video_file.stem}_compressed{video_file.suffix}"
                compressor.compress_video(
                    input_path=str(video_file),
                    output_path=str(output_file),
                    target_size_mb=args.target_size,
                    crf=args.crf,
                    two_pass=args.two_pass,
                    preset=args.preset,
                    tune=args.tune
                )
                success_count += 1
            except Exception as e:
                print(f"Failed: {video_file.name} — {e}")

        print(f"\nBatch complete: {success_count}/{len(video_files)} succeeded")

    elif args.input:
        # Single file mode
        try:
            compressor.compress_video(
                input_path=args.input,
                output_path=args.output,
                target_size_mb=args.target_size,
                crf=args.crf,
                two_pass=args.two_pass,
                preset=args.preset,
                tune=args.tune
            )
        except Exception as e:
            print(f"Error: {e}")
            return 1
    else:
        parser.print_help()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
