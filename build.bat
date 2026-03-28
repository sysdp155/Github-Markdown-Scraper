@echo off
echo Building GitHub Markdown Scraper...
pyinstaller --onefile --windowed --name "GitHubMarkdownScraper" --icon=NONE app.py
echo.
echo Build complete! Check the 'dist' folder for GitHubMarkdownScraper.exe
pause
