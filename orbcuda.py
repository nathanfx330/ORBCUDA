#!/usr/bin/env python3

import subprocess
import argparse
import math
import threading
import time
import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from shutil import which

import cv2
import numpy as np

# -----------------------------
# SYSTEM CHECKS
# -----------------------------

FFMPEG = "ffmpeg"
FFPROBE = "ffprobe"

lock = threading.Lock()

def check_cmd(cmd):
    return which(cmd) is not None

# -----------------------------
# TIME FORMAT
# -----------------------------

def format_time(seconds):
    td = datetime.timedelta(seconds=float(seconds))
    total = int(td.total_seconds())
    h, r = divmod(total, 3600)
    m, s = divmod(r, 60)
    ms = int((seconds - total) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"

# -----------------------------
# VIDEO INFO
# -----------------------------

def get_duration(video):
    cmd = [
        FFPROBE,
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(video),
    ]
    out = subprocess.check_output(cmd).decode().strip()
    return float(out)

# -----------------------------
# ORB SETUP (FEATURE MATCHING)
# -----------------------------

orb = cv2.ORB_create(nfeatures=2500)
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)

def preprocess_image(img_path):
    img = cv2.imread(str(img_path))
    # Resize the reference image to roughly match the extraction scale to ensure feature size parity
    img = cv2.resize(img, (640, 360))
    kp, des = orb.detectAndCompute(img, None)
    return kp, des

# -----------------------------
# FRAME EXTRACTION (SAFE PIPE)
# -----------------------------

def extract_frames(video, start, duration, step_fps):
    """
    Safely streams video into NumPy using exact dimensions.
    Pads the video with black bars to guarantee it is EXACTLY 640x360, 
    preventing NumPy reshape crashes on vertical or ultrawide videos.
    """
    scale_pad = "scale=640:360:force_original_aspect_ratio=decrease,pad=640:360:-1:-1:color=black"
    
    cmd = [
        FFMPEG,
        "-loglevel", "quiet",
        "-ss", str(start),
        "-t", str(duration),
        "-i", str(video),
        "-vf", f"fps={step_fps},{scale_pad}",
        "-f", "image2pipe",
        "-vcodec", "rawvideo",
        "-pix_fmt", "bgr24",
        "-"
    ]

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=10**8)
    frames = []
    
    # 640px * 360px * 3 color channels (BGR) = Exactly 691,200 bytes per frame
    frame_size = 640 * 360 * 3  

    while True:
        raw = proc.stdout.read(frame_size)
        if not raw or len(raw) != frame_size:
            break

        try:
            frame = np.frombuffer(raw, np.uint8).reshape((360, 640, 3))
            frames.append(frame)
        except Exception:
            break

    proc.stdout.close()
    proc.wait()

    return frames

# -----------------------------
# ORB MATCH SCORE
# -----------------------------

def score_frame(img_kp, img_des, frame):
    kp2, des2 = orb.detectAndCompute(frame, None)

    if des2 is None or img_des is None:
        return 0

    # Lowe's Ratio Test
    matches = bf.knnMatch(img_des, des2, k=2)
    good = []
    for m_n in matches:
        if len(m_n) == 2:
            m, n = m_n
            if m.distance < 0.75 * n.distance:
                good.append(m)

    return len(good)

# -----------------------------
# PHASE 1: COARSE SEARCH
# -----------------------------

def scan_bucket(video, img_kp, img_des, start, duration, step):
    frames = extract_frames(video, start, duration, step)

    best_score = 0
    best_time = start

    for i, f in enumerate(frames):
        score = score_frame(img_kp, img_des, f)

        if score > best_score:
            best_score = score
            best_time = start + (i / step)

    return best_score, best_time

# -----------------------------
# PHASE 2: REFINEMENT
# -----------------------------

def refine(video, img_kp, img_des, t, step):
    frames = extract_frames(video, max(0, t - step * 2), step * 4, step * 2)

    best = 0
    best_t = max(0, t - step * 2)

    for i, f in enumerate(frames):
        score = score_frame(img_kp, img_des, f)

        if score > best:
            best = score
            best_t = max(0, t - step * 2) + (i / (step * 2))

    return best, best_t

