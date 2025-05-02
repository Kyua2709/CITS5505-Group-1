# Social Media Sentiment Analysis Platform

A comprehensive web application that analyzes sentiment in social media comments to provide insights into public opinion on specific topics, products, or personalities.

## 📑 Overview

This project aims to create a platform where users can upload social media comment data, analyze sentiment trends, and selectively share their findings with others. The platform offers valuable insights for market research, brand management, and public opinion monitoring.

## ✨ Features

### Data Collection & Processing
- Multiple data input methods:
  - Manual entry of specific comments or post links
  - CSV/JSON file upload for batch processing
  - API keyword search functionality (if viable)
- Support for multiple social media platforms (Weibo, TikTok, Instagram, etc.)
- Data tagging and categorization (by topic, date, source, etc.)

### Sentiment Analysis
- AI-powered sentiment classification (positive, negative, neutral)
- Temporal sentiment trend analysis
- Keyword extraction and visualization
- Comment volume analysis
- Influence analysis (comment engagement, user impact, etc.)

### Data Visualization
- Interactive sentiment dashboards
- Sentiment distribution charts
- Temporal trend graphs
- Word clouds for sentiment-specific keywords
- Detailed comment listing with sentiment classification

### Sharing & Collaboration
- Selective sharing of specific analysis results
- User search functionality
- Customizable sharing permissions
- Sharing history management
- Report generation (PDF export)

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
- NLTK/TextBlob for sentiment analysis
- Optional: Integration with advanced NLP services

### Database Schema
- User table (user information, authentication)
- Project table (analysis project details)
- Dataset table (raw comment data)
- Analysis results table (processed sentiment data)
- Sharing permissions table (user sharing relationships)

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 14+
- pip (Python package manager)
- npm (Node.js package manager)

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/CITS5505-Group-1.git
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

4. Install frontend dependencies
```bash
npm install
```

5. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your settings
```

6. Initialize the database
```bash
flask db init
flask db migrate
flask db upgrade
```

7. Run the application
```bash
flask run
```

8. Access the application at http://localhost:5000

## 📊 Usage Examples

### Basic Sentiment Analysis
1. Upload a CSV file containing social media comments
2. Select the platform type and configure analysis parameters
3. View the sentiment distribution and trend analysis
4. Explore the detailed comment listing with sentiment classification

### Comparing Sentiment Between Topics
1. Create two separate analysis projects
2. Use the comparison feature to view differences in sentiment
3. Export comparison results as a PDF report

### Sharing Analysis Results
1. Select specific visualization panels to share
2. Set sharing permissions (view-only, allow download, etc.)
3. Share with specific users or generate a shareable link

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🙏 Acknowledgements

- [NLTK](https://www.nltk.org/) for natural language processing capabilities
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [Chart.js](https://www.chartjs.org/) for data visualization
- [Bootstrap](https://getbootstrap.com/) for responsive design
# Social Media Sentiment Analysis Platform

A comprehensive web application that analyzes sentiment in social media comments to provide insights into public opinion on specific topics, products, or personalities.

## 📑 Overview

This project aims to create a platform where users can upload social media comment data, analyze sentiment trends, and selectively share their findings with others. The platform offers valuable insights for market research, brand management, and public opinion monitoring.

## ✨ Features

### Data Collection & Processing
- Multiple data input methods:
  - Manual entry of specific comments or post links
  - CSV/JSON file upload for batch processing
  - API keyword search functionality (if viable)
- Support for multiple social media platforms (Weibo, TikTok, Instagram, etc.)
- Data tagging and categorization (by topic, date, source, etc.)

### Sentiment Analysis
- AI-powered sentiment classification (positive, negative, neutral)
- Temporal sentiment trend analysis
- Keyword extraction and visualization
- Comment volume analysis
- Influence analysis (comment engagement, user impact, etc.)

### Data Visualization
- Interactive sentiment dashboards
- Sentiment distribution charts
- Temporal trend graphs
- Word clouds for sentiment-specific keywords
- Detailed comment listing with sentiment classification

### Sharing & Collaboration
- Selective sharing of specific analysis results
- User search functionality
- Customizable sharing permissions
- Sharing history management
- Report generation (PDF export)

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
- NLTK/TextBlob for sentiment analysis
- Optional: Integration with advanced NLP services

### Database Schema
- User table (user information, authentication)
- Project table (analysis project details)
- Dataset table (raw comment data)
- Analysis results table (processed sentiment data)
- Sharing permissions table (user sharing relationships)

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 14+
- pip (Python package manager)
- npm (Node.js package manager)

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/CITS5505-Group-1.git
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

4. Install frontend dependencies
```bash
npm install
```

5. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your settings
```

