import requests
from pathlib import Path
import random
import time

class GitHubRandomScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/vnd.github.v3+json'
        })
        self.should_stop = False
        
    def stop(self):
        self.should_stop = True
    
    def search_users_by_country(self, country, max_users=50):
        """Search for GitHub users by country location."""
        users = []
        try:
            # Search users by location
            url = f"https://api.github.com/search/users?q=location:{country}&per_page={max_users}"
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            
            if 'items' in data:
                users = [user['login'] for user in data['items']]
                
        except Exception as e:
            raise Exception(f"Error searching users: {e}")
            
        return users
    
    def get_user_repos(self, username):
        """Get all repositories for a user."""
        repos = []
        try:
            url = f"https://api.github.com/users/{username}/repos?per_page=100"
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            
            for repo in data:
                repos.append({
                    'name': repo['name'],
                    'full_name': repo['full_name'],
                    'default_branch': repo['default_branch']
                })
                
        except Exception as e:
            print(f"Error getting repos for {username}: {e}")
            
        return repos
    
    def find_md_files_in_repo(self, owner, repo, branch='main', path=''):
        """Recursively find all .md files in a repository."""
        md_files = []
        try:
            url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
            response = self.session.get(url)
            
            if response.status_code == 404:
                return md_files
                
            response.raise_for_status()
            items = response.json()
            
            if isinstance(items, list):
                for item in items:
                    if self.should_stop:
                        break
                        
                    if item['type'] == 'file' and item['name'].endswith('.md'):
                        md_files.append(item['path'])
                    elif item['type'] == 'dir':
                        md_files.extend(self.find_md_files_in_repo(owner, repo, branch, item['path']))
                        
        except Exception as e:
            pass  # Skip errors for individual repos
            
        return md_files
    
    def download_file(self, owner, repo, branch, file_path):
        """Download a single file from GitHub."""
        try:
            url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_path}"
            response = self.session.get(url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            return None
    
    def save_file(self, content, output_path):
        """Save content to a file."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def scrape_random_users(self, country, output_dir='scraped_files', max_users=10, progress_callback=None):
        """Scrape markdown files from random users in a country."""
        self.should_stop = False
        total_files = 0
        
        if progress_callback:
            progress_callback(f"Searching for users in {country}...", 0)
        
        # Search for users
        users = self.search_users_by_country(country, max_users * 3)
        
        if not users:
            if progress_callback:
                progress_callback(f"No users found in {country}", 100)
            return 0
        
        # Randomly select users
        selected_users = random.sample(users, min(max_users, len(users)))
        
        if progress_callback:
            progress_callback(f"Found {len(selected_users)} users. Starting to scrape...", 5)
        
        for idx, username in enumerate(selected_users, 1):
            if self.should_stop:
                if progress_callback:
                    progress_callback(f"Stopped. Scraped {total_files} files.", int((idx/len(selected_users))*100))
                break
            
            if progress_callback:
                progress_callback(f"[{idx}/{len(selected_users)}] Checking user: {username}", int((idx/len(selected_users))*100))
            
            # Get user's repositories
            repos = self.get_user_repos(username)
            
            if not repos:
                continue
            
            # Process each repository
            for repo in repos:
                if self.should_stop:
                    break
                
                repo_name = repo['name']
                full_name = repo['full_name']
                branch = repo['default_branch'] or 'main'
                
                if progress_callback:
                    progress_callback(f"  Scanning repo: {full_name}", int((idx/len(selected_users))*100))
                
                # Find all .md files
                owner = username
                md_files = self.find_md_files_in_repo(owner, repo_name, branch)
                
                if not md_files:
                    continue
                
                # Download each .md file
                for file_path in md_files:
                    if self.should_stop:
                        break
                    
                    if progress_callback:
                        progress_callback(f"    Downloading: {file_path}", int((idx/len(selected_users))*100))
                    
                    content = self.download_file(owner, repo_name, branch, file_path)
                    
                    if content:
                        output_path = Path(output_dir) / username / repo_name / file_path
                        self.save_file(content, output_path)
                        total_files += 1
                
                # Small delay to avoid rate limiting
                time.sleep(0.5)
        
        if progress_callback and not self.should_stop:
            progress_callback(f"Complete! Scraped {total_files} markdown files from {len(selected_users)} users.", 100)
        
        return total_files
