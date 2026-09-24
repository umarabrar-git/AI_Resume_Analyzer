# AI Resume Analyzer

AI Resume Analyzer is a Flask-based web application that helps users upload, review, and improve their resumes using AI-powered insights. It evaluates ATS compatibility, highlights skill gaps, and supports resume creation with a builder experience for job-ready output.

## Overview

The platform is designed for job seekers who want to:

- analyze the strength of their resume
- check ATS friendliness and keyword matching
- identify missing skills and content gaps
- build a polished resume tailored to a role
- export or continue improving versions over time

## Key Features

- Resume upload support for PDF and DOCX files
- ATS scoring and compatibility analysis
- Job matching and skill-gap recommendations
- AI-assisted resume improvement suggestions
- Resume creation and editing workflow
- Version tracking for saved resume variations
- Dashboard and reporting views
- User authentication and session support

## Tech Stack

- Python
- Flask
- Jinja2 templates
- SQLite database
- Bootstrap / custom frontend styling
- Flask-Session
- SQLAlchemy-based models

## Project Structure

```text
AI Resume Analyzer/
├── app.py                  # Flask application entry point
├── config.py               # application configuration
├── requirements.txt        # Python dependencies
├── database/              # database package and SQLite files
├── models/                # app models
├── routes/                # route blueprints and API endpoints
├── services/              # AI analysis and business logic
├── static/                # CSS, JS, and frontend assets
├── templates/             # HTML templates
├── tests/                 # test suite
├── uploads/               # uploaded resumes
├── reports/               # generated report data/output
├── README.md              # project documentation
├── .env                   # local environment config
├── e2e_test.py            # end-to-end checks
└── venv/                  # local virtual environment
```

## Prerequisites

Before running the project, make sure you have:

- Python 3.10+
- pip
- a local virtual environment tool
- access to a browser for testing the app locally

## Setup Instructions

### 1. Clone the repository

```bash
git clone <repository-url>
cd "AI Resume Analyzer"
```

### 2. Create a virtual environment

#### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000/
```

## Application Flow

1. Register or log in.
2. Upload your resume in PDF or DOCX format.
3. The analyzer checks ATS compatibility, keyword optimization, and content quality.
4. Review dashboard insights, recommendations, and role match scores.
5. Use the resume builder to improve and generate a refined version.
6. Export or save multiple resume variants.

## Main Routes

- `/` – home page
- `/auth/register` – registration
- `/auth/login` – login
- `/dashboard` – user dashboard
- `/resume-creation` – resume builder
- `/analysis` – structured resume analysis pages
- `/reports` – report and review screens
- `/upload` – resume upload flow

## Testing

Run the project test suite with:

```bash
pytest
```

For the resume creation checks specifically:

```bash
pytest tests/test_resume_creation_api.py -q
```

## Notes

- The project uses SQLite by default for local development.
- Uploaded resumes are stored in the `uploads/` directory.
- The project is built for local and development usage, and can be extended for production deployment with environment-based configuration and secure secrets.

## License

This project is provided as a local development project. Please review your organization’s licensing and deployment policies before production use.

## Contribution

Contributions are welcome. If you are improving features, fixing bugs, or adding new analysis workflows, please open a pull request with a clear summary of the change.
