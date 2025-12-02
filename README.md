# TasteLab Dashboard

A Flask-based web application for automating sensory data processing and visualization at Breda University's TasteLab facility. This dashboard leverages Vision Language Models (VLMs) to streamline the collection, analysis, and presentation of sensory evaluation data.

**Project Duration:** September 1, 2025 - January 23, 2026

## Overview

The TasteLab Dashboard is an AI-powered toolkit designed to transform how sensory data is processed and analyzed at the TasteLab facility. The system automates the traditionally manual process of sensory evaluation, providing researchers with real-time insights and comprehensive data visualization capabilities.

### Key Features

- **Automated Data Processing**: VLM-powered analysis of sensory evaluation data
- **Emotion Analysis**: Advanced emotion detection and classification from participant responses
- **Experiment Management**: Create, track, and manage sensory evaluation experiments
- **User Authentication**: Secure login and role-based access control
- **Real-time Visualization**: Interactive dashboards displaying experiment results
- **Data Integration**: Seamless connection between MinIO object storage and PostgreSQL database
- **Responsive Interface**: Modern, user-friendly web interface accessible across devices

## Tech Stack

- **Backend**: Flask 3.1.2
- **Database**: PostgreSQL
- **Object Storage**: MinIO
- **Template Engine**: Jinja2 3.1.6
- **Authentication**: Flask-Login with Werkzeug password hashing
- **Frontend**: HTML5, CSS3, JavaScript

## Getting Started

### Prerequisites

Ensure you have the following installed:

- **Python 3.7+** - [Download Python](https://python.org/downloads/)
- **Git** - [Download Git](https://git-scm.com/downloads/)
- **PostgreSQL** - [Download PostgreSQL](https://www.postgresql.org/download/)
- **MinIO** - [Download MinIO](https://min.io/download) (for object storage)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ayumicho/tastelab-dashboard.git
   cd ayumicho/tastelab-dashboard
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv flask_env
   ```

3. **Activate the virtual environment**
   
   On Windows:
   ```bash
   flask_env\Scripts\activate
   ```
   
   On macOS/Linux:
   ```bash
   source flask_env/bin/activate
   ```

4. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure credentials**
   
   Update the `config.py` file with your database and MinIO credentials. This file is included in `.gitignore` to keep credentials secure.

6. **Initialize the database**
   ```bash
   python
   >>> from main import db
   >>> db.create_all()
   >>> exit()
   ```

7. **Run the application**
   ```bash
   python main.py
   ```
   
   The application will be available at `http://127.0.0.1:5000/`

## Project Structure

```
tastelab-dashboard/
├── templates/                     # HTML templates
│   ├── 404.html                   # Error page
│   ├── 500.html                   # Server error page
│   ├── add-experiment.html        # Add experiment page
│   ├── base.html                  # Base template
│   ├── cv.html                    # Showcases data from CV model
│   ├── experiments.html           # Shows list of experiments
│   ├── help.html                  # Help page
│   ├── home.html                  # Dashboard home
│   ├── login.html                 # Login page
│   ├── logout.html                # Logout confirmation
│   ├── privacy-policy.html        # Privacy Policy page
│   ├── profile.html               # User profile
│   ├── signup.html                # Registration page
│   ├── single-experiment.html     # Shows details of a single experiment
│   ├── terms-of-service.html      # Terms of Service page
│   └── nlp.html                   # Showcases data from NLP model
├── static/                        # Static assets
│   ├── css/                       # Stylesheets
│   ├── js/                        # JavaScript files
│   └── images/                    # Image assets
├── auth.py                        # Authentication logic
├── config.py                      # Stores credentials
├── main.py                        # Application entry point
├── models.py                      # Database models
├── view.py                        # Route handlers
├── requirements.txt               # Python dependencies
└── README.md                      # Project documentation
```

## Usage

1. **Create an Account**: Navigate to the signup page and register
2. **Log In**: Access the dashboard with your credentials
3. **Create Experiments**: Set up new sensory evaluation experiments
4. **Upload Data**: Upload participant response data for analysis
5. **View Results**: Access real-time analytics and emotion analysis results

For assistance with dashboard features and functionality, visit the built-in Help page accessible from the navigation menu.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Dashboard home |
| `/login` | GET, POST | User authentication |
| `/signup` | GET, POST | User registration |
| `/logout` | GET | Log out current user |
| `/profile` | GET | User profile page |
| `/experiments` | GET | List all experiments |
| `/experiments/create` | POST | Create new experiment |
| `/experiments/<id>` | GET | View experiment details |

## License

This project is developed for educational purposes as part of the Data Science and AI specialization at Breda University of Applied Sciences. All rights reserved.

---

**Last Updated:** December 2025
**Version:** 1.0.0
