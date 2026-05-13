# 📦 ORBCUDA

**ORB + CUDA accelerated video frame search engine for finding exact image matches inside video using feature-based visual matching and fast multi-stage scanning.**

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
* ⚡ Multi-threaded bucket scanning for performance
* 🧠 ORB feature-based matching (robust to lighting & compression)
* 🎬 Frame-level timestamp precision
* 📸 Automatic 5-frame visual verification grid
* 🧩 Supports single video or batch directories
* 🚀 Designed for CUDA-enabled systems (optional acceleration path)

---

## 🧠 How it works

### Phase 1 — Coarse Search

* Video is split into time buckets
* Frames are extracted via FFmpeg
* ORB features are computed
* Candidate timestamps are ranked by feature similarity

### Phase 2 — Refinement

* Promising regions are re-scanned at higher sampling rate
* Best frame is selected using feature match density

### Output

* Exact timestamp
* Feature match score
* Visual verification grid (5-frame preview)

---

## 📦 Installation

### 1. Create environment

```bash
conda env create -f environment.yml
conda activate orbcuda
```

---

### 2. System requirements

Ensure FFmpeg is installed:

```bash
ffmpeg -version
ffprobe -version
```

If missing:

```bash
sudo apt install ffmpeg
```

---

### 3. Python dependencies

If not using a full conda OpenCV build:

```bash
pip install numpy opencv-python
```

---

## 🚀 Usage

```bash
python find_frame.py VIDEO.mp4 IMAGE.jpg -w 8 -b 20 -s 2.0
```

---

## ⚙️ Parameters

| Flag | Description                              |
| ---- | ---------------------------------------- |
| `-w` | Number of worker threads                 |
| `-b` | Bucket size in seconds (scan chunk size) |
| `-s` | Frame sampling FPS during extraction     |

---

## 📸 Output

Example result:

```text
🏆 SEARCH COMPLETE
🎬 Video: input.mp4
🎯 Time : 00:12:34.120
📊 Match: 87 feature points matched
```

Generated file:

```text
input_match_grid.jpg
```

A 5-frame visual verification strip around the detected timestamp.

---

## 🧪 Use Cases

* Finding screenshots inside long recordings
* Video forensic analysis
* Content verification
* Clip retrieval from archives
* VFX / compositing reference matching
* Media indexing and search workflows

---

## ⚡ Performance Notes

* Scales with CPU cores via multi-threaded bucket scanning
* ORB feature matching is lightweight and fast
* Best performance:

  * SSD storage
  * 8+ CPU cores
  * optional CUDA-enabled OpenCV build

---

## 🧠 Future Roadmap

* CUDA ORB acceleration (GPU feature extraction)
* CLIP-based semantic matching (find objects, not pixels)
* Persistent video indexing (TinEye-style video search)
* Real-time streaming frame search
* Web UI timeline navigation

---

## 📜 License

This project is licensed under the **MIT License**.

### MIT License (Full Text)

```
MIT License

Copyright (c) 2026 ORBCUDA

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
