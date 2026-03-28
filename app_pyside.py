import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTextEdit, QProgressBar, QFileDialog)
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QFont
from scraper_core import GitHubMarkdownScraper
from pathlib import Path

class ScraperThread(QThread):
    progress = Signal(str, int)
    finished = Signal(int)
    
    def __init__(self, repo_url, output_dir, branch='main'):
        super().__init__()
        self.repo_url = repo_url
        self.output_dir = output_dir
        self.branch = branch
        self.scraper = None
        
    def run(self):
        try:
            self.scraper = GitHubMarkdownScraper(self.repo_url, self.branch)
            count = self.scraper.scrape_all(self.output_dir, self.update_progress)
            self.finished.emit(count)
        except Exception as e:
            self.progress.emit(f"Error: {str(e)}", 0)
            self.finished.emit(-1)
    
    def update_progress(self, message, percent):
        self.progress.emit(message, percent)
    
    def stop(self):
        if self.scraper:
            self.scraper.stop()

class ModernScraperUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scraper_thread = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('GitHub Markdown Scraper')
        self.setGeometry(100, 100, 700, 500)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QLabel {
                color: #ffffff;
                font-size: 13px;
            }
            QLineEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #3d3d3d;
                border-radius: 5px;
                padding: 8px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #007acc;
            }
            QPushButton {
                background-color: #007acc;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
            QPushButton:disabled {
                background-color: #3d3d3d;
                color: #808080;
            }
            #stopButton {
                background-color: #d13438;
            }
            #stopButton:hover {
                background-color: #a82a2d;
            }
            #stopButton:pressed {
                background-color: #7f2022;
            }
            QTextEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #3d3d3d;
                border-radius: 5px;
                padding: 8px;
                font-family: Consolas, monospace;
                font-size: 12px;
            }
            QProgressBar {
                background-color: #2d2d2d;
                border: 2px solid #3d3d3d;
                border-radius: 5px;
                text-align: center;
                color: #ffffff;
            }
            QProgressBar::chunk {
                background-color: #007acc;
                border-radius: 3px;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel('GitHub Markdown Scraper')
        title.setFont(QFont('Segoe UI', 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Repository URL
        url_label = QLabel('Repository URL:')
        layout.addWidget(url_label)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText('https://github.com/username/repository')
        layout.addWidget(self.url_input)
        
        # Branch
        branch_layout = QHBoxLayout()
        branch_label = QLabel('Branch:')
        self.branch_input = QLineEdit()
        self.branch_input.setText('main')
        self.branch_input.setMaximumWidth(150)
        branch_layout.addWidget(branch_label)
        branch_layout.addWidget(self.branch_input)
        branch_layout.addStretch()
        layout.addLayout(branch_layout)
        
        # Output Directory
        output_layout = QHBoxLayout()
        output_label = QLabel('Output Folder:')
        self.output_input = QLineEdit()
        self.output_input.setText('scraped_files')
        self.browse_button = QPushButton('Browse')
        self.browse_button.setMaximumWidth(100)
        self.browse_button.clicked.connect(self.browse_folder)
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_input)
        output_layout.addWidget(self.browse_button)
        layout.addLayout(output_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton('Start Scraping')
        self.start_button.clicked.connect(self.start_scraping)
        
        self.stop_button = QPushButton('Stop')
        self.stop_button.setObjectName('stopButton')
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_scraping)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        layout.addLayout(button_layout)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Log Output
        log_label = QLabel('Log:')
        layout.addWidget(log_label)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)
        
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_input.setText(folder)
    
    def start_scraping(self):
        repo_url = self.url_input.text().strip()
        if not repo_url:
            self.log('Please enter a repository URL')
            return
        
        output_dir = self.output_input.text().strip()
        branch = self.branch_input.text().strip() or 'main'
        
        self.log(f'Starting scraper for: {repo_url}')
        self.log(f'Output directory: {output_dir}')
        
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setValue(0)
        
        self.scraper_thread = ScraperThread(repo_url, output_dir, branch)
        self.scraper_thread.progress.connect(self.update_progress)
        self.scraper_thread.finished.connect(self.scraping_finished)
        self.scraper_thread.start()
    
    def stop_scraping(self):
        if self.scraper_thread:
            self.log('Stopping scraper...')
            self.scraper_thread.stop()
            self.stop_button.setEnabled(False)
    
    def update_progress(self, message, percent):
        self.log(message)
        self.progress_bar.setValue(percent)
    
    def scraping_finished(self, count):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        if count >= 0:
            self.log(f'Scraping completed! Total files: {count}')
        self.scraper_thread = None
    
    def log(self, message):
        self.log_output.append(message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ModernScraperUI()
    window.show()
    sys.exit(app.exec())
