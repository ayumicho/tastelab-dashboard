# TasteLab Dashboard

A Flask-based research analytics platform that transforms unstructured experimental data into meaningful insights through intelligent visualizations and analysis. The dashboard helps researchers make sense of complex multimodal data by providing powerful tools for speech analysis and people tracking across synchronized video streams.

**Project Duration:** September 1, 2025 - January 23, 2026

>**Note:** This is a portfolio demo version of the TasteLab Dashboard. The original system was developed for Breda University of Applied Sciences (BUas) and relied on a private MinIO storage server and an internal ETL pipeline that are not accessible outside the university network. In this version, the ETL pipeline has been removed and the database has been pre-populated with sample data so that the dashboard can be explored freely.

## Overview

The TasteLab Dashboard bridges the gap between raw data collection and academic research by automating complex analysis workflows. It specifically addresses challenges such as limited student accessibility, inefficient manual data merging from wearables, and the labor-intensive nature of manual annotation. 

## Key Features

- **Speech-to-Text & Analysis:** Automatic transcription of audio with AI-powered summarization and emotion detection
- **People Tracking:** Track individual participants across the experiment with real-time identification and monitoring
- **Movement Heatmaps:** Visualize which camera angles were most visited and identify movement patterns
- **Interactive Timeline:** Synchronized video and audio playback with granular controls for exploring experiment moments
- **Emotion Detection:** Analyze emotional sentiment from both audio and visual cues throughout the experiment
- **Multi-Camera View:** Process and analyze synchronized video streams from multiple camera angles
- **Research-Friendly UI:** Designed for non-technical researchers with modern, intuitive interface

## Live Demo
The portfolio version is publicly hosted and requires no setup to explore:

