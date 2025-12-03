# 🛠️ Architecture Fix Proposal: Thermal Vision Pipeline

**Date:** November 30, 2025
**Status:** PROPOSED
**Priority:** CRITICAL

---

## 🚨 The Problem: "Vision Mismatch"

Our current simulation and initial training plan relied heavily on the **D-Fire Dataset**.
Upon deeper analysis, we have identified a critical mismatch:

| Feature | D-Fire Dataset (Current) | Real World Requirement (Target) |
| :--- | :--- | :--- |
| **Spectrum** | **RGB (Visible Light)** | **Thermal (Infrared)** |
| **Perspective** | Ground / Surveillance Camera | Aerial / Drone Down-looking |
| **Fire Type** | Large Forest Fires | Early Stage / Small Hotspots |

**Impact:** A model trained on D-Fire will likely **FAIL** to detect fires when using the InfiRay P2Pro thermal camera on the drone. It learns to look for "orange pixels" (fire) and "grey clouds" (smoke), whereas a thermal camera sees "bright white hotspots".

---

## 🏗️ Proposed Architecture Fix

We propose a pivot in the **Data & Model Pipeline** to align with hardware realities.

### 1. Data Pipeline Pivot
**Action:** Deprecate D-Fire as the primary training source. Promote **FLAME Dataset** to Tier 1.

*   **New Primary Dataset:** [FLAME (Fire Luminosity Airborne-based Machine learning Evaluation)](https://ieee-dataport.org/open-access/flame-dataset)
    *   *Why:* It contains actual **aerial thermal footage** from drones.
    *   *Action:* Download immediately (requires IEEE account).
*   **Secondary Dataset:** Custom P2Pro Footage.
    *   *Action:* We must record our own "hotspot" data using the P2Pro camera (lighters, heat guns, campfires) to train for small-scale detection.

### 2. Model Pipeline Pivot
**Action:** Switch from "Training from Scratch" to "Fine-tuning Pre-trained Thermal Models".

*   **Base Model:** Instead of generic YOLOv8n (COCO), use a model pre-trained on thermal/fire data.
    *   *Candidate:* `touati-kamel/yolov8s-forest-fire-detection` (Hugging Face) or similar thermal-specific weights.
*   **Training Strategy:**
    *   Freeze the "backbone" (feature extractor).
    *   Retrain only the "head" (detection layer) on the FLAME thermal dataset.
    *   *Benefit:* Drastically reduces training time and data requirements.

### 3. Simulation Update
**Action:** Update the PC Simulation to mimic thermal vision.

*   **Current:** `simulation.py` feeds RGB video to the model.
*   **Fix:** Apply a **Greyscale/Inverted filter** to the RGB simulation video to roughly approximate thermal imagery (White = Hot).
    *   *Code Change:* `frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY); frame = cv2.bitwise_not(frame)` (approximate).
    *   *Goal:* Test the workflow with "thermal-like" inputs before flying.

---

## 📅 Implementation Plan

| Phase | Task | Owner | Est. Time |
| :--- | :--- | :--- | :--- |
| **Phase 1B** | **Download FLAME Dataset** | User | 1 Day |
| **Phase 1B** | **Download Pre-trained Model** | User | < 1 Hour |
| **Phase 1B** | **Update Simulation (Thermal Mode)** | Agent | 1 Hour |
| **Phase 2** | **Hardware Data Collection (P2Pro)** | User | 1 Week |

---

## 🤝 Request for Comments
Please review this proposal. If approved, we will proceed with:
1.  Downloading the FLAME dataset.
2.  Switching the simulation to "Thermal Mode".
