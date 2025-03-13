# Expense Ingestion System Design Document

## 1. Overview

This document outlines the design for a web-based system to **upload, validate, and process monthly expense CSV statements** using the **Medallion Architecture**. The system ensures robust **data ingestion, validation, logging, and reprocessing capabilities**, with integration to **Google Drive for storage** and **Google Identity for authentication**.

---

## 2. Key Features

### Web UI (Streamlit-Based)

- **Google Identity Authentication**
- **Drag-and-Drop CSV Upload** (Supports Multiple Files)
- **File Status Dashboard** (Uploaded, Processing, Completed, Failed)
- **Strict Schema Validation** (Reject invalid files)
- **Reload Management**:
  - Auto-reload if file changes (checksum-based).
  - "Force Reload" option for manual override.
- **Error Handling & Editing**
  - Failed rows are stored in a **separate error table**.
  - Users can **edit failed rows** and set them as "ready_to_reload".
  - Next ingestion cycle will **automatically reprocess fixed rows**.
- **Email Notifications** on processing completion (Success/Failure).

---

## 3. Ingestion Pipeline (Medallion Architecture)

### Bronze Layer (Raw Data Storage)

- **Stores original CSVs in Google Drive**.
- **Logs metadata** (file name, size, checksum, row count, timestamps).
- **Prevents duplicate processing** using **checksum-based reload logic**.
- **Triggers ingestion pipeline asynchronously** (Celery).

### Silver Layer (Validated & Transformed Data)

- **Performs Schema Validation** (Rejects invalid files).
- **Cleans & standardizes data** (Formats dates, trims spaces, etc.).
- **Stores only valid rows in PostgreSQL**.
- **Failed rows go to a separate error table.**

### Gold Layer (Final Processed Data)

- **Moves validated data from Silver → Gold**.
- **Tracks row counts per file**.
- **Sends email notification to the user upon completion.**

---

## 4. Error Handling & Reprocessing

### File-Level Failure

- **Scenario:** Entire file fails due to incorrect format, missing columns, or corruption.
- **Solution:**
  - Log the failure in the metadata table.
  - Store error details (e.g., "Missing column: Amount").
  - Send an **email notification** to the user.
  - Allow re-upload of the corrected file.

### Row-Level Failure

- **Scenario:** Some rows within a file fail validation (e.g., invalid dates, missing values).
- **Solution:**
  - **Store failed rows in a dedicated error table** (not in Silver Layer).
  - Allow users to **edit these rows directly** in the error table.
  - Set corrected rows as **"ready_to_reload"**.
  - The next ingestion cycle **automatically reprocesses these rows**.
  - If successful, the row moves to the Gold Layer; otherwise, it stays in the error table with an updated error reason.

---

## 5. Next Steps: Web UI (Streamlit)

The next phase involves defining and designing the **Streamlit UI layout** to facilitate CSV upload, error tracking, and reprocessing workflows.
