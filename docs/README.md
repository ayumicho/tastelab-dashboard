# TasteLab Dashboard - Documentation

This folder contains comprehensive technical documentation for the TasteLab Dashboard project.

## Directory Structure

```
/docs/
├── researcher_manual.md                      # User guide for researchers
├── technical_report_dashboard.pdf            # Detailed technical report
└── README.md                                 # This documentation overview                       
```

## Documentation Contents

### 1. [Research User Manual](researcher_manual.md)
**Target Audience:** Students and Academic Researchers.

This guide explains how to use the dashboard features to extract insights from experiments.

- **Network Setup:** Instructions for on-premise and VPN access.
- **Using the ETL Sync:** How to retrieve new data using the Sync Minio button.
- **Analytics Guide:** Understanding NLP (Speech/Emotion) and CV (Tracking) results.
- **Human-in-the-Loop:** How to use the manual annotation tools to improve AI accuracy.

### 2. [Technical Report](technical_report_dashboard.pdf)
**Target Audience:** Developers, System Administrators, and Graders.
A comprehensive PDF detailing the engineering behind the platform.

**Architecture:** Breakdown of the Flask backend, PostgreSQL schema, and MinIO integration.

**ETL Logic:** Deep dive into the "Sync and Store" strategy and bulk data processing.

**Model Integration:** Documentation of the custom NLP and CV pipelines.
Future Roadmap: Planned enhancements for user roles and real-time ingestion.

## Quick Reference for Researchers
### Accessing the Dashboard
The dashboard is hosted on internal BUas servers. To view videos and sync data, you must be:

- **On Campus:** Connected to Eduroam.
- **Remote:** Connected via VPN (with BUas routing active).

### Syncing New Data
If you have uploaded new files to MinIO and they do not appear in the dashboard:

1. Open the Experiment List.

2. Click the "Sync Minio" button (🔄).

3. The ETL pipeline will process the new analysis files and update your view in seconds.

## Related Documentation
- **Root Readme:** For installation and local development setup, see the [Main README.md.](../README.md)

- **ETL Technical Docs:** For specific logic regarding the data import scripts, see [sync/README.md.](../sync/README.md)

**Contact:** For support or access issues, please contact the dashboard developer at ayumicto@gmail.com.

**Last Updated:** January 2026

**Maintained by:** Ayumi Chotoe
