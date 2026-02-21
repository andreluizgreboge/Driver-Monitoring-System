# System Architecture - Driver Monitoring System AI

This document describes the high-level design and data flow of the Driver Monitoring System.

## ⚙️ Core Components

The system is divided into three main layers that operate asynchronously:

### 1. Perception Layer (YOLO Engine)
* **Module:** `yolo_realtime.py`
* **Tech:** YOLOv8n (Nano), OpenCV.
* **Responsibility:** Constant monitoring of the camera stream at 320x240 resolution. It performs real-time object detection (cell phones, bottles) and triggers an event capture only when a risk is detected and a cooldown period has passed.

### 2. Audit Layer (AI Vision Auditor)
* **Module:** `auditor.py`
* **Tech:** Qwen2-VL (Visual Language Model).
* **Responsibility:** Monitors the SQLite database for entries with `PENDING` status. It analyzes the saved evidence image with a specialized prompt to confirm the violation, ignoring non-driving backgrounds (Home Office bypass).

### 3. Management Layer (Dashboard & Analytics)
* **Module:** `app.py`, `templates/`, `static/`
* **Tech:** Flask, Chart.js, Bootstrap 5.
* **Responsibility:** Provides a web interface for:
    * **Live Logs:** Viewing detections and AI audit results.
    * **Human-in-the-loop:** Allowing a human supervisor to "Confirm" or "Discard" AI findings.
    * **Analytics:** Visualizing peak risk hours and AI accuracy metrics.

## 🔄 Data Flow

1.  **Detection:** YOLO detects a "cell phone" -> Saves `.jpg` -> Inserts row into `database.db` with status `PENDING`.
2.  **Audit:** `auditor.py` polls the DB -> Sends image to Qwen AI -> Updates row with `AI_REVIEWED` and the AI reasoning.
3.  **Review:** Human Analyst opens the Dashboard -> Reviews the evidence -> Clicks "Confirm" or "Discard" -> Updates `human_decision` column.
4.  **Visualization:** Analytics page aggregates DB data to show trends and performance.

## 📊 Database Schema (SQLite)

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | Integer | Primary Key |
| `timestamp` | Text | Event time (YYYY-MM-DD HH-MM-SS) |
| `event_type` | Text | Initial YOLO detection label |
| `status` | Text | PENDING -> AI_REVIEWED |
| `ai_analysis` | Text | Detailed reasoning from Qwen-VL |
| `human_decision` | Text | Confirmed / Discarded / Pending |