6. Initialize the database
```bash
flask db init
flask db migrate
flask db upgrade
```

7. Run the application
```bash
flask run
```

8. Access the application at http://localhost:5000

## 📊 Usage Examples

### Basic Sentiment Analysis
1. Upload a CSV file containing social media comments
2. Select the platform type and configure analysis parameters
3. View the sentiment distribution and trend analysis
4. Explore the detailed comment listing with sentiment classification

### Comparing Sentiment Between Topics
1. Create two separate analysis projects
2. Use the comparison feature to view differences in sentiment
3. Export comparison results as a PDF report

### Sharing Analysis Results
1. Select specific visualization panels to share
2. Set sharing permissions (view-only, allow download, etc.)
3. Share with specific users or generate a shareable link

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🙏 Acknowledgements

- [NLTK](https://www.nltk.org/) for natural language processing capabilities
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [Chart.js](https://www.chartjs.org/) for data visualization
- [Bootstrap](https://getbootstrap.com/) for responsive design
# Social Media Sentiment Analysis Platform

A comprehensive web application that analyzes sentiment in social media comments to provide insights into public opinion on specific topics, products, or personalities.

## 📑 Overview

This project aims to create a platform where users can upload social media comment data, analyze sentiment trends, and selectively share their findings with others. The platform offers valuable insights for market research, brand management, and public opinion monitoring.

## ✨ Features

### Data Collection & Processing
- Multiple data input methods:
  - Manual entry of specific comments or post links
  - CSV/JSON file upload for batch processing
  - API keyword search functionality (if viable)
- Support for multiple social media platforms (Weibo, TikTok, Instagram, etc.)
- Data tagging and categorization (by topic, date, source, etc.)

### Sentiment Analysis
- AI-powered sentiment classification (positive, negative, neutral)
- Temporal sentiment trend analysis
- Keyword extraction and visualization
- Comment volume analysis
- Influence analysis (comment engagement, user impact, etc.)

### Data Visualization
- Interactive sentiment dashboards
- Sentiment distribution charts
- Temporal trend graphs
- Word clouds for sentiment-specific keywords
- Detailed comment listing with sentiment classification

### Sharing & Collaboration
- Selective sharing of specific analysis results
- User search functionality
- Customizable sharing permissions
- Sharing history management
- Report generation (PDF export)

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
- NLTK/TextBlob for sentiment analysis
- Optional: Integration with advanced NLP services

### Database Schema
- User table (user information, authentication)
- Project table (analysis project details)
- Dataset table (raw comment data)
- Analysis results table (processed sentiment data)
- Sharing permissions table (user sharing relationships)

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 14+
- pip (Python package manager)
- npm (Node.js package manager)

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/CITS5505-Group-1.git
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

4. Install frontend dependencies
```bash
npm install
```

5. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your settings
```

6. Initialize the database
```bash
flask db init
flask db migrate
flask db upgrade
```

7. Run the application
```bash
flask run
```

8. Access the application at http://localhost:5000

## 📊 Usage Examples

### Basic Sentiment Analysis
1. Upload a CSV file containing social media comments
2. Select the platform type and configure analysis parameters
3. View the sentiment distribution and trend analysis
4. Explore the detailed comment listing with sentiment classification

### Comparing Sentiment Between Topics
1. Create two separate analysis projects
2. Use the comparison feature to view differences in sentiment
3. Export comparison results as a PDF report

### Sharing Analysis Results
1. Select specific visualization panels to share
2. Set sharing permissions (view-only, allow download, etc.)
3. Share with specific users or generate a shareable link

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🙏 Acknowledgements

- [NLTK](https://www.nltk.org/) for natural language processing capabilities
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [Chart.js](https://www.chartjs.org/) for data visualization
- [Bootstrap](https://getbootstrap.com/) for responsive design