Live Demo -> 
- Hosted on: [Render](http://render.com/)
- Database: [Supabase](http://supabase.com/) (PostgreSQL), pre-populated with sample experiment data

The first load may take a moment if the Render instance has spun down due to inactivity. This is expected on the free tier. Once loaded, you can navigate through the dashboard and explore the various features using the sample data.

## Portfolio vs. Original Version

| Feature | Original (BUas) | Portfolio Demo |
|---|---|---|
| Data source | MinIO object storage (BUas server) | Pre-loaded sample data |
| ETL pipeline | Automated 24h sync + manual trigger | Removed |
| Database | On-premise PostgreSQL | Supabase (hosted PostgreSQL) |
| Hosting | BUas internal server (campus/VPN only) | Render (publicly accessible) |

## Getting Started

Follow these instructions to get the project running on your local machine for development and testing purposes.

### Prerequisites

Make sure you have the following installed on your system:
- [**Python 3.7+**](https://python.org/downloads/)
- [**Git**](https://git-scm.com/downloads/)
- [**PostgreSQL**](https://www.postgresql.org/download/)(or a Supabase project)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ayumicho/tastelab-dashboard.git
   cd tastelab-dashboard
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv flask_env
   ```

3. **Activate the virtual environment**

   **On Windows:**
   ```bash
   flask_env\Scripts\activate
   ```

   **On macOS/Linux:**
   ```bash
   source flask_env/bin/activate
   ```

4. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

5. **Database Configuration**

   Update `SQLALCHEMY_DATABASE_URI` in `config.py` with your PostgreSQL or Supabase credentials:

   ```python
   # Local PostgreSQL
   postgresql://username:password@localhost:5432/tastelab

   # Supabase (replace with your project connection string)
   postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres
   ```

   Alternatively, set a `DATABASE_URL` environment variable to avoid changing the code directly.

6. **Run the application**
   ```bash
   python main.py
   ```

   The application should now be running at `http://127.0.0.1:5000/` locally.

## Project Structure

```
tastelab-dashboard/
├── docs/                                       # Technical documentation
│   └── README.md                               # Documentation guide
│   └── technical_report_dashboard.pdf          # Comprehensive technical report
│
├── static/                                     # CSS and images
│   ├── css/
│   │   ├── base.css                            # Global styles
│   │   ├── detection-tracking.css
│   │   ├── doc.css
│   │   ├── experiments.css
│   │   └── README.md                           # CSS documentation
│   │ 
│   └── images/
│       ├── 404.png                             # 404 error image
│       ├── 500.png                             # 500 error image 
│       ├── logo.png                            # BUas logo
│       └── README.md                           # Images documentation
│
├── sync/                                       # ETL pipeline for MinIO data
│   ├── __init__.py
│   ├── data_import.py                          # JSON parsing & DB insertion
│   ├── minio_service.py                        # MinIO interaction layer
│   ├── minio_sync.py                           # Orchestration & sync logic
│   └── README.md                               # ETL pipeline documentation
│
├── templates/                                  # HTML templates
│   ├── 404.html
│   ├── 500.html
│   ├── base.html
│   ├── home.html
│   ├── login.html
│   ├── logout.html
│   ├── profile.html
│   ├── signup.html
│   └── ...
│
├── auth.py                                     # Authentication module
├── config.py                                   # Configuration settings
├── db_names.py                                 # Database table names
├── docker-compose.yml                          # Docker Compose configuration
├── Dockerfile                                  # Dockerfile for containerization
├── main_docker.py                              # Docker entry point
├── main.py                                     # Main Flask application
├── minio_config.py                             # MinIO configuration
├── models.py                                   # Database models
├── reid_blueprint.py                           # People re-identification module
├── requirements.txt                            # Python dependencies
├── README.md                                   # Project documentation
└── view.py                                     # View functions

```
> **Note:** The `sync/` directory containing the ETL pipeline has been removed from this portfolio version, as it depended on the BUas MinIO server which is not accessible externally.

---

## Architecture & Code Organization

The application follows a modular Flask architecture:

- **`views.py`**: Handles application routing and logic. Defines Blueprints, manages URL endpoints (e.g. `/experiments`, `/profile`), and connects frontend templates to the backend.
- **`models.py`**: Defines the database schema using SQLAlchemy, representing data structures (Users, Experiments, NLP Analysis) as Python classes.
- **`db_names.py`**: A centralized configuration file for table and column name constants, ensuring consistency and safer schema refactoring.

> Detailed documentation for specific modules can be found in `README.md` files within their respective subdirectories.

---

## Dependencies

The project uses the following main packages:

- **Flask 3.1.2**
- **Jinja2 3.1.6**
- **Werkzeug 3.1.3**
- **Click 8.2.1**

For a complete list, see [`requirements.txt`](https://github.com/ayumicho/tastelab-dashboard/requirements.txt).

---

## Development

### Running in Development Mode

To run the application in development mode with debug enabled:

```bash
export FLASK_ENV=development  # On Windows use: set FLASK_ENV=development
python main.py
```

### Making Changes

1. Make your changes to the code
2. The development server will automatically reload when you save files
3. Refresh your browser to see the changes

---

## Troubleshooting

### Common Issues

**Issue: `python: command not found`**
- Make sure Python is installed and added to your system PATH
- Try using `python3` instead of `python`

**Issue: `pip: command not found`**
- Try using `python -m pip` instead of `pip`

**Issue: Permission denied errors**
- Make sure your virtual environment is activated
- On Linux/Mac, you may need to use `python3` and `pip3`

**Issue: Port already in use**
- The default port 5000 may be occupied
- Try running on a different port: `python main.py --port 5001`

**Issue: Database connection failed**
- Double-check your `SQLALCHEMY_DATABASE_URI` or `DATABASE_URL` environment variable
- Ensure your Supabase project is active and the connection string is correct

### Getting Help

If you encounter any issues:
1. Check that your virtual environment is activated
2. Ensure all dependencies are installed: `pip install -r requirements.txt`
3. Verify Python version: `python --version`
4. Check Flask installation: `flask --version`
5. Review error messages in the terminal for clues

---

## Docker Deployment

The application is containerized using Docker.

- **Entry Point:** `main_docker.py` is configured for the containerized environment (binds to `0.0.0.0` on port `3139`).
- **Running with Docker:**
  ```bash
  docker-compose up --build -d
  ```

---

## License

Distributed under the MIT License. See [LICENSE](https://github.com/ayumicho/tastelab-dashboard/tree/main/LICENSE) for more information.

---

**Last Updated:** February 2026

**Maintained by:** Ayumi Cho
