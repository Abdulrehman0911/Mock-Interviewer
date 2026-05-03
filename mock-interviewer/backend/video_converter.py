"""Convert WebM video to MP4 using bundled ffmpeg.

Browser records video as WebM VP9 codec which Windows FFmpeg/OpenCV can't decode.
This module converts WebM → MP4 (H.264) which is universally supported.
"""

import os
import subprocess
import tempfile

# Use bundled ffmpeg from imageio_ffmpeg (same as the rest of the backend)
try:
    import imageio_ffmpeg as _iio_ffmpeg
    _FFMPEG_EXE = _iio_ffmpeg.get_ffmpeg_exe()
    print(f"[CONVERT] Using bundled ffmpeg: {_FFMPEG_EXE}")
except Exception as _e:
    _FFMPEG_EXE = "ffmpeg"
    print(f"[CONVERT] Warning: imageio_ffmpeg not available, using system ffmpeg: {_e}")


def convert_webm_to_mp4(webm_path):
    """
    Convert WebM video to MP4 using ffmpeg.
    MP4 is universally compatible with Windows FFmpeg + OpenCV.

    Args:
        webm_path: Path to input WebM file.

    Returns:
        Path to converted MP4 file.

    Raises:
        FileNotFoundError: If input file doesn't exist.
        Exception: If conversion fails.
    """
    if not os.path.exists(webm_path):
        raise FileNotFoundError(f"Video file not found: {webm_path}")

    # Create temporary MP4 file
    temp_dir = tempfile.gettempdir()
    mp4_path = os.path.join(temp_dir, 'converted_video.mp4')

    # If MP4 already exists, delete it
    if os.path.exists(mp4_path):
        try:
            os.remove(mp4_path)
        except Exception:
            pass

    print(f"[CONVERT] Input WebM: {webm_path}")
    print(f"[CONVERT] Output MP4: {mp4_path}")

    # FFmpeg command to convert WebM to MP4
    # -c:v libx264 = use H.264 codec (universally supported)
    # -preset fast = faster encoding
    # -crf 23 = quality (lower = better, 23 is default)
    # -c:a aac = use AAC audio codec
    command = [
        _FFMPEG_EXE,
        '-i', webm_path,           # Input WebM file
        '-c:v', 'libx264',         # Video codec: H.264
        '-preset', 'fast',         # Speed (fast/medium/slow)
        '-crf', '23',              # Quality (23 is default)
        '-c:a', 'aac',             # Audio codec: AAC
        '-y',                       # Overwrite output
        mp4_path                   # Output MP4
    ]

    try:
        print(f"[CONVERT] Running ffmpeg conversion...")
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )

        if result.returncode != 0:
            print(f"[CONVERT] FFmpeg stderr: {result.stderr[-500:]}")
            raise Exception(f"FFmpeg conversion failed: {result.stderr[-300:]}")

        if not os.path.exists(mp4_path):
            raise Exception("MP4 file was not created")

        file_size = os.path.getsize(mp4_path)
        print(f"[CONVERT] [OK] Conversion successful. MP4 size: {file_size} bytes")

        return mp4_path

    except subprocess.TimeoutExpired:
        raise Exception("FFmpeg conversion timed out (>2 minutes)")
    except Exception as e:
        raise Exception(f"FFmpeg conversion failed: {str(e)}")


def get_video_duration(video_path):
    """Get video duration using ffprobe-like approach via ffmpeg.

    Args:
        video_path: Path to video file.

    Returns:
        Duration in seconds (float). Falls back to 30s on failure.
    """
    try:
        command = [
            _FFMPEG_EXE,
            '-i', video_path,
        ]

        result = subprocess.run(command, capture_output=True, text=True, timeout=10)

        # ffmpeg prints info to stderr even on "error" exit
        stderr_text = result.stderr if result.stderr else ""
        for line in stderr_text.splitlines():
            if "Duration:" in line:
                parts = line.split("Duration:")[1].split(",")[0].strip()
                h, m, s = parts.split(":")
                duration = int(h) * 3600 + int(m) * 60 + float(s)
                return duration

        return 30  # Default fallback
    except Exception:
        return 30  # Default fallback
