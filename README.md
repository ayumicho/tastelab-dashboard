# TasteLab Dashboard

A Flask-based research analytics platform that transforms unstructured experimental data into meaningful insights through intelligent visualizations and analysis. The dashboard helps researchers make sense of complex multimodal data by providing powerful tools for speech analysis and people tracking across synchronized video streams.

**Project Duration:** September 1, 2025 - January 23, 2026
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

## Network Requirements & Hosting
The TasteLab Dashboard is hosted on a private BUas internal server. Because it handles sensitive research data and heavy video streams, it is not accessible via the open internet.

- **On-Premise:** You must be physically on the BUas campus and connected to the Eduroam or local faculty network.
- **Remote (Working from Home):** 1. Connect via a VPN (e.g., FortiClient). 2. Ensure you have added BUas to the VPN routing; otherwise, the internal server IP will not resolve in your browser.

## Data Connectivity & ETL Pipeline
The dashboard relies on an automated ETL (Extract, Transform, Load) pipeline to fetch data from the MinIO storage server.

- **Automatic Sync:** The pipeline automatically refreshes every 24 hours.
- **Manual Sync:** If your experiment data is not showing up, click the "Sync Minio" button (or the 🔄 icon) in the dashboard. This will manually trigger the pipeline and retrieve your data in seconds.

## Getting Started

Follow these instructions to get the project running on your local machine for development and testing purposes.

### Prerequisites

Make sure you have the following installed on your system:
- [**Python 3.7+**](https://python.org/downloads/)
- [**Git**](https://git-scm.com/downloads/)
- [**PostgreSQL**](https://www.postgresql.org/download/)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/BredaUniversityADSAI/2025-26ab-fai3-specialisation-project-team-tastelab
   cd 2025-26ab-fai3-specialisation-project-team-tastelab
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

4. **Path to the project directory**
   ```bash
   cd dashboard
   ```

5. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```
6. **Database Configuration** 

Update ``SQLALCHEMY_DATABASE_URI`` in config.py with your local PostgreSQL credentials:

```bash
postgresql://username:password@localhost:5432/tastelab
```

7. **Run the application**
   ```bash
   python main.py
   ```

   The application should now be running at `http://127.0.0.1:5000/` on your local machine.

## Project Structure

```
/dashboard/
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

## Architecture & Code Organization

The application follows a modular Flask architecture:

* **`views.py`**: Handles the application routing and logic. It defines the Blueprints, manages URL endpoints (like `/experiments`, `/profile`), and connects the frontend templates to the backend data.
* **`models.py`**: Defines the database schema using SQLAlchemy. It represents the data structure (Users, Experiments, NLP Analysis) as Python classes.
* **`db_names.py`**: A centralized configuration file containing constant strings for table and column names. This ensures consistency across the application and makes refactoring database schema names safer and easier.
* **`sync/`**: Contains the ETL (Extract, Transform, Load) pipeline logic. This module is responsible for fetching raw JSON/video data from the MinIO storage server, transforming it, and loading it into the local PostgreSQL database.

> **Note:** Detailed documentation for specific modules can be found in `README.md` files located within their respective subdirectories (e.g., `/sync/README.md`).

## Dependencies

The project uses the following main packages:

- **Flask 3.1.2**
- **Jinja2 3.1.6**
- **Werkzeug 3.1.3**
- **Click 8.2.1**

For a complete list, see [`requirements.txt`](https://github.com/BredaUniversityADSAI/2025-26ab-fai3-specialisation-project-team-tastelab/requirements.txt).

## Development

### Running in Development Mode

To run the application in development mode with debug enabled:

```bash
export FLASK_ENV=development  # On Windows use: set FLASK_ENV=development
python main.py
```

### Database Configuration

By default, the application looks for a PostgreSQL database. To run the dashboard locally with full functionality:

1.  **Install PostgreSQL:** Download and install [PostgreSQL](https://www.postgresql.org/download/).
2.  **Create a Database:** Create a new local database (e.g., named `tastelab`).
3.  **Configure Connection:**
    * Open `config.py`.
    * Locate the `SQLALCHEMY_DATABASE_URI` variable.
    * Update the string to match your local credentials:
        ```python
        # format: postgresql://username:password@localhost:5432/database_name
        SQLALCHEMY_DATABASE_URI = os.getenv(
            'DATABASE_URL',
            'postgresql://postgres:your_password@localhost:5432/tastelab'
        )
        ```
    * Alternatively, you can set a `DATABASE_URL` environment variable to avoid changing the code.

### Making Changes

1. Make your changes to the code
2. The development server will automatically reload when you save files
3. Refresh your browser to see the changes

## Usage

1. Start the application using the installation steps above
2. Open your web browser and navigate to `http://127.0.0.1:5000/`
3. You should see the TasteLab dashboard interface


## Troubleshooting

### Common Issues

**Issue: `python: command not found`**
- Make sure Python is installed and added to your system PATH
- Try using `python3` instead of `python`

**Issue: `pip: command not found`**
- Make sure pip is installed with Python
- Try using `python -m pip` instead of `pip`

**Issue: Permission denied errors**
- Make sure you have activated your virtual environment
- On Linux/Mac, you might need to use `python3` and `pip3`

**Issue: Port already in use**
- The default port 5000 might be occupied
- Try running on a different port: `python main.py --port 5001`

### Getting Help

If you encounter any issues:
1. Check that your virtual environment is activated
2. Ensure all dependencies are installed: `pip install -r requirements.txt`
3. Verify Python version: `python --version`
4. Check Flask installation: `flask --version`
5. Review error messages in the terminal for clues

## Docker Deployment

The application is containerized using Docker and is hosted on a private BUas server.

* **Entry Point:** `main_docker.py` is configured specifically for the containerized environment (binds to `0.0.0.0` on port `3139`).
* **Running with Docker:**
    Ensure Docker is installed, then build and run using Docker Compose:
    ```bash
    docker-compose up --build -d
    ```

## License
Distributed under the MIT License. See [LICENSE](https://github.com/BredaUniversityADSAI/2025-26ab-fai3-specialisation-project-team-tastelab/tree/main/dashboard/LICENSE) for more information.
---

**Last Updated:** January 2026

**Maintained by:** Ayumi Chotoe
