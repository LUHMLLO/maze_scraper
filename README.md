# Maze Report Scraper

A Python-based tool to automatically discover and scrape content from Maze.co reports. It features a simple web interface to input a share URL, visualize real-time progress, and download the results as JSON or CSV.

## Features

- **Automatic Block Discovery**: Automatically navigates through the report to find all sub-pages (blocks).
- **Real-Time Progress**: View the scraping status in real-time via the web interface.
- **Data Export**: Download scraped data in JSON or CSV format.
- **Headless Browsing**: Uses Selenium with a headless Chrome browser for efficient scraping.

## Prerequisites

- Python 3.8+
- Google Chrome installed (for Selenium)

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/yourusername/maze-scraper.git
    cd maze-scraper
    ```

2.  Create a virtual environment (recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  Start the Flask application:
    ```bash
    python app.py
    ```

2.  Open your browser and navigate to:
    `http://127.0.0.1:5000`

3.  Enter a Maze Share URL (e.g., `https://app.maze.co/report/...`).

4.  Click **Start Scraping** and wait for the process to complete.

5.  Download your data!

## Disclaimer

This tool is for educational purposes only. Please respect the terms of service of the websites you scrape. The authors are not responsible for any misuse of this tool.

## License

[MIT](LICENSE)
