# TasteLab Dashboard: Research User Manual
Welcome to the TasteLab Dashboard. This platform is designed to help you analyze multimodal experiment data (video and audio) without needing a technical background in data science.

## Table of Contents
1. [Network Requirements](#network-requirements)
2. [Data Synchronization (The ETL Pipeline)](#data-synchronization-the-etl-pipeline)
3. [Speech & Emotion Analysis (NLP)](#speech--emotion-analysis-nlp)
4. [Participant Tracking & Movement (CV)](#participant-tracking--movement-cv)
5. [Human-in-the-Loop Annotation](#human-in-the-loop-annotation)
6. [Data Integrity & Thresholds](#data-integrity--thresholds)

## Network Requirements
The TasteLab Dashboard is hosted locally on the BUas internal servers. For security and data privacy, it is not accessible via the public internet.

- **On-Premise Access:** You must be physically present at the BUas campus and connected to the Eduroam or local faculty Wi-Fi.
- **Remote Access (Working from Home):** 1. You must use a **VPN (Virtual Private Network)** to create a secure tunnel to the campus network. 2. Ensure you are using the official BUas VPN client (e.g., FortiClient). 3. **Crucial:** Once the VPN is connected, you must verify that "BUas" or the "Campus Network" is the active gateway in your VPN settings, otherwise the dashboard URL will not resolve.

## Data Synchronization (The ETL Pipeline)
The dashboard uses an automated "Sync and Store" pipeline to fetch the latest experiment data from MinIO storage.

#### How It Works
- **Automated Refresh:** The system is scheduled to automatically scan and import new data every 24 hours.
- **Manual Refresh:** If you have just uploaded new experiment files and don't want to wait, you can manually trigger the pipeline.
- **The Sync Button:** Look for the "Sync Minio" button (or the 🔄 refresh icon) in the navigation bar or experiment list.
- **Speed:** While the initial raw analysis is heavy, the sync button processes the data into the dashboard in just a few seconds, making the insights immediately queryable. Want to know more about this process? Check out the [ETL Pipeline Documentation](../sync/README.md).

## Speech & Emotion Analysis (NLP)
The dashboard automatically processes audio to provide a deep dive into participant interactions.

#### Key Features
- **AI Summary:** View an auto-generated overview of the key points discussed during the session.
- **Emotion Timeline:** Track 17 different emotions across the duration of the experiment.
- **Complex Moments:** Look for segments where multiple emotions are detected simultaneously (e.g., "Happy" and "Hopeful" appearing together).
- **Keyword Extraction:** Review the top 20 keywords ranked by TF-IDF scores to identify the most significant topics.
- **Action Items & Questions:** Access a list of tasks identified by the AI and questions asked during the experiment, along with confidence metrics.

## Participant Tracking & Movement (CV)
The Computer Vision (CV) model tracks how participants move within the TasteLab facility.

#### Analytics Tools

- **Movement Heatmaps:** Visualize spatial activity levels across different camera zones, such as the "Food Station" or "Door".
- **Zone Occupancy:** View a table showing the percentage of time participants spent in specific camera views (e.g., CAM4: 52.6%).
- **Participant Tracking Cards:** Check how many cameras captured a specific person and the total duration of their movements.
- **Multi-Camera Patterns:** Identify cross-camera movement patterns to understand how participants navigate the space.

## Human-in-the-Loop Annotation
To ensure high research validity, you can manually verify and label participants to train the AI model.

#### The Labeling Workflow

- **Identify:** The dashboard displays images of people detected by the system.
- **Label:** Assign a specific ID or role to the detection (e.g., "Participant A", "Facilitator").
- **Train:** Once enough labels are collected, the system triggers model training to recognize those specific participants throughout the rest of the video.
- **Refine:** Use the "Undo" or "Skip" buttons to correct assignments or remove low-quality detections.

## Data Integrity & Thresholds
When conducting your research, keep the following constraints in mind:

- **Confidence Filtering:** The system automatically filters out predictions below a certain threshold to ensure only actionable insights are shown.
- **Transcription Accuracy:** NLP confidence scores for questions and topics typically range between 60-80%.
- **Synchronization:** While the ETL pipeline aligns timestamps, slight misalignments between separate audio and video feeds may occur; always verify critical moments using the timestamped transcript.

## Need Help?
If you encounter any issues or have questions about using the TasteLab Dashboard, please reach out to ayumicto@gmail.com.

For detailed technical documentation, refer to the [Technical Report](../docs/technical_report_dashboard.pdf) and the [ETL Pipeline Documentation](../sync/README.md).

---
**Last Updated:** January 2026

**Maintained by:** Ayumi Cho
