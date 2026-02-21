# 🚛 Driver Monitoring System | Driver Monitoring System with AI

### 🚀 Real-Time Computer Vision for Fleet Safety with Local AI Auditing

A practical prototype that bridges real-time object detection with AI-driven forensic auditing. This project demonstrates how to build a high-performance safety system designed to run on **low-end hardware**, combining YOLOv8 efficiency with the reasoning power of the Qwen2-VL vision model.

---

## 🎥 Demo

Watch a live demonstration of Driver Monitoring System in action:

> [![Watch the demo](https://img.youtube.com/vi/79D-cZHhqzk/0.jpg)](https://www.youtube.com/watch?v=79D-cZHhqzk)
> *This video shows real-time detection of risky behaviors (cell phone use / distraction), the automated AI audit process, and the management dashboard.*

---

## 📋 Overview

**Driver Monitoring System** presents a professional approach to fleet safety management, transforming raw video streams into actionable safety intelligence.

Developed by a **Financial Analyst and independent AI developer**, this project focuses on:

- Low-cost implementation  
- Fully local AI processing (no cloud dependency)  
- Performance optimization for everyday hardware  

### 🔍 Core Features

- **Ultra-Light Perception**  
  Runs YOLOv8n at optimized resolutions (320x240) to detect distractions such as mobile phones or bottles with minimal CPU/GPU load.

- **Forensic AI Auditing**  
  Uses Qwen2-VL as a Vision-Language Model to verify detections, acting as a “second pair of eyes” that explains *why* a behavior is considered risky.

- **Human-in-the-Loop Validation**  
  A dedicated dashboard allows managers to provide the final decision, combining machine precision with human judgment.

- **Home-Office Optimized Testing**  
  The AI auditor is tuned to ignore non-truck backgrounds and focus exclusively on driver hand behavior.

- **Safety Analytics**  
  Automatic visualization of peak risk hours and AI accuracy metrics using Chart.js.

---

## 🛠️ Tech Stack

| Component | Technology |
|------------|------------|
| **Real-Time Detection** | YOLOv8 (Nano), OpenCV |
| **Forensic AI** | Qwen2-VL (Vision-Language Model) |
| **Backend** | Python 3.x, Flask, SQLite |
| **Frontend** | HTML5, CSS3, Bootstrap 5 |
| **Data Visualization** | Chart.js |

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/andreluizgreboge/SafetyCore-AI.git
cd SafetyCore-AI
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Initialize the database

```bash
python init_db.py
```

---

## ▶️ How to Run

### Step 1 — Real-Time Monitoring

```bash
python yolo_realtime.py
```

### Step 2 — AI Auditing Engine

```bash
python auditor.py
```

### Step 3 — Web Dashboard

```bash
python app.py
```

---

## 🧠 System Architecture

The system operates as a three-stage asynchronous pipeline, ensuring stability even on modest hardware.

### 1️⃣ Detection

YOLOv8 monitors the video stream. When a risky behavior is detected:

- A compressed JPEG image is saved  
- A `PENDING` event is logged in the database  

### 2️⃣ Verification

The AI Auditor:

- Polls the database for pending events  
- Sends captured evidence to Qwen2-VL  
- Generates a structured description of the driver's actions  
- Ignores irrelevant background elements  

### 3️⃣ Human Review

A manager:

- Reviews the evidence through the Web UI  
- Provides the final verdict  
- Feeds validated data into the analytics engine  

---

## 📂 Project Structure

```plaintext
SafetyCore-AI/
├── static/
│   ├── captures/       # Evidence images (.jpg)
│   └── style.css       # UI theme
├── templates/
│   ├── dashboard.html  # Live logs and human review
│   └── analytics.html  # Charts and performance metrics
├── app.py              # Flask Web Server
├── auditor.py          # Qwen2-VL Audit Engine
├── yolo_realtime.py    # YOLOv8 Perception Module
├── init_db.py          # Database initialization
├── requirements.txt    # Project dependencies
└── README.md           # Documentation
```

---

## ⚖️ License

This project is licensed under the MIT License.  
See the `LICENSE` file for full details.
