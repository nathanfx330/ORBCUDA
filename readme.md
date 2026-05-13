# 📦 ORBCUDA

**A high-performance video frame search engine for finding exact image matches inside video timelines using feature-based visual matching.**

*(Note: Currently heavily CPU-optimized via multi-threading. True GPU/CUDA acceleration is in active development, but the environment is already pre-configured with CUDA toolkits).*

---

## 🔥 Overview

ORBCUDA is a high-performance video search tool that locates the exact timestamp where a reference image appears inside a video.

Instead of brute-force pixel comparison, it uses computer vision feature matching:

* ORB feature detection (structure-based visual fingerprints)
* Multi-stage bucket scanning
* Parallel processing
* FFmpeg-based frame extraction pipeline

Think of it as:

> **Reverse image search, but inside video timelines.**

---

## ⚙️ Features

* 🎯 Find exact image matches inside long videos
* ⚡ Multi-threaded bucket scanning for massive CPU performance gains
* 🧠 ORB feature-based matching (robust to minor lighting/compression changes)
* 🎬 Frame-level timestamp precision
* 📸 Automatic 5-frame visual verification grid generation
* 🚀 Drop-in ready for bash/batch scripting workflows

---

## 🧠 How it works

### Phase 1 — Coarse Search

* Video is split into time buckets.
* Frames are extracted rapidly via an FFmpeg pipe.
* ORB features are computed.
* Candidate timestamps are ranked by feature similarity.

### Phase 2 — Refinement

* Promising regions are re-scanned at a higher sampling rate.
* The exact best frame is selected using Lowe's Ratio Test for feature match density.

### Output

* Exact timestamp.
* Feature match score.
* Visual verification grid (5-frame preview saved to disk).

---

## 📦 Installation

ORBCUDA uses Conda to manage all dependencies—including FFmpeg and the NVIDIA CUDA toolkits—ensuring a clean, isolated setup.

### 1. Create the `environment.yml` file
Save the following as `environment.yml` in your project directory:

```yaml
name: orbcuda
channels:
  - conda-forge
  - nvidia

dependencies:
  - python=3.10
  - numpy
  - ffmpeg
  - pip

  # GPU tooling 
  - cudatoolkit
  - cudnn

  - pip:
      - opencv-python
      - opencv-contrib-python
```
*(Note: `argparse` is built into standard Python 3, so it does not need to be explicitly installed via pip).*

### 2. Build and Activate the Environment

```bash
conda env create -f environment.yml
conda activate orbcuda
```

---

## 🚀 Usage

### Basic Search
Run the script by passing the target video and the image you want to find:

```bash
python find_frame.py input_video.mp4 target_image.jpg -w 8 -b 30 -s 2.0
```

### Batch Processing (Directory)
Because ORBCUDA is a CLI tool, it easily integrates into shell loops to search an entire directory of videos for a specific image:

**Linux / macOS (Bash):**
```bash
for f in *.mp4; do python find_frame.py "$f" target_image.jpg; done
```

**Windows (PowerShell):**
```powershell
Get-ChildItem -Filter *.mp4 | ForEach-Object { python find_frame.py $_.FullName target_image.jpg }
```

---

## ⚙️ Parameters

| Flag | Name | Default | Description |
| :--- | :--- | :--- | :--- |
| `-w` | `--workers` | `8` | Number of worker threads. Set to your CPU core count for max speed. |
| `-b` | `--bucket` | `30` | Bucket size in seconds. Splits the video into parallel processing chunks. |
| `-s` | `--step` | `2.0` | Frame sampling FPS during Phase 1 extraction. |

---

## 📸 Output

**Example Terminal Output:**

```text
🎬 Sliced video into 20 buckets. Hunting across 8 threads...
[██████████████████████████████] 20/20 | Best Time: 00:12:34.000 | Max Features: 87
🔬 Phase 2: Refining area around 00:12:34.000...
------------------------------------------------------------
🏆 SEARCH COMPLETE
🎬 Video: input_video.mp4
🎯 Time : 00:12:34.120
📊 Match: 92 features matched
------------------------------------------------------------

📸 Generating 5-Frame Verification Grid...
✅ Saved to: input_video_match_grid.jpg
```

**Generated File:**
A file named `input_video_match_grid.jpg` will be saved in the directory, featuring a 5-frame visual verification strip with timestamps burned in around the detected match.

---

## 🧪 Use Cases

* Finding specific slides or screenshots inside long meeting recordings.
* Video forensic analysis.
* Content verification and ad-tracking.
* Clip retrieval from massive media archives.
* VFX / compositing reference matching.
* Media indexing and search workflows.

---

## ⚡ Performance Notes

* Scaling is heavily dependent on CPU cores via multi-threaded bucket scanning.
* Piping raw video directly from FFmpeg to NumPy avoids heavy disk I/O bottlenecks.
* Best performance is achieved on systems with fast NVMe SSD storage and 8+ CPU cores.

---

## 🗺️ Future Roadmap

* **v2.0**: True CUDA acceleration (GPU feature extraction via `cv2.cuda.ORB_create`).
* CLIP-based semantic matching (search for text prompts/concepts, not just exact pixels).
* Persistent video indexing (TinEye-style local video database).
* Web UI for timeline navigation.

---

## 📜 License

This project is licensed under the **MIT License**.

### MIT License (Full Text)

```text
MIT License

Copyright (c) 2025 ORBCUDA

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