# -----------------------------
# MULTI-THREAD SEARCH
# -----------------------------

def hunt(video, img_kp, img_des, duration, bucket, step, workers):
    buckets = []

    for i in range(math.ceil(duration / bucket)):
        buckets.append((i * bucket, bucket))

    best_score = 0
    best_time = 0

    print(f"🎬 Sliced video into {len(buckets)} buckets. Hunting across {workers} threads...")

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [
            ex.submit(scan_bucket, video, img_kp, img_des, s, d, step)
            for s, d in buckets
        ]

        done = 0

        for f in as_completed(futures):
            score, t = f.result()

            with lock:
                if score > best_score:
                    best_score = score
                    best_time = t

            done += 1
            bar = int(30 * done / len(buckets)) * "█"
            sys_time = format_time(best_time)

            print(f"\r[{bar:<30}] {done}/{len(buckets)} | Best Time: {sys_time} | Max Features: {best_score}", end="")

    print()
    return best_score, best_time

# -----------------------------
# VISUAL VERIFICATION GRID
# -----------------------------

def generate_verification_grid(video_file, best_time):
    print(f"\n📸 Generating 5-Frame Verification Grid...")
    start_time = max(0.0, best_time - 2.0)
    out_file = video_file.with_name(f"{video_file.stem}_match_grid.jpg")
    
    hh_mm_ss = format_time(start_time).split('.')[0]
    tc_str = hh_mm_ss.replace(':', '\\:') + '\\:00'
    
    vf = (
        "fps=1,scale=-1:250,"
        f"drawtext=timecode='{tc_str}':rate=1:x=(w-tw-10):y=(h-th-10):"
        "fontsize=24:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=5,"
        "tile=layout=5x1:padding=10:margin=10:color=black"
    )
    
    cmd = [
        FFMPEG, '-loglevel', 'error',
        '-ss', str(start_time), 
        '-i', str(video_file),
        '-t', '5',              
        '-vf', vf,
        '-frames:v', '1',       
        '-y', str(out_file)
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Saved to: {out_file.name}")
    except subprocess.CalledProcessError:
        print(f"❌ Failed to generate verification grid.")

# -----------------------------
# MAIN
# -----------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("video")
    parser.add_argument("image")
    parser.add_argument("-w", "--workers", type=int, default=8)
    parser.add_argument("-b", "--bucket", type=int, default=30)
    parser.add_argument("-s", "--step", type=float, default=2.0, help="Frames Per Second to extract during scan.")

    args = parser.parse_args()

    video = Path(args.video)
    image = Path(args.image)

    if not check_cmd(FFMPEG) or not check_cmd(FFPROBE):
        print("Error: ffmpeg or ffprobe missing from PATH.")
        return

    if not image.is_file():
        print(f"Error: Image '{image}' not found.")
        return

    duration = get_duration(video)
    
    # Extract ORB features from the target image
    img_kp, img_des = preprocess_image(image)
    if img_des is None:
        print("Error: Could not extract features from the reference image.")
        return

    print("-" * 60)
    print(f"🔍 Target Image : {image.name}")
    print(f"⚡ ORB Features : OpenCV Feature Matching Engine Active")
    print("-" * 60)

    # Phase 1
    _, rough = hunt(
        video,
        img_kp,
        img_des,
        duration,
        args.bucket,
        args.step,
        args.workers
    )

    print(f"🔬 Phase 2: Refining area around {format_time(rough)}...")

    # Phase 2
    score, exact = refine(
        video,
        img_kp,
        img_des,
        rough,
        args.step
    )

    print("-" * 60)
    print("🏆 SEARCH COMPLETE")
    print(f"🎬 Video: {video.name}")
    print(f"🎯 Time : {format_time(exact)}")
    print(f"📊 Match: {score} features matched")
    print("-" * 60)

    # Phase 3
    generate_verification_grid(video, exact)

if __name__ == "__main__":
    main()
