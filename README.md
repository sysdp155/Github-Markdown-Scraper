# GitHub Markdown Scraper

A modern desktop application to scrape .md files from GitHub repositories.

## Features

- Modern dark-themed UI
- Start/Stop controls for scraping
- Automatic discovery of all .md files in a repository
- Progress tracking with real-time logs
- Saves files with original folder structure
- Configurable output directory and branch

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Run the Application

```bash
python app.py
```

### Build .exe File

```bash
build.bat
```

Or manually:
```bash
pyinstaller --onefile --windowed --name "GitHubMarkdownScraper" app.py
```

The .exe file will be in the `dist` folder.

## How to Use

1. Enter the GitHub repository URL (e.g., `https://github.com/username/repo`)
2. Optionally change the branch (default: `main`)
3. Choose output folder (default: `scraped_files`)
4. Click **Start Scraping** to begin
5. Click **Stop** to cancel anytime
6. Files are automatically saved to the output folder

## Requirements

- Python 3.8+
- PyQt6
- requests
- pyinstaller (for building .exe)
