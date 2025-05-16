# Social Media Sentiment Analysis Platform

A comprehensive web application that analyzes sentiment in social media comments to provide insights into public opinion on specific topics, products, or personalities.

## 📑 Overview

This project aims to create a platform where users can upload social media comment data, analyze sentiment trends, and selectively share their findings with others. The platform offers valuable insights for market research, brand management, and public opinion monitoring.

## ✨ Features

### Data Collection & Processing

- **Flexible data input options**:

  - Manually enter specific comments
  - Upload text files for batch processing
  - Automatically fetch comments from post URLs

- **Cross-platform support**

  - Compatible with multiple social media platforms, including Reddit and YouTube
  - Planned expansion to additional platforms

- **AI-powered sentiment analysis**

  - Automatically classifies comments as positive, negative, or neutral
  - Provides sentiment scores for quantitative analysis

### Data Visualization

- **Interactive dashboards** to explore sentiment trends
- **Sentiment distribution charts** for visual breakdowns
- **Word clouds** highlighting keywords by sentiment
- **Detailed comment listings** with sentiment tags
- **Search functionality** to filter comments quickly
- **Report generation** with support for PDF export

### Sharing & Collaboration

- Share specific analysis results selectively
- Manage sharing history for better oversight
- Easily view reports that have been shared with you

## 🛠️ Tech Stack

### Frontend

- HTML/CSS for structure and styling
- Bootstrap for responsive design
- JavaScript for interactive elements
- Chart.js/D3.js for data visualization

### Backend

- Flask web framework
- SQLAlchemy ORM
- SQLite database (for development)
- BERT for sentiment analysis

### Database Schema

- `User` table (user information, authentication)
- `Upload` table (dataset metadata)
- `Comment` table (processed sentiment data)
- `Share` table (user sharing relationships)

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. Clone the repository

```bash
git clone https://github.com/Kyuan/CITS5505-Group-1.git
cd CITS5505-Group-1
```

2. Set up virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install backend dependencies

```bash
pip install -r requirements.txt
```

4. Run the application

```bash
flask run
```

5. Access the application at http://localhost:5000

### Testing

This project includes a comprehensive test suite.

- Run all **unit tests**:

```bash
py test.py ut
```

- Run all **system tests**:

```bash
py test.py st
```

## Contributors

| Name                | UWA Student ID | GitHub Username      |
| ------------------- | -------------- | -------------------- |
| Tianyu Li           | 23898365       | @543808706           |
| Kexing Yuan         | 24443823       | @Kyua2709            |
| Aashutosh Chapagain | 24661021       | @aashutosh-chapagain |
| Zhaodong Shen       | 24301655       | @Rockruff            |
