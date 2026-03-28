import requests
import re
from urllib.parse import urljoin, urlparse
from pathlib import Path

class GitHubMarkdownScraper:
    def __init__(self, repo_url):
        """
        Initialize scraper with a GitHub repository URL.
        Example: https://github.com/username/repo
        """
        self.repo_url = repo_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def get_raw_url(self, file_path):
        """Convert GitHub file URL to raw content URL."""
        parts = self.repo_url.replace('https://github.com/', '').split('/')
        owner, repo = parts[0], parts[1]
        return f"https://raw.githubusercontent.com/{owner}/{repo}/main/{file_path}"
    
    def scrape_file(self, file_path):
        """Scrape a single markdown file."""
        raw_url = self.get_raw_url(file_path)
        try:
            response = self.session.get(raw_url)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error scraping {file_path}: {e}")
            return None
    
    def save_file(self, content, output_path):
        """Save scraped content to a file."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Saved: {output_path}")

    def scrape_multiple(self, file_paths, output_dir='output'):
        """Scrape multiple markdown files."""
        for file_path in file_paths:
            content = self.scrape_file(file_path)
            if content:
                output_path = Path(output_dir) / file_path
                self.save_file(content, output_path)


if __name__ == "__main__":
    # Example usage
    scraper = GitHubMarkdownScraper("https://github.com/username/repo")
    
    # Scrape single file
    content = scraper.scrape_file("README.md")
    if content:
        scraper.save_file(content, "output/README.md")
    
    # Scrape multiple files
    files = ["README.md", "docs/guide.md", "CONTRIBUTING.md"]
    scraper.scrape_multiple(files)
