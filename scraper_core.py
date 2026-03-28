import requests
from pathlib import Path

class GitHubMarkdownScraper:
    def __init__(self, repo_url, branch='main'):
        self.repo_url = repo_url.rstrip('/')
        self.branch = branch
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.should_stop = False
        
    def stop(self):
        self.should_stop = True
        
    def get_api_url(self, path=''):
        parts = self.repo_url.replace('https://github.com/', '').split('/')
        owner, repo = parts[0], parts[1]
        return f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    
    def get_raw_url(self, file_path):
        parts = self.repo_url.replace('https://github.com/', '').split('/')
        owner, repo = parts[0], parts[1]
        return f"https://raw.githubusercontent.com/{owner}/{repo}/{self.branch}/{file_path}"
    
    def find_all_md_files(self, path=''):
        md_files = []
        try:
            response = self.session.get(self.get_api_url(path))
            response.raise_for_status()
            items = response.json()
            
            for item in items:
                if self.should_stop:
                    break
                    
                if item['type'] == 'file' and item['name'].endswith('.md'):
                    md_files.append(item['path'])
                elif item['type'] == 'dir':
                    md_files.extend(self.find_all_md_files(item['path']))
                    
        except Exception as e:
            raise Exception(f"Error finding files: {e}")
            
        return md_files
    
    def scrape_file(self, file_path):
        raw_url = self.get_raw_url(file_path)
        response = self.session.get(raw_url)
        response.raise_for_status()
        return response.text
    
    def save_file(self, content, output_path):
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def scrape_all(self, output_dir='scraped_files', progress_callback=None):
        self.should_stop = False
        
        if progress_callback:
            progress_callback("Finding markdown files...", 0)
        
        md_files = self.find_all_md_files()
        
        if not md_files:
            if progress_callback:
                progress_callback("No markdown files found.", 100)
            return 0
        
        total = len(md_files)
        scraped = 0
        
        for i, file_path in enumerate(md_files, 1):
            if self.should_stop:
                if progress_callback:
                    progress_callback(f"Stopped. Scraped {scraped}/{total} files.", int((scraped/total)*100))
                break
                
            if progress_callback:
                progress_callback(f"Scraping {i}/{total}: {file_path}", int((i/total)*100))
            
            try:
                content = self.scrape_file(file_path)
                output_path = Path(output_dir) / file_path
                self.save_file(content, output_path)
                scraped += 1
            except Exception as e:
                if progress_callback:
                    progress_callback(f"Error with {file_path}: {e}", int((i/total)*100))
        
        if progress_callback and not self.should_stop:
            progress_callback(f"Complete! Scraped {scraped}/{total} files.", 100)
        
        return scraped
